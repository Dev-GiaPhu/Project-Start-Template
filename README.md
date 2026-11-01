# AI Context — Nguồn tài liệu chính thức của dự án

Nhánh **`ai-context`** chỉ lưu các tài liệu phục vụ AI làm việc với dự án. Đây là bộ khung **chưa chứa dữ liệu dự án**; không sao chép thông tin của một dự án cụ thể.

| File | Trách nhiệm duy nhất |
| --- | --- |
| `PROJECT_CONFIG.json` | Định danh dự án, tên repository, nhánh, loại dự án |
| `PROJECT_CONTEXT.md` | **File duy nhất cần gửi vào chat mới**; hướng dẫn AI tự nạp nguồn và bối cảnh kỹ thuật đã xác minh |
| `AI_PROJECT_WORKING_RULES.md` | **Nguồn duy nhất của toàn bộ quy tắc AI** |
| `PROJECT_STATUS.md` | Hiện trạng đã xác minh, kết quả kiểm thử và blocker |
| `PROJECT_ROADMAP.md` | Công việc dự kiến, mốc tương lai, ưu tiên |
| `DECISIONS.md` | Quyết định có thẩm quyền, bằng chứng và quyết định bị thay thế |
| `templates/` | Bản mẫu tài liệu tùy loại dự án; **không phải quyết định thực tế** |
| `docs/NEW_PROJECT_SETUP.md` | Cách tạo repo mới từ template và điền dữ liệu đúng nhánh |
| `tools/` | Công cụ khởi tạo/kiểm tra tài liệu (không sửa code sản phẩm) |

Nhánh `main` chỉ chứa **sản phẩm thực tế**. Nhánh `feature/ai-project-memory` chứa **nhật ký sự kiện nguyên gốc**. Không chuyển hoặc sao chép bộ nhớ sang đây.

**Bắt đầu:** đọc [docs/NEW_PROJECT_SETUP.md](docs/NEW_PROJECT_SETUP.md), khởi tạo cấu hình, rồi dùng [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) làm file bàn giao duy nhất.
