# PROJECT CONTEXT — TỰ TIẾP NHẬN DỰ ÁN KHI BẮT ĐẦU CHAT MỚI

> **ĐÂY LÀ FILE BÀN GIAO DUY NHẤT.** Khi người dùng tải lên hoặc gửi riêng file này, hãy coi đó là yêu cầu tiếp nhận dự án. **Không yêu cầu họ soạn thêm prompt.** Phần thông tin chưa được khởi tạo phải được báo thiếu, không được suy đoán.

## 0. QUY TRÌNH TỰ TIẾP NHẬN BẮT BUỘC

1. Đọc `PROJECT_CONFIG.json` **trên nhánh `ai-context` của repository mà người dùng đang làm**; từ đây xác định chính xác tên dự án, loại, nhánh và nguồn truy cập. Nếu `initialized=false`, chỉ tiếp nhận ở **chế độ template**, không giả vờ dự án đã có GDD/tiến độ/code.
2. Đọc `AI_PROJECT_WORKING_RULES.md` **trên cùng nhánh**; đây là nguồn duy nhất cho luật làm việc, quyền và bảo vệ `main`.
3. Với dự án game và **GDD đã được tạo/chấp thuận**, đọc GDD thực tế trên `ai-context` trước khi thiết kế game; `templates/GAME_DESIGN_DOCUMENT.template.md` chỉ là khung rỗng, **không phải GDD đã duyệt**. Với loại dự án khác, đọc tài liệu yêu cầu/thiết kế phù hợp nếu có.
4. Đọc hồ sơ **dưới đây**, `PROJECT_STATUS.md`, `PROJECT_ROADMAP.md`, `DECISIONS.md`; chỉ tin vào trạng thái được chứng minh bằng source, commit hoặc kiểm thử. Ưu tiên đính chính mới nhất, không hỏi lại quyết định đã chốt.
5. Đọc nhánh **`feature/ai-project-memory`** tại `AI-Memory/MEMORY_INDEX.md`, `AI-Memory/project.json` và chỉ mục/sự kiện thực tế đã lưu; tra các lượt liên quan và file theo ID, thứ tự, thời gian, SHA-256. Không coi tóm tắt là bản ghi chat nguyên văn.
6. Nếu chưa kết nối GitHub hoặc không có quyền đọc repository riêng tư, nói chính xác file nào chưa đọc được; sử dụng thông tin hiện có, **không tự tuyên bố đã nạp hết lịch sử**. Chỉ hỏi thêm khi thiếu nguồn cần thiết cho việc người dùng giao.
7. Đối với code sản phẩm, đọc source mới nhất do người dùng cung cấp hoặc tại `main` theo quyền được cấp; không coi GDD/Context là bằng chứng đã chạy code. **Không được ghi file AI vào `main`, kể cả theo yêu cầu thông thường.**
8. Khi có recorder/adapter có quyền nhận câu trả lời hoàn tất và được phép lưu dữ liệu, **mỗi lượt chat hoàn chỉnh đúng một commit trên nhánh bộ nhớ** sau khi lưu user message, assistant final và mọi sự kiện/tool/tệp khả dụng. Nếu chưa có adapter hoặc thiếu dữ liệu, phải nói **CHƯA ĐỒNG BỘ**; prompt không tự động ghi GitHub.
9. Sau khi nạp các nguồn được phép, tiếp tục **tác vụ mới nhất**; không buộc người dùng gửi thêm prompt khởi động hoặc lặp lại ngữ cảnh đã có.

## 1. Thông tin dự án

- **Tên dự án:** Chưa khởi tạo — lấy từ `PROJECT_CONFIG.json`.
- **Repository:** Chưa khởi tạo — lấy từ `PROJECT_CONFIG.json`.
- **Mục tiêu sản phẩm:** Chưa cung cấp.
- **Đối tượng sử dụng:** Chưa cung cấp.
- **Phạm vi hiện tại:** Chưa cung cấp.
- **Công nghệ:** Chưa xác minh.
- **Các nguồn thiết kế chính thức:** Chưa được chỉ định.

## 2. Kiến trúc / phụ thuộc hiện có

Chưa có dữ liệu thực tế. Cập nhật tại đây **chỉ khi được phép và có nguồn xác minh**; không sao chép mã sản phẩm hoặc lịch sử hội thoại nguyên văn.

## 3. Các ràng buộc đặc thù của dự án

Chưa có dữ liệu. Quy tắc chung thuộc `AI_PROJECT_WORKING_RULES.md`, không chép lại vào phần này.

## 4. Vị trí cần đọc khi tiếp tục

- Quy tắc: `ai-context:AI_PROJECT_WORKING_RULES.md`.
- Trạng thái: `ai-context:PROJECT_STATUS.md`.
- Kế hoạch: `ai-context:PROJECT_ROADMAP.md`.
- Quyết định: `ai-context:DECISIONS.md`.
- Dữ liệu chat: `feature/ai-project-memory:AI-Memory/MEMORY_INDEX.md`.
- Code sản phẩm: `main`, hoặc bản local người dùng cung cấp mới hơn.

## 5. Điểm dừng công việc / bàn giao

Chưa có phiên dự án. Sau các tác vụ thật, chỉ cập nhật thông tin kỹ thuật cần thiết tại đây; lịch sử từng lời chat và tool để trong nhánh bộ nhớ.

**Không có quyền mặc định:** việc đọc file này không tự cấp GitHub access, quyền commit, quyền thay đổi `main` hay khả năng thu thập hội thoại tự động.
