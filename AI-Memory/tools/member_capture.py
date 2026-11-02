#!/usr/bin/env python3
"""Bộ ghi sự kiện từ host tin cậy, mỗi tin nhắn một commit, tách theo thành viên.

Không tự thu thập sự kiện ChatGPT. Host phải cung cấp sự kiện có thật, token,
Git checkout nhánh bộ nhớ, Git remote có quyền push và callback sau assistant final.
"""
from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import hmac
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

from event_store import append_event, attach_file, build_index, create_session, load_json, save_json_atomic, verify_session

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-z][a-z0-9-]{1,63}$")
EVENTS = {"message.created", "message.completed", "message.edited", "message.prepared",
          "tool.call", "tool.result", "tool.error", "file.read", "file.write",
          "ui.rendered", "attachment.imported", "capture.gap"}
MAX_MESSAGE = 2 * 1024 * 1024
MAX_ATTACHMENT = 8 * 1024 * 1024


def git(*args, check=True):
    p = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if check and p.returncode:
        raise RuntimeError(f"Git lỗi ({' '.join(args[:2])}): {p.stderr.strip()[:300]}")
    return p.stdout.strip()


def safe_config():
    cfg = load_json(ROOT / "project.json")
    if cfg.get("initialized") is False or not cfg.get("project_id"):
        raise RuntimeError("Kho bộ nhớ template chưa được khởi tạo dự án")
    branch = cfg.get("memory_branch")
    if git("branch", "--show-current") != branch:
        raise RuntimeError("TỪ CHỐI: chỉ được ghi khi đang ở nhánh bộ nhớ")
    if git("diff", "--cached", "--name-only"):
        raise RuntimeError("TỪ CHỐI: index Git đang có file staged ngoài giao dịch")
    return cfg


def registry():
    # Danh sách thành viên là nguồn chuẩn trên ai-context, không sao chép vào memory.
    data = json.loads(git("show", "ai-context:TEAM/MEMBERS.json"))
    if not data.get("initialized"):
        raise RuntimeError("Danh sách thành viên/owner chưa được chủ dự án cấu hình")
    return data


def authenticate(token, roster):
    if not token or len(token) < 32:
        raise PermissionError("Chưa có token host đủ mạnh")
    raw = os.environ.get("AI_CAPTURE_KEYS_JSON", "")
    if not raw:
        raise PermissionError("Thiếu cấu hình AI_CAPTURE_KEYS_JSON ở host")
    credentials = json.loads(raw)
    digest = hashlib.sha256(token.encode()).hexdigest()
    principal = None
    for expected, value in credentials.items():
        if hmac.compare_digest(digest, expected):
            principal = value
    if principal is None or not isinstance(principal, dict):
        raise PermissionError("Token host không hợp lệ")
    member_id = principal.get("member_id")
    if not isinstance(member_id, str) or not ID.fullmatch(member_id):
        raise PermissionError("member_id không hợp lệ")
    members = {m["member_id"]: m for m in roster.get("members", [])}
    member = members.get(member_id)
    if member is None or member.get("status") != "active":
        raise PermissionError("Thành viên chưa được chủ dự án kích hoạt")
    if member.get("role") not in ("owner", "member"):
        raise PermissionError("Vai trò không hợp lệ")
    if member.get("role") == "owner" and roster.get("owner_member_id") != member_id:
        raise PermissionError("Owner không khớp danh sách chính thức")
    if principal.get("role") != member.get("role"):
        raise PermissionError("Token và vai trò chính thức không khớp")
    return member_id, member["role"]


@contextmanager
def exclusive_git_lock():
    # Một checkout chỉ tạo một commit tại một thời điểm.
    lockfile = Path(git("rev-parse", "--git-path", "member-capture.lock"))
    if not lockfile.is_absolute():
        lockfile = ROOT.parent / lockfile
    lockfile.parent.mkdir(parents=True, exist_ok=True)
    with lockfile.open("a+b") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)


def verify_remote(sha, branch):
    remote = git("ls-remote", "origin", f"refs/heads/{branch}")
    actual = remote.split()[0] if remote else None
    if actual != sha:
        raise RuntimeError("CHƯA ĐỒNG BỘ: remote SHA không khớp commit vừa tạo")
    return actual


def ingest(payload, token, dry_run=False):
    if len(json.dumps(payload, ensure_ascii=False).encode()) > MAX_MESSAGE + MAX_ATTACHMENT * 4:
        raise ValueError("Payload vượt ngưỡng cho phép")
    with exclusive_git_lock():
        cfg = safe_config()
        member_id, role = authenticate(token, registry())
        kind = payload.get("kind")
        if kind not in EVENTS:
            raise ValueError("Loại sự kiện không được hỗ trợ")
        message_id = payload.get("message_id")
        conversation_id = payload.get("conversation_id")
        if not isinstance(message_id, str) or not 1 <= len(message_id) <= 200:
            raise ValueError("Host phải cấp message_id ổn định")
        if not isinstance(conversation_id, str) or not 1 <= len(conversation_id) <= 200:
            raise ValueError("Host phải cấp conversation_id ổn định")
        if kind == "message.completed" and payload.get("published") is not True:
            raise ValueError("Không được gọi completed khi host chưa xác nhận final đã phát hành")
        if kind.startswith("message.") and not isinstance(payload.get("text"), str):
            raise ValueError("Thông điệp cần text nguyên gốc")
        if kind == "message.created" and payload.get("actor") != "user":
            raise ValueError("message.created phải đến từ user")
        if kind in ("message.completed", "message.prepared") and payload.get("actor") != "assistant":
            raise ValueError("Sai vai trò phản hồi")
        if payload.get("actor") not in ("user", "assistant", "tool", "recorder"):
            raise ValueError("actor không hợp lệ")
        if len(payload.get("text", "").encode()) > MAX_MESSAGE:
            raise ValueError("Tin nhắn vượt giới hạn 2 MiB")
        if payload.get("member_id") and payload["member_id"] != member_id:
            raise PermissionError("Host không được ghi vào hồ sơ thành viên khác")
        key = hashlib.sha256(json.dumps([member_id, conversation_id, message_id, kind],
                                        ensure_ascii=False).encode()).hexdigest()
        member_root = ROOT / "members" / member_id
        index_path = member_root / "indexes" / "capture.json"
        index = load_json(index_path) if index_path.exists() else {"sessions": {}, "dedup": {}}
        if key in index["dedup"]:
            # Gửi lại commit đang có nếu lần trước đã tạo nhưng push thất bại.
            sha = git("rev-parse", "HEAD")
            if not dry_run:
                git("push", "origin", f"HEAD:refs/heads/{cfg['memory_branch']}")
                verify_remote(sha, cfg["memory_branch"])
            return {"status": "duplicate", "member_id": member_id,
                    "commit_sha": sha if not dry_run else None}
        if dry_run:
            return {"status": "validated", "member_id": member_id, "role": role}
        if conversation_id in index["sessions"]:
            session = ROOT / index["sessions"][conversation_id]
            if not (session / "session.json").is_file():
                raise RuntimeError("Chỉ mục phiên trỏ tới dữ liệu không tồn tại")
        else:
            session = create_session(member_root, "host", payload.get("title", "Hội thoại"),
                                     author=member_id, source_conversation_id=conversation_id,
                                     capture_method="trusted-host", capture_status="partial")
            index["sessions"][conversation_id] = session.relative_to(ROOT).as_posix()
            meta = load_json(session / "session.json")
            meta["member_id"] = member_id
            meta["member_role_at_capture"] = role
            save_json_atomic(session / "session.json", meta)
        # Kiểm dữ liệu tệp trước khi ghi để tránh commit trạng thái nửa chừng.
        validated_attachments = []
        attachments = payload.get("attachments", [])
        if not isinstance(attachments, list) or len(attachments) > 16:
            raise ValueError("Danh sách attachment không hợp lệ")
        for item in attachments:
            if not isinstance(item, dict):
                raise ValueError("Định dạng attachment sai")
            filename = item.get("name", "attachment.bin")
            if not isinstance(filename, str) or not 1 <= len(filename) <= 200 or "\x00" in filename:
                raise ValueError("Tên tệp không hợp lệ")
            data = base64.b64decode(item["base64"], validate=True)
            if len(data) > MAX_ATTACHMENT:
                raise ValueError("Attachment vượt 8 MiB")
            validated_attachments.append((filename, data))
        raw = {"format": payload.get("format", "text"), "text": payload.get("text", ""),
               "source": "trusted-host", "source_message_id": message_id,
               "member_id": member_id, "member_role_at_capture": role,
               "published": payload.get("published", False)}
        if kind.startswith("tool.") or kind.startswith("ui.") or kind == "capture.gap":
            raw["data"] = payload.get("data")
        event = append_event(session, kind, payload["actor"], raw,
                             occurred_at=payload.get("occurred_at"),
                             turn_id=payload.get("turn_id"), source_event_id=message_id,
                             capture_status="captured" if payload.get("source_complete", True) else "partial")
        for filename, data in validated_attachments:
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "attachment.bin"
                path.write_bytes(data)
                attach_file(member_root, session, path, filename, turn_id=payload.get("turn_id"))
        index["dedup"][key] = {"event_id": event["event_id"], "session_id": event["session_id"]}
        save_json_atomic(index_path, index)
        member_index = build_index(member_root)
        member_index["member_id"] = member_id
        save_json_atomic(member_root / "indexes" / "sessions.json", member_index)
        if verify_session(session):
            raise RuntimeError("Kiểm tra chuỗi hash session không thành công")
        relative = member_root.relative_to(ROOT).as_posix()
        git("add", "-A", "--", relative)
        staged = git("diff", "--cached", "--name-only").splitlines()
        if not staged or any(not p.startswith("AI-Memory/" + relative + "/") for p in staged):
            raise RuntimeError("Phát hiện file staged ngoài vùng dữ liệu member")
        git("commit", "-m", f"memory({member_id}): capture {kind} {key[:12]}")
        sha = git("rev-parse", "HEAD")
        git("push", "origin", f"HEAD:refs/heads/{cfg['memory_branch']}")
        verify_remote(sha, cfg["memory_branch"])
        return {"status": "synced", "member_id": member_id,
                "event_id": event["event_id"], "session_id": event["session_id"],
                "commit_sha": sha}


def main():
    parser = argparse.ArgumentParser(description="Trusted host per-message capture")
    parser.add_argument("--payload-file", required=True,
                        help="JSON event host quan sát được, dùng '-' để đọc stdin")
    parser.add_argument("--token-env", default="AI_CAPTURE_TOKEN",
                        help="Tên biến môi trường chứa token, không nhập token qua CLI")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    raw = sys.stdin.read() if args.payload_file == "-" else Path(args.payload_file).read_text(encoding="utf-8")
    try:
        result = ingest(json.loads(raw), os.environ.get(args.token_env), args.dry_run)
        print(json.dumps(result, ensure_ascii=False))
    except (ValueError, OSError, RuntimeError, PermissionError, KeyError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
