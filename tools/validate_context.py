#!/usr/bin/env python3
"""Kiểm tra file và định danh AI Context bằng Python standard library."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "AI_PROJECT_WORKING_RULES.md", "PROJECT_CONFIG.json", "PROJECT_CONTEXT.md",
    "PROJECT_STATUS.md", "PROJECT_ROADMAP.md", "DECISIONS.md",
    "docs/NEW_PROJECT_SETUP.md", "docs/FILE_OWNERSHIP.md"
]


def validate(root=ROOT):
    errors = [f"Thiếu file: {path}" for path in REQUIRED if not (root/path).is_file()]
    if not (root/"PROJECT_CONFIG.json").is_file():
        return errors
    try:
        config = json.loads((root/"PROJECT_CONFIG.json").read_text(encoding="utf-8"))
        for key, branch in (("main_branch","main"),("context_branch","ai-context"),("memory_branch","feature/ai-project-memory")):
            if config.get(key) != branch:
                errors.append(f"Sai cấu hình {key}")
        if config.get("initialized"):
            if not re.fullmatch(r"[a-z][a-z0-9-]{1,62}", config.get("project_id") or ""):
                errors.append("project_id không hợp lệ")
            if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", config.get("repository") or ""):
                errors.append("repository không hợp lệ")
            if not config.get("project_name"):
                errors.append("Thiếu project_name")
        else:
            if any(config.get(key) is not None for key in ("project_id","project_name","repository")):
                errors.append("Cấu hình chưa khởi tạo phải giữ project_id/name/repository=null")
        context = (root/"PROJECT_CONTEXT.md").read_text(encoding="utf-8")
        if "## 0. QUY TRÌNH TỰ TIẾP NHẬN" not in context:
            errors.append("Context thiếu hướng dẫn tự tiếp nhận")
    except (ValueError, OSError, TypeError) as error:
        errors.append(f"Config/Context: {error}")
    return errors


if __name__ == "__main__":
    errors = validate()
    if errors:
        print("\n".join("LỖI: "+e for e in errors),file=sys.stderr)
        sys.exit(1)
    print("OK: AI Context đúng cấu trúc; không kiểm chứng nội dung dự án đã được điền.")
