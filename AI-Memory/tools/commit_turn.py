#!/usr/bin/env python3
"""Đóng một lượt trao đổi vào đúng một Git commit trên nhánh bộ nhớ.

Chạy SAU khi host đã giao câu trả lời cuối cùng và ghi message.completed.
Không tự chặn/thu thập ChatGPT/Codex, không đọc bộ nhớ riêng của mô hình.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

from event_store import build_index, load_json, read_events, save_json_atomic, verify_session, session_lock

ROOT = Path(__file__).resolve().parents[1]
PROJECT = load_json(ROOT / "project.json")
PROJECT_ID = PROJECT["project_id"]
BRANCH = PROJECT["memory_branch"]
OWNER_REPO = PROJECT["memory_repository"]
TURN_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
REDACT_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"sk-(?:proj-|live-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"Authorization\s*[:=]\s*Bearer\s+\S+", re.I),
]


def git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT.parent), *args],
        text=True, capture_output=True, check=False
    )
    if result.returncode and check:
        raise RuntimeError(f"Git {args[0]} thất bại (exit={result.returncode}). Kiểm tra Git/auth/nhánh cục bộ.")
    return result.stdout.rstrip("\n")


def guard_branch_and_remote() -> None:
    if not PROJECT.get("initialized") or not PROJECT_ID or not OWNER_REPO:
        raise RuntimeError("Template chưa được khởi tạo; từ chối commit lên GitHub")
    if git("branch", "--show-current") != BRANCH:
        raise RuntimeError(f"TỪ CHỐI: chỉ commit trên nhánh bộ nhớ {BRANCH!r}")
    url = git("remote", "get-url", "origin").lower().rstrip("/")
    expected = OWNER_REPO.lower()
    allowed = {
        f"https://github.com/{expected}",
        f"https://github.com/{expected}.git",
        f"git@github.com:{expected}",
        f"git@github.com:{expected}.git",
        f"ssh://git@github.com/{expected}",
        f"ssh://git@github.com/{expected}.git"
    }
    if url not in allowed:
        raise RuntimeError("TỪ CHỐI: origin không trỏ chính xác tới repository bộ nhớ đã cấu hình")


def resolve_session(reference: str) -> Path:
    base = (ROOT / "conversations").resolve()
    path = (ROOT / reference).resolve()
    if not path.is_relative_to(base) or not (path / "session.json").is_file():
        raise ValueError("Phiên phải nằm trong conversations/ và có session.json")
    if path.parent.parent.parent.parent != base:
        raise ValueError("Đường dẫn phiên cần có định dạng YYYY/MM/DD/session-id")
    return path


def committed_event_ids(relative: str) -> set[str]:
    files = git("ls-tree", "-r", "--name-only", "HEAD", "--", relative).splitlines()
    ids: set[str] = set()
    for path in files:
        if not path.endswith(".jsonl"):
            continue
        raw = git("show", f"HEAD:{path}")
        for line in raw.splitlines():
            if line.strip():
                ids.add(json.loads(line)["event_id"])
    return ids


def existing_commit(session_id: str, turn_id: str, relative: str) -> str | None:
    log = git("log", "--format=%H%n%B%n===PAM-ENTRY===", "HEAD", "--", relative)
    for entry in log.split("===PAM-ENTRY==="):
        if f"PAM-Session-ID: {session_id}\n" in entry and f"PAM-Turn-ID: {turn_id}\n" in entry:
            return entry.strip().splitlines()[0]
    return None


def check_events(session: Path, turn_id: str, committed_ids: set[str]) -> list[dict]:
    if (problems := verify_session(ROOT, session)):
        raise ValueError("Bản ghi không toàn vẹn: " + "; ".join(problems[:3]))
    events = list(read_events(session))
    new = [e for e in events if e["event_id"] not in committed_ids]
    if not new:
        raise ValueError("Không có sự kiện mới để commit")
    mismatched = [e["event_id"] for e in new if (e.get("links") or {}).get("turn_id") != turn_id]
    if mismatched:
        raise ValueError("Có sự kiện khác lượt/không có turn_id chưa commit; từ chối gộp nhiều lượt")
    user = [e for e in new if e.get("actor") == "user" and e.get("kind") in ("message.created", "message.imported")]
    assistant = [e for e in new if e.get("actor") == "assistant" and e.get("kind") == "message.completed"]
    if not user or not assistant:
        raise ValueError("Lượt chưa đủ message.created của user và message.completed của assistant; KHÔNG COMMIT trước final")
    if not all(e.get("payload") not in (None, {}, "") for e in user + assistant):
        raise ValueError("Lượt có thông điệp rỗng; không giả định đã nhận được nội dung")
    if any(e.get("capture_status") == "missing" for e in assistant):
        raise ValueError("Phản hồi cuối bị thiếu; chỉ ghi capture.gap và chờ nguồn thực")
    for event in new:
        payload_text = json.dumps(event.get("payload"), ensure_ascii=False)
        if any(p.search(payload_text) for p in REDACT_PATTERNS):
            raise ValueError("Phát hiện mẫu giống credential trong event; cần loại bỏ/bảo vệ trước khi commit")
    return new


def ensure_other_sessions_clean(current_relative: str) -> None:
    dirty = git("status", "--porcelain", "--untracked-files=all", "--", "AI-Memory/conversations")
    for line in dirty.splitlines():
        path = line[3:].strip().strip('"')
        if not path.startswith(current_relative + "/"):
            raise RuntimeError("Có phiên khác chưa được commit. Hãy xử lý riêng từng lượt trước khi cập nhật index")


def push_and_confirm(sha: str) -> None:
    git("push", "origin", f"HEAD:refs/heads/{BRANCH}")
    remote = git("ls-remote", "--heads", "origin", BRANCH)
    remote_sha = remote.split()[0] if remote else ""
    if remote_sha != sha:
        raise RuntimeError("Push trả về nhưng chưa xác nhận SHA của nhánh bộ nhớ trên GitHub")


def commit_turn(session_ref: str, turn_id: str, approved: bool, push: bool) -> str:
    if not approved:
        raise ValueError("Cần --approved khi đã kiểm tra dữ liệu được phép chia sẻ")
    if not TURN_PATTERN.fullmatch(turn_id):
        raise ValueError("turn_id chỉ gồm A-Z, a-z, 0-9, dấu -, _, . và tối đa 128 ký tự")
    guard_branch_and_remote()
    session = resolve_session(session_ref)
    relative = session.relative_to(ROOT.parent).as_posix()
    session_id = load_json(session / "session.json")["session_id"]
    with session_lock(session):
        previous = existing_commit(session_id, turn_id, relative)
        if previous:
            if push:
                head = git("rev-parse", "HEAD")
                if head != previous:
                    raise RuntimeError("Đã có commit của lượt trước đó nhưng HEAD đã đổi; từ chối push mơ hồ")
                push_and_confirm(head)
            print(f"Đã có commit trước đó, không tạo lại: {previous}")
            return previous
        if git("diff", "--cached", "--name-only"):
            raise RuntimeError("Có file đã stage từ trước; không được commit lẫn thay đổi không thuộc bộ nhớ")
        ensure_other_sessions_clean(relative)
        already = committed_event_ids(relative)
        new_events = check_events(session, turn_id, already)

        index = ROOT / "indexes" / "sessions.json"
        save_json_atomic(index, build_index(ROOT))
        paths = [
            f"{relative}/session.json",
            f"{relative}/events.jsonl",
            f"AI-Memory/indexes/sessions.json"
        ]
        paths += [p.relative_to(ROOT.parent).as_posix()
                  for p in (session / "segments").glob("*.jsonl")]
        manifest = load_json(session / "session.json")
        for item in manifest.get("attachments", []):
            chunks = item.get("chunks", [item])
            paths.extend(f"AI-Memory/{part['object_path']}" for part in chunks)
        git("add", "--", *sorted(set(paths)))
        staged = git("diff", "--cached", "--name-only").splitlines()
        if not staged or any(not x.startswith("AI-Memory/") for x in staged):
            raise RuntimeError("Phạm vi stage không hợp lệ hoặc trống")
        subject = f"memory(turn): {session_id} {turn_id}"
        body = f"PAM-Project-ID: {PROJECT_ID}\nPAM-Session-ID: {session_id}\nPAM-Turn-ID: {turn_id}\nPAM-New-Events: {len(new_events)}"
        git("commit", "-m", subject, "-m", body)
        sha = git("rev-parse", "HEAD")
        if push:
            push_and_confirm(sha)
            print(f"ĐÃ ĐỒNG BỘ GITHUB: {sha}")
        else:
            print(f"ĐÃ COMMIT LOCAL, CHƯA ĐỒNG BỘ GITHUB: {sha}")
        return sha


def main() -> None:
    parser = argparse.ArgumentParser(description="Một lượt hoàn chỉnh = đúng một commit bộ nhớ")
    parser.add_argument("--session", required=True, help="conversations/YYYY/MM/DD/<session-id>")
    parser.add_argument("--turn-id", required=True)
    parser.add_argument("--approved", action="store_true")
    parser.add_argument("--no-push", action="store_true", help="Chỉ dùng để kiểm thử hoặc khi offline")
    args = parser.parse_args()
    try:
        commit_turn(args.session, args.turn_id, args.approved, not args.no_push)
    except (ValueError, RuntimeError, OSError, json.JSONDecodeError, KeyError) as exc:
        parser.exit(2, f"CHƯA ĐỒNG BỘ: {exc}\n")


if __name__ == "__main__":
    main()
