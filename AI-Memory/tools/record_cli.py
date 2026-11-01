#!/usr/bin/env python3
"""CLI lưu, đọc, tìm và kiểm tra bản ghi AI (chỉ trên nhánh bộ nhớ đã cấu hình)."""
from __future__ import annotations

import argparse
import json
import hashlib
import os
import subprocess
import sys
from pathlib import Path

from event_store import (
    append_event, attach_file, build_index, create_session,
    load_json, read_events, save_json_atomic, session_lock, verify_session
)

ROOT = Path(__file__).resolve().parents[1]


def ensure_memory_branch() -> None:
    config = load_json(ROOT / "project.json")
    if not config.get("initialized") or not config.get("project_id"):
        raise RuntimeError("Kho chưa được khởi tạo, chạy initialize_memory.py trước")
    expected = config["memory_branch"]
    result = subprocess.run(
        ["git", "-C", str(ROOT), "branch", "--show-current"],
        text=True, capture_output=True, check=False
    )
    if result.returncode != 0 or result.stdout.strip() != expected:
        actual = result.stdout.strip() if result.returncode == 0 else "(không phải Git checkout)"
        raise RuntimeError(
            f"TỪ CHỐI GHI: đang ở nhánh {actual!r}, chỉ được ghi ở {expected!r}. "
            "Không cho phép bỏ qua khóa bảo vệ qua CLI."
        )


def session_path(name: str) -> Path:
    candidate = (ROOT / name).resolve()
    if not candidate.is_relative_to(ROOT.resolve()) or not (candidate / "session.json").is_file():
        raise ValueError("Thư mục phiên không nằm trong kho bộ nhớ hoặc không tồn tại")
    return candidate


def command_new(args) -> None:
    ensure_memory_branch()
    if not args.approved:
        raise ValueError("Yêu cầu --approved sau khi người dùng đồng ý chia sẻ dữ liệu vào repo nhóm")
    folder = create_session(ROOT, args.platform, args.title, args.author,
                            args.conversation_id, args.capture_method)
    print(folder.relative_to(ROOT).as_posix())


def command_append(args) -> None:
    ensure_memory_branch()
    if not args.approved:
        raise ValueError("Yêu cầu --approved")
    if args.json_file:
        source = sys.stdin if args.json_file == "-" else open(args.json_file, "r", encoding="utf-8")
        try:
            payload = json.load(source)
        finally:
            if source is not sys.stdin:
                source.close()
    else:
        if args.text_file == "-":
            content = sys.stdin.read()
        else:
            content = Path(args.text_file).read_text(encoding="utf-8")
        payload = {"text": content}
    event = append_event(
        session_path(args.session), kind=args.kind, actor=args.actor,
        payload=payload, occurred_at=args.occurred_at,
        turn_id=args.turn_id, parent_event_id=args.parent_event_id,
        tool_call_id=args.tool_call_id, source_event_id=args.source_event_id,
        capture_status=args.capture_status
    )
    print(json.dumps({"event_id": event["event_id"], "sequence": event["sequence"], "hash": event["hash"]}))


def command_attach(args) -> None:
    ensure_memory_branch()
    if not args.approved:
        raise ValueError("Yêu cầu --approved")
    attachment = attach_file(ROOT, session_path(args.session), Path(args.file), args.name, turn_id=args.turn_id)
    print(json.dumps(attachment, ensure_ascii=False))


def command_verify(args) -> None:
    paths = [session_path(args.session)] if args.session else [
        file.parent for file in (ROOT / "conversations").glob("*/*/*/*/session.json")
    ]
    failures = []
    for session in sorted(paths):
        errors = verify_session(ROOT, session)
        for error in errors:
            failures.append(f"{session.relative_to(ROOT)}: {error}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        raise SystemExit(1)
    print(f"OK — xác minh {len(paths)} phiên; không xác nhận đã thu thập toàn bộ dữ liệu nền tảng")


def command_replay(args) -> None:
    count = 0
    for event in read_events(session_path(args.session)):
        if args.kind and event.get("kind") not in args.kind:
            continue
        print(json.dumps(event, ensure_ascii=False))
        count += 1
        if not args.all and count >= args.limit:
            break


def command_search(args) -> None:
    hits = 0
    for file in sorted((ROOT / "conversations").glob("*/*/*/*/session.json")):
        for event in read_events(file.parent):
            if args.query.casefold() in json.dumps(event.get("payload", ""), ensure_ascii=False).casefold():
                print(json.dumps({
                    "session": file.parent.relative_to(ROOT).as_posix(),
                    "event_id": event["event_id"], "kind": event["kind"],
                    "sequence": event["sequence"], "timestamp": event["time"]["recorded_at"]
                }, ensure_ascii=False))
                hits += 1
                if hits >= args.limit:
                    return


def command_index(args) -> None:
    ensure_memory_branch()
    if not args.approved:
        raise ValueError("Yêu cầu --approved")
    result = build_index(ROOT)
    save_json_atomic(ROOT / "indexes" / "sessions.json", result)
    print(f"Đã lập chỉ mục {result['session_count']} phiên, không sao chép nội dung hội thoại")


def command_restore(args) -> None:
    """Khôi phục bytes gốc từ các chunk, kiểm tra SHA-256, không sửa repository."""
    session = session_path(args.session)
    manifest = load_json(session / "session.json")
    matches = [x for x in manifest.get("attachments", []) if x.get("sha256") == args.sha256]
    if len(matches) != 1:
        raise ValueError("Không tìm được đúng một attachment với SHA-256 yêu cầu")
    item = matches[0]
    destination = Path(args.output).resolve()
    if destination.is_relative_to(ROOT.parent.resolve()):
        raise ValueError("TỪ CHỐI: phải khôi phục ra ngoài Git checkout, không viết vào nhánh code/AI")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError("Tệp đầu ra đã tồn tại; không ghi đè")
    digest = hashlib.sha256()
    written = 0
    fragments = item.get("chunks", [item])
    try:
        with destination.open("xb") as output:
            for fragment in fragments:
                object_file = (ROOT / fragment["object_path"]).resolve()
                if not object_file.is_relative_to(ROOT.resolve()):
                    raise ValueError("object_path vượt khỏi kho bộ nhớ")
                data = object_file.read_bytes()
                if hashlib.sha256(data).hexdigest() != fragment["sha256"]:
                    raise ValueError("Checksum của chunk sai")
                output.write(data)
                digest.update(data)
                written += len(data)
        if written != item["size"] or digest.hexdigest() != item["sha256"]:
            raise ValueError("Khôi phục không khớp SHA-256/size")
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    print(str(destination))


def command_gap(args) -> None:
    ensure_memory_branch()
    if not args.approved:
        raise ValueError("Yêu cầu --approved")
    session = session_path(args.session)
    with session_lock(session):
        meta = load_json(session / "session.json")
        gap = {"kind": args.kind, "reason": args.reason}
        meta.setdefault("capture_gaps", []).append(gap)
        meta["capture_status"] = "partial"
        save_json_atomic(session / "session.json", meta)
    append_event(session, "capture.gap", "recorder", gap, turn_id=args.turn_id, capture_status="partial")
    print("Đã ghi rõ phần dữ liệu không thể thu thập")


def main() -> None:
    parser = argparse.ArgumentParser(description="PAM Archive v2 — nhật ký sự kiện AI đa phương thức")
    commands = parser.add_subparsers(dest="cmd", required=True)
    new = commands.add_parser("new", help="Tạo phiên mới")
    new.add_argument("--platform", required=True, help="chatgpt, codex, other")
    new.add_argument("--title", required=True)
    new.add_argument("--author", default="unspecified")
    new.add_argument("--conversation-id")
    new.add_argument("--capture-method", default="manual")
    new.add_argument("--approved", action="store_true")
    new.set_defaults(run=command_new)

    add = commands.add_parser("append", help="Ghi một sự kiện được quan sát")
    add.add_argument("--session", required=True, help="Ví dụ conversations/2026/11/02/SESSION")
    add.add_argument("--kind", required=True, help="message.created, tool.call, tool.result, ui.rendered ...")
    add.add_argument("--actor", required=True, help="user, assistant, tool hoặc recorder")
    values = add.add_mutually_exclusive_group(required=True)
    values.add_argument("--json-file", help="File JSON chứa payload nguyên cấu trúc, hoặc '-' cho stdin")
    values.add_argument("--text-file", help="File text nội dung nguyên văn, hoặc '-' cho stdin")
    add.add_argument("--occurred-at", help="ISO-8601 có múi giờ; bỏ trống nếu không biết")
    add.add_argument("--turn-id")
    add.add_argument("--parent-event-id")
    add.add_argument("--tool-call-id")
    add.add_argument("--source-event-id")
    add.add_argument("--capture-status", choices=("captured", "partial", "missing"), default="captured")
    add.add_argument("--approved", action="store_true")
    add.set_defaults(run=command_append)

    attach = commands.add_parser("attach", help="Lưu binary nguyên bản theo SHA-256")
    attach.add_argument("--session", required=True)
    attach.add_argument("--file", required=True)
    attach.add_argument("--name")
    attach.add_argument("--turn-id", help="ID lượt để đưa attachment vào commit của lượt đó")
    attach.add_argument("--approved", action="store_true")
    attach.set_defaults(run=command_attach)

    verify = commands.add_parser("verify", help="Kiểm tra hash chain và tệp")
    verify.add_argument("--session")
    verify.set_defaults(run=command_verify)

    replay = commands.add_parser("replay", help="Xuất sự kiện JSONL nguyên gốc cho AI")
    replay.add_argument("--session", required=True)
    replay.add_argument("--kind", action="append")
    replay.add_argument("--limit", type=int, default=50)
    replay.add_argument("--all", action="store_true", help="Không cắt số lượng sự kiện")
    replay.set_defaults(run=command_replay)

    search = commands.add_parser("search", help="Tìm sự kiện từ payload thực, không tạo bản tóm tắt")
    search.add_argument("--query", required=True)
    search.add_argument("--limit", type=int, default=30)
    search.set_defaults(run=command_search)

    index = commands.add_parser("index", help="Lập chỉ mục phiên không lặp nội dung")
    index.add_argument("--approved", action="store_true")
    index.set_defaults(run=command_index)

    restore = commands.add_parser("restore", help="Khôi phục tệp gốc theo SHA-256 ra ngoài repository")
    restore.add_argument("--session", required=True)
    restore.add_argument("--sha256", required=True)
    restore.add_argument("--output", required=True)
    restore.set_defaults(run=command_restore)

    gap = commands.add_parser("gap", help="Ghi rõ dữ liệu chưa thu thập được")
    gap.add_argument("--session", required=True)
    gap.add_argument("--kind", required=True)
    gap.add_argument("--reason", required=True)
    gap.add_argument("--turn-id", help="Lượt chat cần ghi tình trạng thiếu dữ liệu")
    gap.add_argument("--approved", action="store_true")
    gap.set_defaults(run=command_gap)

    args = parser.parse_args()
    if hasattr(args, "limit") and args.limit <= 0:
        parser.error("--limit phải lớn hơn 0")
    try:
        args.run(args)
    except (RuntimeError, ValueError, FileNotFoundError, KeyError, OSError) as exc:
        parser.exit(2, f"LỖI: {exc}\n")


if __name__ == "__main__":
    main()
