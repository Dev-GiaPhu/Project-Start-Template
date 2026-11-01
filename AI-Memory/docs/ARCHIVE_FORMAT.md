# Archive v2 — Hợp đồng dữ liệu máy đọc được

Mỗi phiên `conversations/YYYY/MM/DD/<session-id>/` có `session.json` và một hay nhiều tệp JSONL sự kiện. Mỗi dòng một object JSON UTF-8 theo `schemas/event.schema.json`. Các file chỉ chứa sự kiện **có thật, có thể quan sát** từ nguồn dữ liệu.

- **`kind`:** tên loại sự kiện mở, ví dụ `message.created`, `message.completed`, `message.edited`, `tool.call`, `tool.result`, `tool.error`, `tool.approval`, `file.read`, `file.write`, `ui.rendered`, `attachment.imported`, `capture.gap`.
- **`actor`:** user, assistant, tool hoặc recorder. `payload` chứa dữ liệu nguyên gốc theo khả năng xuất của host, giữ code, Markdown, đa phương thức và các cấu trúc như JSON, không tóm tắt thay nguồn.
- **`sequence`, `event_id`:** thứ tự và ID duy nhất cho mỗi sự kiện.
- **`time`:** recorded_at (có múi giờ) và UTC; occurred_at chỉ điền khi nguồn thực sự cung cấp.
- **`links`:** turn_id, parent_event_id, tool_call_id, source_event_id để nối lời chat và thao tác.
- **`previous_hash`, `hash`:** hash-chain SHA-256 trên canonical JSON để phát hiện sửa/thất lạc event trong kho đã ghi.
- **`session.json`:** nguồn, title, author (nếu có quyền lưu), capture_status/gaps, event_count, checksum cuối, attachments và phiên bản.
- **`objects/sha256`:** tệp nhị phân hoặc các khối 8 MiB theo SHA-256 có manifest khôi phục.

### Đơn vị commit
Đơn vị lưu event khác đơn vị commit. **Một user message + các event được host cung cấp + assistant final = một Git commit** sau khi final được nhận. Lệnh `commit_turn.py` dùng `session_id+turn_id` để phát hiện commit trùng và không chấp nhận sự kiện không cùng lượt.

### Mức độ đầy đủ
Checksum chỉ xác thực **dữ liệu đã ghi**, không chứng minh đã thu thập đủ dữ liệu nền tảng. Với ChatGPT export hoặc môi trường thiếu event/tool/file, ghi `capture_status=partial` và `capture.gap` khi có. Không lưu hoặc dựng lại private chain-of-thought/system instructions không được cung cấp.

### Truy xuất cho AI
Đọc chỉ mục → session metadata → events/segments theo sequence → tệp objects khi cần. Lưu ID, SHA và phần chưa đọc nếu lịch sử vượt ngữ cảnh. **Không có giới hạn số event cố định trong schema, nhưng GitHub/Git có giới hạn thực tế về dung lượng và hiệu năng.**
