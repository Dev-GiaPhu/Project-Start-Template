#!/usr/bin/env python3
"""Khởi tạo archive identity. Không ghi nhánh khác hay tự commit/push."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = re.compile(r"^[a-z][a-z0-9-]{1,62}$")
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def git(*args):
    proc = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    if proc.returncode:
        raise RuntimeError("Không thể kiểm tra Git: " + args[0])
    return proc.stdout.strip()


def initialize(args):
    if not args.approved:
        raise ValueError("Cần --approved sau khi đã được chủ repository đồng ý.")
    branch = git("branch", "--show-current")
    if branch != "feature/ai-project-memory":
        raise RuntimeError("Chỉ khởi tạo cấu hình trên nhánh feature/ai-project-memory.")
    if not REPO.fullmatch(args.repo) or not SLUG.fullmatch(args.project_id):
        raise ValueError("repo phải ở dạng OWNER/REPO; project-id phải là slug hợp lệ.")
    origin = git("remote", "get-url", "origin").lower().rstrip("/").removesuffix(".git")
    target = args.repo.lower()
    if origin not in (f"https://github.com/{target}", f"git@github.com:{target}",
                      f"ssh://git@github.com/{target}"):
        raise RuntimeError("--repo không khớp Git origin; từ chối ghi.")
    config_file = ROOT / "project.json"
    config = json.loads(config_file.read_text(encoding="utf-8"))
    if config.get("initialized"):
        raise ValueError("Định danh đã được khởi tạo; không tự ghi đè.")
    if config.get("memory_branch") != branch:
        raise ValueError("Nhánh cấu hình không khớp nhánh đang làm việc.")
    config.update({
        "initialized": True,
        "project_id": args.project_id,
        "project_name": args.name.strip() if args.name else None,
        "memory_repository": args.repo,
        "source_repository": args.repo,
        "timezone": args.timezone,
        "automatic_chat_capture_configured": False
    })
    config_file.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Đã điền cấu hình local. CHƯA COMMIT hoặc PUSH.")


def main():
    parser = argparse.ArgumentParser(description="Khởi tạo định danh bộ nhớ cho một dự án mới")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--name")
    parser.add_argument("--timezone", default="UTC")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()
    try:
        initialize(args)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, "CHƯA KHỞI TẠO: " + str(exc) + "\n")


if __name__ == "__main__":
    main()
