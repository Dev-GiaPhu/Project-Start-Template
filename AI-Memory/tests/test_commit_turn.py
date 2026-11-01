"""Kiểm thử mỗi lượt đúng một commit; không kết nối GitHub hoặc ghi nhánh thật."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SOURCE_TOOLS = Path(__file__).resolve().parents[1] / "tools"


def git(root, *args):
    process = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if process.returncode:
        raise AssertionError(f"Git {args[0]} thất bại: {process.stderr}")
    return process.stdout.strip()


class TurnCommitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "project"
        self.repo.mkdir()
        git(self.repo, "init")
        git(self.repo, "config", "user.name", "PAM Test")
        git(self.repo, "config", "user.email", "pam-test@example.invalid")
        git(self.repo, "checkout", "-b", "feature/ai-project-memory")
        git(self.repo, "remote", "add", "origin", "https://github.com/example-owner/example-project.git")
        tools = self.repo / "AI-Memory" / "tools"
        tools.mkdir(parents=True)
        for name in ("event_store.py", "commit_turn.py"):
            shutil.copyfile(SOURCE_TOOLS / name, tools / name)
        (self.repo / "AI-Memory" / "project.json").write_text(json.dumps({
            "initialized": True,
            "project_id": "example-project",
            "memory_repository": "example-owner/example-project",
            "memory_branch": "feature/ai-project-memory"
        }))
        git(self.repo, "add", "AI-Memory/tools", "AI-Memory/project.json")
        git(self.repo, "commit", "-m", "Initial test fixture")
        sys.path.insert(0, str(tools))
        from event_store import create_session, append_event
        self.create_session = create_session
        self.append_event = append_event
        self.root = self.repo / "AI-Memory"
        self.session = create_session(self.root, "codex", "Test event workflow")
        self.relative = self.session.relative_to(self.root).as_posix()
        self.script = tools / "commit_turn.py"

    def record_turn(self, turn_id="turn-1", final=True):
        self.append_event(self.session, "message.created", "user", {"text": "Xin chào"}, turn_id=turn_id)
        self.append_event(self.session, "tool.call", "assistant",
                          {"name": "get_file", "arguments": {"path": "README.md"}},
                          turn_id=turn_id, tool_call_id="tool-1")
        self.append_event(self.session, "tool.result", "tool", {"status": "ok"},
                          turn_id=turn_id, tool_call_id="tool-1")
        if final:
            self.append_event(self.session, "message.completed", "assistant",
                              {"text": "Trả lời đầy đủ."}, turn_id=turn_id)

    def close(self, turn_id):
        return subprocess.run([
            sys.executable, str(self.script), "--session", self.relative,
            "--turn-id", turn_id, "--approved", "--no-push"
        ], cwd=self.repo, capture_output=True, text=True)

    def test_one_complete_turn_one_commit_and_idempotent_retry(self):
        self.record_turn()
        run = self.close("turn-1")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("CHƯA ĐỒNG BỘ GITHUB", run.stdout)
        head = git(self.repo, "rev-parse", "HEAD")
        self.assertIn("PAM-Turn-ID: turn-1", git(self.repo, "log", "-1", "--format=%B"))
        self.assertEqual(git(self.repo, "show", "--pretty=", "--name-only", "HEAD").count("AI-Memory/"), 3)
        repeat = self.close("turn-1")
        self.assertEqual(repeat.returncode, 0, repeat.stderr)
        self.assertEqual(git(self.repo, "rev-parse", "HEAD"), head)

    def test_reject_unfinished_assistant_reply(self):
        self.record_turn(final=False)
        result = self.close("turn-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CHƯA ĐỒNG BỘ", result.stderr)
        self.assertNotIn("memory(turn)", git(self.repo, "log", "--oneline"))

    def test_reject_wrong_turn_mixed_events(self):
        self.record_turn()
        self.append_event(self.session, "tool.result", "tool", {"result": "other"},
                          turn_id="turn-2")
        result = self.close("turn-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("khác lượt", result.stderr)

    def test_reject_main_branch(self):
        self.record_turn()
        git(self.repo, "checkout", "-b", "main")
        result = self.close("turn-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("chỉ commit trên nhánh bộ nhớ", result.stderr)

    def test_second_turn_is_another_commit(self):
        self.record_turn("turn-1")
        self.assertEqual(self.close("turn-1").returncode, 0)
        self.record_turn("turn-2")
        self.assertEqual(self.close("turn-2").returncode, 0)
        self.assertEqual(len(git(self.repo, "log", "--format=%s", "--", f"AI-Memory/{self.relative}").splitlines()), 2)

    def test_reject_credential_in_payload(self):
        self.record_turn()
        self.append_event(self.session, "tool.result", "tool",
                          {"header": "Authorization: Bearer abc_secret_123"},
                          turn_id="turn-1")
        result = self.close("turn-1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("credential", result.stderr)


if __name__ == "__main__":
    unittest.main()
