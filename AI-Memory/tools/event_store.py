#!/usr/bin/env python3
"""Kho sự kiện AI dùng chung, append-only; chỉ ghi dữ liệu thực sự quan sát được.

Không đọc các hội thoại của ChatGPT/Codex nếu môi trường không cung cấp chúng.
Không truy cập private reasoning, credentials hoặc dữ liệu ẩn của nền tảng.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import mimetypes
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

CONFIG_FILE = Path(__file__).resolve().parents[1] / "project.json"
PROJECT_ID = json.loads(CONFIG_FILE.read_text(encoding="utf-8")).get("project_id") or "__TEMPLATE_UNINITIALIZED__"
TZ = ZoneInfo("Asia/Ho_Chi_Minh")
EMPTY_HASH = "0" * 64
MAX_REGULAR_GIT_OBJECT = 90 * 1024 * 1024
BLOB_CHUNK_SIZE = 8 * 1024 * 1024
SEGMENT_TARGET = 8 * 1024 * 1024
EVENT_TYPE = re.compile(r"^[a-z][a-z0-9_.-]*$")
SESSION_ID = re.compile(r"^[0-9]{8}T[0-9]{6}-[0-9a-f]{8}$")


def canonical_json(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save_json_atomic(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    try:
        temporary.write_bytes(json.dumps(value, ensure_ascii=False, indent=2).encode("utf-8") + b"\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return value


def current_time() -> datetime:
    return datetime.now(TZ)


def create_session(root: Path, platform: str, title: str, author: str = "unspecified",
                   source_conversation_id: str | None = None,
                   capture_method: str = "manual",
                   capture_status: str = "partial") -> Path:
    if capture_status not in ("partial", "complete", "unknown"):
        raise ValueError("capture_status must be partial, complete or unknown")
    now = current_time()
    ident = now.strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:8]
    path = root / "conversations" / now.strftime("%Y/%m/%d") / ident
    path.mkdir(parents=True, exist_ok=False)
    manifest = {
        "schema_version": "2.0",
        "project_id": PROJECT_ID,
        "session_id": ident,
        "title": title,
        "platform": platform,
        "author": author,
        "source_conversation_id": source_conversation_id,
        "capture_method": capture_method,
        "capture_status": capture_status,
        "capture_gaps": [],
        "created_at": now.isoformat(timespec="microseconds"),
        "event_count": 0,
        "last_event_hash": EMPTY_HASH,
        "attachments": [],
        "segment_count": 0,
        "notes": "Trạng thái complete chỉ có nghĩa đầy đủ đối với phạm vi dữ liệu bộ ghi quan sát được."
    }
    save_json_atomic(path / "session.json", manifest)
    (path / "events.jsonl").touch(exist_ok=False)
    return path


@contextlib.contextmanager
def session_lock(path: Path):
    """Khóa file Unix/macOS/Linux; thiếu khả năng khóa thì từ chối ghi để tránh mất sự kiện."""
    try:
        import fcntl
    except ImportError as exc:
        raise RuntimeError("Recorder cần khóa ghi; môi trường này chưa hỗ trợ fcntl") from exc
    lock_path = path / ".writer.lock"
    with lock_path.open("a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def append_event(path: Path, kind: str, actor: str, payload: object,
                 occurred_at: str | None = None, turn_id: str | None = None,
                 parent_event_id: str | None = None, tool_call_id: str | None = None,
                 source_event_id: str | None = None,
                 capture_status: str = "captured") -> dict:
    if not EVENT_TYPE.fullmatch(kind):
        raise ValueError("Event kind không hợp lệ")
    if capture_status not in ("captured", "partial", "missing"):
        raise ValueError("capture_status không hợp lệ")
    if occurred_at is not None:
        source = datetime.fromisoformat(occurred_at.replace("Z", "+00:00"))
        if source.tzinfo is None or source.utcoffset() is None:
            raise ValueError("occurred_at phải có múi giờ")
    with session_lock(path):
        manifest = load_json(path / "session.json")
        now = current_time()
        event = {
            "schema_version": "2.0",
            "event_id": uuid.uuid4().hex,
            "session_id": manifest["session_id"],
            "sequence": manifest["event_count"] + 1,
            "kind": kind,
            "actor": actor,
            "time": {
                "recorded_at": now.isoformat(timespec="microseconds"),
                "recorded_at_utc": now.astimezone(timezone.utc).isoformat(timespec="microseconds"),
                "occurred_at": occurred_at
            },
            "links": {
                "turn_id": turn_id,
                "parent_event_id": parent_event_id,
                "tool_call_id": tool_call_id,
                "source_event_id": source_event_id
            },
            "capture_status": capture_status,
            "payload": payload,
            "previous_hash": manifest["last_event_hash"]
        }
        event["hash"] = sha256(canonical_json(event))
        encoded = json.dumps(event, ensure_ascii=False, separators=(",", ":")).encode("utf-8") + b"\n"
        events_file = path / "events.jsonl"
        if events_file.stat().st_size and events_file.stat().st_size + len(encoded) > SEGMENT_TARGET:
            directory = path / "segments"
            directory.mkdir(exist_ok=True)
            next_segment = manifest.get("segment_count", 0) + 1
            os.replace(events_file, directory / f"{next_segment:06d}.jsonl")
            events_file.touch(exist_ok=False)
            manifest["segment_count"] = next_segment
        with events_file.open("ab") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        manifest["event_count"] = event["sequence"]
        manifest["last_event_hash"] = event["hash"]
        if capture_status != "captured":
            manifest["capture_status"] = "partial"
        save_json_atomic(path / "session.json", manifest)
        return event


def _save_object(root: Path, data: bytes) -> dict:
    fingerprint = sha256(data)
    target = root / "objects" / "sha256" / fingerprint[:2] / fingerprint
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        if sha256(target.read_bytes()) != fingerprint:
            raise ValueError("Checksum của object có sẵn bị sai")
    else:
        try:
            with target.open("xb") as handle:
                handle.write(data)
        except FileExistsError:
            if sha256(target.read_bytes()) != fingerprint:
                raise ValueError("Có ghi đồng thời không hợp lệ vào kho object")
    return {
        "sha256": fingerprint, "size": len(data),
        "object_path": target.relative_to(root).as_posix()
    }


def attach_file(root: Path, session: Path, filepath: Path,
                label: str | None = None, media_type: str | None = None,
                turn_id: str | None = None) -> dict:
    """Tự chia các tệp lớn thành khối <=8 MiB; không giới hạn tổng theo kích thước file Git."""
    if not filepath.is_file():
        raise FileNotFoundError(filepath)
    full_hash = hashlib.sha256()
    fragments = []
    total_bytes = 0
    with filepath.open("rb") as stream:
        while True:
            chunk = stream.read(BLOB_CHUNK_SIZE)
            if not chunk:
                break
            total_bytes += len(chunk)
            full_hash.update(chunk)
            fragments.append(_save_object(root, chunk))
    if not fragments:
        fragments.append(_save_object(root, b""))
    original_hash = full_hash.hexdigest()
    obj = {
        "sha256": original_hash, "size": total_bytes,
        "filename": label or filepath.name,
        "media_type": media_type or mimetypes.guess_type(filepath.name)[0] or "application/octet-stream"
    }
    if len(fragments) == 1:
        obj["object_path"] = fragments[0]["object_path"]
    else:
        obj["storage"] = "chunked-sha256-v1"
        obj["chunks"] = fragments
    with session_lock(session):
        manifest = load_json(session / "session.json")
        if not any(a.get("sha256") == original_hash for a in manifest["attachments"]):
            manifest["attachments"].append(obj)
            save_json_atomic(session / "session.json", manifest)
    append_event(session, kind="attachment.imported", actor="recorder", payload=obj, turn_id=turn_id)
    return obj


def read_events(session: Path):
    """Đọc các phân đoạn theo thứ tự, giữ nguyên chuỗi hash xuyên nhiều tệp."""
    segments = sorted((session / "segments").glob("*.jsonl"))
    for filename in [*segments, session / "events.jsonl"]:
        if not filename.is_file():
            raise ValueError(f"Thiếu segment: {filename}")
        with filename.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"JSONL không hợp lệ: {filename}:{number}") from exc
                if not isinstance(event, dict):
                    raise ValueError(f"Event không phải object: {filename}:{number}")
                yield event


def verify_session(root: Path, session: Path) -> list[str]:
    errors = []
    try:
        manifest = load_json(session / "session.json")
        seen_ids = set()
        count, previous = 0, EMPTY_HASH
        for event in read_events(session):
            count += 1
            fingerprint = event.get("hash")
            content = {key: value for key, value in event.items() if key != "hash"}
            if event.get("sequence") != count:
                errors.append(f"sequence sai ở event {count}")
            if event.get("session_id") != manifest.get("session_id"):
                errors.append(f"session_id sai ở event {count}")
            if event.get("previous_hash") != previous:
                errors.append(f"hash chain đứt ở event {count}")
            if fingerprint != sha256(canonical_json(content)):
                errors.append(f"checksum không đúng ở event {count}")
            if event.get("event_id") in seen_ids:
                errors.append(f"event_id trùng ở event {count}")
            seen_ids.add(event.get("event_id"))
            previous = fingerprint
        if count != manifest.get("event_count"):
            errors.append("Số event khác session.json")
        if previous != manifest.get("last_event_hash"):
            errors.append("last_event_hash khác session.json")
        segments = sorted((session / "segments").glob("*.jsonl"))
        if len(segments) != manifest.get("segment_count", 0):
            errors.append("Số đoạn sự kiện khác session.json")
        for item in manifest.get("attachments", []):
            fragments = item.get("chunks")
            if fragments is None:
                fragments = [item]
            full_hash = hashlib.sha256()
            observed_size = 0
            for fragment in fragments:
                objpath = root / fragment["object_path"]
                if not objpath.is_file():
                    errors.append(f"Thiếu object: {fragment['object_path']}")
                    continue
                raw = objpath.read_bytes()
                if sha256(raw) != fragment["sha256"]:
                    errors.append(f"Checksum object sai: {fragment['object_path']}")
                if len(raw) != fragment["size"]:
                    errors.append(f"Kích thước object sai: {fragment['object_path']}")
                observed_size += len(raw)
                full_hash.update(raw)
            if observed_size != item["size"] or full_hash.hexdigest() != item["sha256"]:
                errors.append(f"File đính kèm hỏng hoặc thiếu: {item.get('filename')}")
    except (OSError, KeyError, ValueError, TypeError) as exc:
        errors.append(str(exc))
    return errors


def build_index(root: Path) -> dict:
    sessions = []
    for path in sorted((root / "conversations").glob("*/*/*/*/session.json")):
        record = load_json(path)
        sessions.append({
            "session_id": record["session_id"],
            "session_path": path.parent.relative_to(root).as_posix(),
            "platform": record["platform"],
            "title": record["title"],
            "created_at": record["created_at"],
            "event_count": record["event_count"],
            "last_event_hash": record["last_event_hash"],
            "capture_status": record["capture_status"],
            "capture_gaps": record.get("capture_gaps", [])
        })
    return {"schema_version": "2.0", "project_id": PROJECT_ID, "session_count": len(sessions), "sessions": sessions}
