"""Kiểm thử bộ ghi sự kiện bằng dữ liệu giả lập, không lấy dữ liệu chat thật."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))
from event_store import (
    append_event, attach_file, build_index, create_session, read_events, verify_session
)
from import_chatgpt import import_conversation


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tempdir.cleanup)
        self.root = Path(self.tempdir.name)
        (self.root / "conversations").mkdir()

    def test_round_trip_messages_and_actions(self):
        session = create_session(self.root, "codex", "Test", capture_method="instrumented")
        events = [
            append_event(session, "message.created", "user", {"content": [{"type": "text", "text": "Xin chào"}]}),
            append_event(session, "tool.call", "assistant", {"tool": "read_file", "arguments": {"path": "example.txt"}}, tool_call_id="c1"),
            append_event(session, "tool.result", "tool", {"output": "nội dung file"}, tool_call_id="c1"),
            append_event(session, "message.created", "assistant", {"content": [{"type": "markdown", "text": "**Xong**"}]})
        ]
        self.assertEqual([e["sequence"] for e in events], [1, 2, 3, 4])
        self.assertEqual(events[1]["links"]["tool_call_id"], "c1")
        self.assertEqual(len(list(read_events(session))), 4)
        self.assertEqual(verify_session(self.root, session), [])

    def test_binary_attachment_and_deduplication(self):
        session = create_session(self.root, "manual", "Attachment")
        source = self.root / "demo.bin"
        source.write_bytes(b"\x00\xff\x00\xaa")
        a = attach_file(self.root, session, source)
        b = attach_file(self.root, session, source)
        self.assertEqual(a["sha256"], b["sha256"])
        self.assertEqual((self.root / a["object_path"]).read_bytes(), source.read_bytes())
        self.assertEqual(len(json.loads((session / "session.json").read_text())["attachments"]), 1)
        self.assertEqual(verify_session(self.root, session), [])

    def test_tamper_detection(self):
        session = create_session(self.root, "chatgpt", "Integrity")
        append_event(session, "message.created", "user", {"text": "đúng"})
        file = session / "events.jsonl"
        file.write_text(file.read_text(encoding="utf-8").replace("đúng", "sai"), encoding="utf-8")
        self.assertTrue(any("checksum" in item for item in verify_session(self.root, session)))

    def test_index_is_metadata_only(self):
        session = create_session(self.root, "codex", "Không lặp nội dung")
        append_event(session, "message.created", "user", {"text": "PRIVATE_MESSAGE_CONTENT"})
        index = build_index(self.root)
        self.assertEqual(index["session_count"], 1)
        self.assertNotIn("PRIVATE_MESSAGE_CONTENT", json.dumps(index))
        self.assertEqual(index["sessions"][0]["event_count"], 1)

    def test_chatgpt_export_preserves_raw_nodes_and_branches(self):
        fake_export = {
            "id": "test-conversation-1", "title": "Kiểm thử dữ liệu",
            "current_node": "b", "mapping": {
                "root": {"message": None, "parent": None, "children": ["a"]},
                "a": {"parent": "root", "children": ["b", "c"], "message": {
                    "id": "msg-a", "author": {"role": "user"}, "create_time": 1762100000,
                    "content": {"content_type": "text", "parts": ["nội dung gốc"]}}},
                "b": {"parent": "a", "children": [], "message": {
                    "id": "msg-b", "author": {"role": "assistant"}, "create_time": 1762100001,
                    "content": {"content_type": "text", "parts": ["trả lời"]}}},
                "c": {"parent": "a", "children": [], "message": {
                    "id": "msg-c", "author": {"role": "system"}, "create_time": 1762100002,
                    "content": {"parts": ["internal"]}}}
            }}
        session, count = import_conversation(self.root, fake_export)
        self.assertEqual(count, 4)
        events = list(read_events(session))
        self.assertEqual(len(events), 4)
        self.assertEqual(verify_session(self.root, session), [])
        self.assertIn("nội dung gốc", json.dumps(events, ensure_ascii=False))
        self.assertNotIn('"parts": ["internal"]', json.dumps(events, ensure_ascii=False))
        self.assertEqual(json.loads((session / "session.json").read_text())["capture_status"], "partial")
        self.assertTrue(any(e["kind"] == "conversation.node.omitted" for e in events))
        with self.assertRaises(ValueError):
            import_conversation(self.root, fake_export)

    def test_event_log_segments_do_not_lose_order(self):
        import event_store
        original = event_store.SEGMENT_TARGET
        event_store.SEGMENT_TARGET = 300
        try:
            session = create_session(self.root, "codex", "Segments")
            for i in range(5):
                append_event(session, "tool.result", "tool", {"payload": f"{i}-" + "x" * 100})
            self.assertGreaterEqual(len(list((session / "segments").glob("*.jsonl"))), 1)
            self.assertEqual([e["sequence"] for e in read_events(session)], [1, 2, 3, 4, 5])
            self.assertEqual(verify_session(self.root, session), [])
        finally:
            event_store.SEGMENT_TARGET = original

    def test_large_attachment_is_split_into_git_safe_chunks(self):
        session = create_session(self.root, "codex", "Big file")
        raw = b"\x00\xfe\x01\xff" * (2 * 1024 * 1024 + 5)
        source = self.root / "big.bin"
        source.write_bytes(raw)
        attachment = attach_file(self.root, session, source)
        self.assertEqual(attachment["storage"], "chunked-sha256-v1")
        self.assertEqual(len(attachment["chunks"]), 2)
        self.assertEqual(verify_session(self.root, session), [])

    def test_event_time_needs_timezone(self):
        session = create_session(self.root, "codex", "Time")
        with self.assertRaises(ValueError):
            append_event(session, "message.created", "user", {"text": "hi"}, occurred_at="2026-11-02T05:30:00")


if __name__ == "__main__":
    unittest.main()
