# AI Memory Archive — kho dữ liệu sự kiện chung

**Nhánh chuyên dụng:** `feature/ai-project-memory`. Đây là cấu trúc **rỗng** để dự án mới lưu hội thoại thật. Không có dữ liệu phiên, người dùng, file, tên sản phẩm hay quyết định dự án nào được điền sẵn.

## Trách nhiệm
- **Tin nhắn/sự kiện:** dữ liệu nguyên gốc có thể quan sát từ AI và người dùng, không phải tóm tắt được AI suy diễn.
- **Thao tác:** gọi công cụ, kết quả, lỗi, quyền chấp thuận, dữ liệu UI/biểu đồ và biến thể phản hồi khi host cung cấp.
- **Tệp:** bytes của tệp có quyền lưu, được chia khối 8 MiB và đánh địa chỉ SHA-256.
- **Truy xuất:** chỉ mục phiên, các sự kiện JSONL và quan hệ `session_id` / `turn_id` / `tool_call_id`.
- **Không làm:** không lưu Rules/GDD/Context/tiến độ tại đây; các tài liệu đó ở `ai-context`. Không sửa mã sản phẩm ở `main`.

## Các đường dẫn

```text
AI-Memory/
  project.json                       # Định danh nơi lưu; ban đầu initialized=false
  MEMORY_INDEX.md                    # Chỉ mục kỹ thuật, không chứa ngữ cảnh dự án
  conversations/YYYY/MM/DD/<id>/
    session.json                     # Nguồn, thời gian, phạm vi ghi, thiếu dữ liệu
    events.jsonl                     # Sự kiện cuối, ghi nối tiếp
    segments/*.jsonl                 # Phân đoạn sự kiện trước đó
  objects/sha256/XX/<sha256>         # Bytes gốc hoặc các khối có checksum
  indexes/sessions.json             # Chỉ mục sinh ra khi có dữ liệu
  imports/                           # Nơi chuẩn bị nhập export (không commit file riêng tư)
  schemas/
  tools/
  tests/
  docs/
```

## Khởi tạo và sử dụng

Sau khi tạo dự án bằng **Use this template → Include all branches**, chạy `python3 AI-Memory/tools/initialize_memory.py --repo OWNER/PROJECT --project-id project-slug --approved` trên đúng nhánh này. File này chỉ đổi cấu hình local; cần kiểm tra diff và commit riêng.

Công cụ ghi tại `tools/record_cli.py` hỗ trợ các sự kiện có thật. `tools/commit_turn.py` kiểm tra câu trả lời AI đã hoàn tất rồi tạo **đúng một commit cho một lượt chat** và xác minh đẩy lên GitHub. Xem `docs/QUICK_START.md`.

**Không tự động ghi toàn bộ ChatGPT chỉ nhờ có branch hoặc prompt.** Cần adapter nhận dữ liệu sau final của AI hoặc nhập export có thật; thông tin không có từ nền tảng phải đánh dấu thiếu. Không lưu private reasoning hoặc secrets.
