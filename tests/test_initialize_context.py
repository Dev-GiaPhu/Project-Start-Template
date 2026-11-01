"""Kiểm thử khởi tạo dự án mới trên repository local giả."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools" / "initialize_context.py"


def run_git(path, *args):
    proc = subprocess.run(["git", "-C", str(path), *args], capture_output=True, text=True)
    if proc.returncode:
        raise AssertionError(f"git {args[0]}: {proc.stderr}")
    return proc.stdout.strip()


class InitializeContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "project"
        self.root.mkdir()
        for name in ("PROJECT_CONFIG.json", "PROJECT_CONTEXT.md", "PROJECT_STATUS.md"):
            shutil.copyfile(ROOT / name, self.root / name)
        (self.root / "tools").mkdir()
        shutil.copyfile(SOURCE, self.root / "tools" / "initialize_context.py")
        run_git(self.root, "init")
        run_git(self.root, "config", "user.name", "Test")
        run_git(self.root, "config", "user.email", "test@example.invalid")
        run_git(self.root, "checkout", "-b", "ai-context")
        run_git(self.root, "remote", "add", "origin", "https://github.com/example-owner/example-project.git")
        run_git(self.root, "add", ".")
        run_git(self.root, "commit", "-m", "test initialization")

    def initialize(self, *extra):
        return subprocess.run([
            sys.executable, str(self.root / "tools" / "initialize_context.py"),
            "--repo", "example-owner/example-project",
            "--project-id", "example-project", "--name", "Example project",
            *extra
        ], capture_output=True, text=True)

    def test_requires_approval(self):
        result = self.initialize()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--approved", result.stderr)

    def test_config_and_handoff_are_initialized(self):
        result = self.initialize("--approved")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = json.loads((self.root / "PROJECT_CONFIG.json").read_text(encoding="utf-8"))
        self.assertTrue(config["initialized"])
        self.assertEqual(config["project_id"], "example-project")
        self.assertEqual(config["repository"], "example-owner/example-project")
        self.assertIn("Example project", (self.root / "PROJECT_CONTEXT.md").read_text(encoding="utf-8"))
        self.assertIn("ĐÃ KHỞI TẠO", (self.root / "PROJECT_STATUS.md").read_text(encoding="utf-8"))
        self.assertEqual(self.initialize("--approved").returncode, 2)

    def test_refuses_to_write_main(self):
        run_git(self.root, "checkout", "-b", "main")
        result = self.initialize("--approved")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ai-context", result.stderr)
        self.assertFalse(json.loads((self.root / "PROJECT_CONFIG.json").read_text())["initialized"])


if __name__ == "__main__":
    unittest.main()
