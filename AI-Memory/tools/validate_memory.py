#!/usr/bin/env python3
"""Kiểm tra cấu trúc kho nhật ký và toàn vẹn của phiên mới; tệp legacy được giữ nguyên."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from event_store import PROJECT_ID, verify_session

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "README.md", "project.json", "MEMORY_INDEX.md",
    "docs/ARCHIVE_FORMAT.md", "tools/event_store.py", "tools/record_cli.py",
    "tools/import_chatgpt.py", "schemas/event.schema.json",
    "schemas/session.schema.json", "conversations/README.md"
)


def validate() -> list[str]:
    errors = []
    for item in REQUIRED:
        if not (ROOT / item).is_file():
            errors.append(f"Thiếu {item}")
    try:
        config = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
        if config.get("initialized"):
            if not config.get("project_id") or config.get("project_id") != PROJECT_ID:
                errors.append("project_id không đúng")
            if not config.get("memory_repository"):
                errors.append("Thiếu memory_repository")
        elif any(config.get(key) is not None for key in ("project_id", "memory_repository")):
            errors.append("Template chưa khởi tạo phải giữ định danh null")
        if config.get("memory_branch") != "feature/ai-project-memory":
            errors.append("memory_branch không đúng")
    except (ValueError, OSError, KeyError) as exc:
        errors.append(f"project.json: {exc}")
    for metadata in (ROOT / "conversations").glob("*/*/*/*/session.json"):
        errors.extend(f"{metadata.parent.relative_to(ROOT)}: {x}" for x in verify_session(ROOT, metadata.parent))
    # Không yêu cầu summary.md hoặc messages.jsonl ở mỗi phiên: events.jsonl là nguồn nguyên gốc.
    return errors


if __name__ == "__main__":
    result = validate()
    if result:
        print("\n".join(result), file=sys.stderr)
        sys.exit(1)
    print("OK — cấu trúc và tính toàn vẹn các sự kiện quan sát được; không chứng nhận dữ liệu thu thập 100%")
