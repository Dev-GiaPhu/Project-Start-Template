"""Kiểm tra mẫu rỗng không tự ghi lịch sử hoặc dữ liệu dự án."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemplateArchiveTests(unittest.TestCase):
    def test_template_config_uninitialized(self):
        config = json.loads((ROOT / "project.json").read_text(encoding="utf-8"))
        # Test running in source template must not assert a real project is initialized.
        if not config.get("initialized"):
            self.assertIsNone(config.get("project_id"))
            self.assertIsNone(config.get("memory_repository"))
        self.assertEqual(config["memory_branch"], "feature/ai-project-memory")

    def test_empty_template_has_no_fake_chat_sessions(self):
        if not json.loads((ROOT / "project.json").read_text()).get("initialized"):
            self.assertEqual(list((ROOT / "conversations").glob("*/*/*/*/session.json")), [])

    def test_initializer_requires_approval(self):
        p = subprocess.run([
            sys.executable, str(ROOT / "tools" / "initialize_memory.py"),
            "--repo", "example-owner/example-project", "--project-id", "example-project"
        ], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("--approved", p.stderr)


if __name__ == "__main__":
    unittest.main()
