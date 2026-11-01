#!/usr/bin/env python3
"""Khởi tạo PROJECT_CONFIG và phần định danh Context; chỉ chạy trên ai-context."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def git(*args: str) -> str:
    process = subprocess.run(
        ["git", "-C", str(ROOT), *args], capture_output=True, text=True
    )
    if process.returncode:
        raise RuntimeError("Git command failed: " + args[0])
    return process.stdout.strip()


def initialize(args) -> None:
    if not args.approved:
        raise ValueError("Yêu cầu --approved khi chủ dự án đã cho phép khởi tạo.")
    if git("branch", "--show-current") != "ai-context":
        raise RuntimeError("TỪ CHỐI: chỉ sửa tài liệu trên nhánh ai-context.")
    if not REPO.fullmatch(args.repo) or not ID.fullmatch(args.project_id):
        raise ValueError("repo phải là OWNER/REPO và project-id dạng slug.")
    remote = git("remote", "get-url", "origin").lower().removesuffix(".git").rstrip("/")
    expected = args.repo.lower()
    valid = (
        f"https://github.com/{expected}",
        f"git@github.com:{expected}",
        f"ssh://git@github.com/{expected}"
    )
    if remote not in valid:
        raise ValueError("Repo --repo không khớp remote origin; từ chối ghi.")
    path = ROOT / "PROJECT_CONFIG.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("initialized"):
        raise ValueError("Dự án đã khởi tạo; không tự ghi đè danh tính.")
    if not args.name.strip() or len(args.name.strip()) > 150:
        raise ValueError("Tên dự án không hợp lệ.")
    data.update(
        initialized=True, project_id=args.project_id,
        project_name=args.name.strip(), repository=args.repo,
        project_type=args.type, timezone=args.timezone
    )
    context = ROOT / "PROJECT_CONTEXT.md"
    text = context.read_text(encoding="utf-8")
    expected_lines = {
        "- **Tên dự án:** Chưa khởi tạo — lấy từ \`PROJECT_CONFIG.json\`.": f"- **Tên dự án:** {args.name.strip()}.",
        "- **Repository:** Chưa khởi tạo — lấy từ \`PROJECT_CONFIG.json\`.": f"- **Repository:** \`{args.repo}\`."
    }
    for old, new in expected_lines.items():
        if old not in text:
            raise ValueError("Context không còn có placeholder dự kiến; không ghi đè.")
        text = text.replace(old, new, 1)
    status_path = ROOT / "PROJECT_STATUS.md"
    status = status_path.read_text(encoding="utf-8")
    old_status = "**Trạng thái template:** CHƯA KHỞI TẠO. File này không khẳng định dự án đã bắt đầu, đã có code hay đã kiểm thử."
    if old_status not in status:
        raise ValueError("Status template đã thay đổi; không tự cập nhật.")
    status = status.replace(old_status,
      "**Trạng thái dự án:** ĐÃ KHỞI TẠO ĐỊNH DANH; chưa có bằng chứng code/kiểm thử.")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    context.write_text(text, encoding="utf-8")
    status_path.write_text(status, encoding="utf-8")
    print("Đã khởi tạo local. CHƯA COMMIT/PUSH. Chỉ stage 3 file Context/Config/Status trên ai-context.")


def main():
    parser = argparse.ArgumentParser(description="Điền định danh dự án vào nhánh ai-context")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--type", default="other", choices=["software","game","research","content","design","other"])
    parser.add_argument("--timezone", default="UTC")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()
    try:
        initialize(args)
    except (ValueError, RuntimeError, OSError, KeyError) as exc:
        parser.exit(2, "CHƯA KHỞI TẠO: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
