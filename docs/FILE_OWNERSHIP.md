# Sở hữu file, không ghi trùng

| Loại dữ liệu | Nhánh/file chịu trách nhiệm | Không ghi ở |
| --- | --- | --- |
| Sản phẩm thực | `main` | ai-context, memory |
| Quy tắc AI | `ai-context/AI_PROJECT_WORKING_RULES.md` | main, memory, Context |
| Cấu hình/tên dự án | `ai-context/PROJECT_CONFIG.json` | main, mô tả history |
| Ngữ cảnh kỹ thuật và file bàn giao | `ai-context/PROJECT_CONTEXT.md` | main, memory |
| Tình trạng thực nghiệm | `ai-context/PROJECT_STATUS.md` | roadmap, memory summary |
| Việc tương lai | `ai-context/PROJECT_ROADMAP.md` | status, memory summary |
| Quyết định đã chốt | `ai-context/DECISIONS.md` | memory làm nguồn chuẩn |
| GDD/spec đã được người dùng duyệt (nếu có) | `ai-context` với file chuyên dụng | main (nếu chỉ phục vụ AI), memory |
| Tin nhắn, thao tác AI, ảnh, tệp, metadata | `feature/ai-project-memory/AI-Memory/` | main, ai-context |

Mọi tham chiếu chéo dùng `repo@branch:path#event/commit` khi có thể. Hạn chế sao chép thông tin giữa file; file bàn giao **chỉ dẫn cách nạp**, không phải bản chép toàn bộ GDD/luật/history.
