# Quy trình kỹ thuật lưu một lượt

**Luật được chủ dự án duyệt** thuộc `ai-context/AI_PROJECT_WORKING_RULES.md`; file này chỉ hướng dẫn bộ ghi.

1. Nguồn (host/adapter/export) cung cấp event và metadata thực tế, có quyền lưu.
2. Gán `session_id`, `turn_id`; ghi user message, các tool/input/output/error/attachment/UI event quan sát được theo trình tự.
3. Nhận assistant final thật từ host **sau khi phản hồi hoàn tất**, ghi `message.completed` kèm cùng `turn_id`.
4. `commit_turn.py` xác minh toàn vẹn hash, nhánh, remote, không lẫn lượt, final và nội dung tối thiểu; commit chỉ file `AI-Memory/`, push non-force.
5. Xác minh SHA remote rồi mới báo đã đồng bộ. Nếu không có adapter sau final thì báo CHƯA ĐỒNG BỘ, không tạo commit giả.
6. Không tự đồng bộ vào `ai-context` hay `main`; chỉ lưu ID/sha đường dẫn làm con trỏ tới nguồn, không chép GDD/Rules/Context.

**Lưu ý:** với import lịch sử ChatGPT, những event xuất sẵn không nhất thiết có `turn_id` và assistant final tương thích, nên không tuyên bố importer tạo được live one-commit-per-turn tự động.
