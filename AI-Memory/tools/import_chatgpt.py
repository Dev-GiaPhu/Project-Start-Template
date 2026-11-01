#!/usr/bin/env python3
"""Nhập một hội thoại từ file export ChatGPT (JSON/ZIP) khi đã được chủ dữ liệu duyệt.

Không giả lập sự kiện hay công cụ bị thiếu; không truy cập API ChatGPT.
Chỉ lấy phần dữ liệu thực sự có trong export; không nhập system/developer/analysis.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from event_store import (
    PROJECT_ID, append_event, create_session, load_json, save_json_atomic, session_lock
)
from record_cli import ROOT, ensure_memory_branch

HIDDEN_CHANNELS = {"analysis", "justify", "confidence"}
HIDDEN_ROLES = {"system", "developer"}
EXPORT_NAMES = re.compile(r"^conversations(?:[-_][0-9]+)?\.json$", re.IGNORECASE)


def load_conversations(path: Path) -> list[dict]:
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as container:
            files = [name for name in container.namelist()
                     if EXPORT_NAMES.fullmatch(Path(name).name)]
            if not files:
                raise ValueError("ZIP không chứa conversations.json/phiên bản đánh số")
            merged = []
            for name in files:
                with container.open(name) as stream:
                    content = json.load(stream)
                    if not isinstance(content, list):
                        raise ValueError(f"{name} không chứa danh sách hội thoại")
                    merged.extend(content)
            return merged
    content = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(content, list):
        raise ValueError("Tệp JSON cần chứa danh sách hội thoại")
    return content


def iso_from_epoch(value):
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(value, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None


def import_conversation(root: Path, conversation: dict, author: str = "unspecified") -> tuple[Path, int]:
    conversation_id = conversation.get("id") or conversation.get("conversation_id")
    if not conversation_id:
        raise ValueError("Hội thoại không có id")
    for meta_path in (root / "conversations").glob("*/*/*/*/session.json"):
        if load_json(meta_path).get("source_conversation_id") == conversation_id:
            raise ValueError(f"Đã nhập hội thoại {conversation_id}; không nhập trùng")
    title = str(conversation.get("title") or "(không có tiêu đề)")
    session = create_session(
        root, platform="chatgpt", title=title, author=author,
        source_conversation_id=str(conversation_id),
        capture_method="chatgpt_export", capture_status="partial"
    )
    # Mapping là đồ thị phân nhánh; lưu parent/children và thứ tự gốc, không giả định tuyến chat duy nhất.
    mapping = conversation.get("mapping", {})
    if not isinstance(mapping, dict):
        raise ValueError("Không có đồ thị mapping hợp lệ")
    nodes = list(mapping.items())
    def ordering(item):
        node = item[1] if isinstance(item[1], dict) else {}
        msg = node.get("message") or {}
        t = msg.get("create_time") if isinstance(msg, dict) else None
        return (t if isinstance(t, (int, float)) else float("inf"), item[0])
    count = 0
    for node_id, node in sorted(nodes, key=ordering):
        if not isinstance(node, dict):
            continue
        message = node.get("message")
        skeleton = {
            "node_id": node_id,
            "parent_node_id": node.get("parent"),
            "child_node_ids": node.get("children", [])
        }
        if not isinstance(message, dict):
            append_event(session, "conversation.node", "recorder", skeleton,
                         source_event_id=str(node_id))
            count += 1
            continue
        author_info = message.get("author") or {}
        role = author_info.get("role", "unknown") if isinstance(author_info, dict) else "unknown"
        metadata = message.get("metadata") or {}
        channel = metadata.get("channel") if isinstance(metadata, dict) else None
        if role in HIDDEN_ROLES or channel in HIDDEN_CHANNELS:
            append_event(session, "conversation.node.omitted", "recorder",
                         {**skeleton, "reason": "internal_role_or_channel_not_exported_as_memory"},
                         source_event_id=str(message.get("id") or node_id),
                         capture_status="partial")
            count += 1
            continue
        payload = {**skeleton, "exported_message": message}
        append_event(session, "message.imported", str(role), payload,
                     occurred_at=iso_from_epoch(message.get("create_time")),
                     source_event_id=str(message.get("id") or node_id))
        count += 1
    gaps = [
        {"kind": "live_tool_trace", "reason": "Export không bảo đảm chứa từng thao tác công cụ"},
        {"kind": "attachments", "reason": "Tệp gốc chỉ được lưu nếu xuất và nhập được; tham chiếu không tương đương bytes"},
        {"kind": "hidden_internal_state", "reason": "Không thu thập suy luận nội bộ hoặc dữ liệu nền tảng không cung cấp"}
    ]
    with session_lock(session):
        manifest = load_json(session / "session.json")
        manifest["capture_gaps"] = gaps
        manifest["export_metadata"] = {
            "conversation_id": str(conversation_id),
            "source_title": title,
            "create_time": iso_from_epoch(conversation.get("create_time")),
            "update_time": iso_from_epoch(conversation.get("update_time")),
            "current_node": conversation.get("current_node")
        }
        save_json_atomic(session / "session.json", manifest)
    return session, count


def main():
    parser = argparse.ArgumentParser(description="Nhập dữ liệu chat đã xuất (mỗi lần một conversation ID)")
    parser.add_argument("export", help="conversations.json hoặc ZIP export")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--list", action="store_true", help="Liệt kê ID/title; không ghi")
    selection.add_argument("--conversation-id", help="ID hội thoại cần nhập")
    parser.add_argument("--author", default="unspecified")
    parser.add_argument("--approved", action="store_true", help="Xác nhận quyền lưu hội thoại vào repo nhóm")
    args = parser.parse_args()
    try:
        source = load_conversations(Path(args.export))
        if args.list:
            for conversation in source:
                print(json.dumps({
                    "id": conversation.get("id") or conversation.get("conversation_id"),
                    "title": conversation.get("title")
                }, ensure_ascii=False))
            return
        ensure_memory_branch()
        if not args.approved:
            raise ValueError("Yêu cầu --approved để nhập hội thoại")
        matching = [c for c in source
                    if str(c.get("id") or c.get("conversation_id")) == args.conversation_id]
        if len(matching) != 1:
            raise ValueError(f"Yêu cầu đúng một hội thoại ID {args.conversation_id!r}; tìm được {len(matching)}")
        result, count = import_conversation(ROOT, matching[0], args.author)
        print(f"Đã nhập {count} nodes/events vào {result.relative_to(ROOT)} (capture_status=partial)")
        print("Không mặc định có đủ tool trace, attachments, hoặc toàn bộ nội dung ẩn.")
    except (ValueError, OSError, KeyError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        parser.exit(2, f"LỖI: {exc}\n")


if __name__ == "__main__":
    main()
