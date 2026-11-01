# MEMORY INDEX — Hệ thống tra cứu (không có phiên mẫu)

- **Định danh:** `project.json`.
- **Danh mục phiên thật:** `indexes/sessions.json` (chỉ được tạo khi có dữ liệu).
- **Từng phiên:** `conversations/YYYY/MM/DD/<session-id>/session.json`.
- **Sự kiện gốc:** `segments/*.jsonl` theo số tăng dần, sau đó `events.jsonl`.
- **Bytes hình/audio/video/tài liệu nếu có:** `objects/sha256/`.
- **Hợp đồng dữ liệu:** `schemas/event.schema.json` và `schemas/session.schema.json`.
- **Công cụ:** `tools/record_cli.py`, `tools/import_chatgpt.py`, `tools/commit_turn.py`, `tools/validate_memory.py`.

**Quy trình nạp:** xác định project ID từ `project.json`; chọn session ở chỉ mục; đọc các event nguyên gốc theo thứ tự, giữ `turn_id` và tool IDs; lấy tệp theo hash khi cần. Nếu index trống thì chưa có hội thoại thực nào được lưu, không tự dựng lịch sử.

**Đối chiếu tài liệu điều hành:** đọc `ai-context/PROJECT_CONTEXT.md` và các đường dẫn nó hướng dẫn. **Không có GDD/Rules/Context sao chép tại đây.**
