# PROJECT CONTEXT — TỰ TIẾP NHẬN DỰ ÁN KHI BẮT ĐẦU CHAT MỚI

## HỘP THƯ CHỜ CHỦ DỰ ÁN — ĐỌC NGAY KHI NHẬN FILE BÀN GIAO (02/11/2026)

Đây là **mẫu quản trị chung**; không được gán tiến độ, thành viên hoặc dữ liệu Zimbo.exe cho dự án mới. Khi đã khởi tạo repo mới, AI phải kiểm tra các vấn đề chờ owner trong Project Context dự án đó ngay từ chat đầu; nếu xác thực người chat là owner thì chủ động báo dù không được nhắc, còn member không có quyền phê duyệt. Chỉ thay đổi nhỏ không mâu thuẫn mới được tự cập nhật theo `AI_PROJECT_WORKING_RULES.md` §9.

- **TEMPLATE-OWNER-001 — ĐÃ ĐƯỢC OWNER ĐÍNH CHÍNH 02/11/2026:** Quy tắc đã chuyển sang mỗi tin nhắn một commit; **không triển khai host/webhook/dịch vụ bên thứ ba**. Ưu tiên dùng GitHub connector trực tiếp trong chat. Không tuyên bố tự động lưu mọi chat hoặc lưu assistant final đã được phát hành nếu nền tảng không cung cấp sự kiện.
- **MỌI DỰ ÁN MỚI — CẦN KIỂM TRA LÚC TIẾP NHẬN:** Từ file bàn giao đầu tiên, thử ghi trực tiếp user message vào đúng nhánh bộ nhớ qua GitHub connector, xác minh SHA; lưu nội dung AI đã soạn với `message.prepared`. Nếu chưa có quyền hoặc công cụ thì báo rõ CHƯA ĐỒNG BỘ, không yêu cầu host bổ sung. Định danh member chưa rõ thì giữ `unattributed`.

Khi giải quyết xong yêu cầu template, đánh dấu quyết định và trạng thái kiểm thử có nguồn; không chép nguyên vấn đề của template thành việc còn chờ của từng dự án mới nếu đã giải quyết.


> **ĐÂY LÀ FILE BÀN GIAO DUY NHẤT.** Khi người dùng tải lên hoặc gửi riêng file này, hãy coi đó là yêu cầu tiếp nhận dự án. **Không yêu cầu họ soạn thêm prompt.** Phần thông tin chưa được khởi tạo phải được báo thiếu, không được suy đoán.

## KHỞI TẠO DỰ ÁN MỚI — CHỈ CẦN GỬI FILE NÀY

**LỆNH GỬI TỚI AI Ở CHAT MỚI:** Nếu `PROJECT_CONFIG.json` thuộc repo template có `initialized=false`, hãy chuyển vào **chế độ tạo dự án**. File này đã là prompt hoàn chỉnh. Không yêu cầu người dùng soạn thêm văn bản, tạo repo trước hoặc chạy lệnh thủ công nếu AI có công cụ và quyền thích hợp. Nếu đang nhận file đã khởi tạo của một dự án thật, sử dụng §0 phía dưới để tiếp tục công việc, không hỏi tên lại.

**Nguồn mẫu cố định:** https://github.com/Dev-GiaPhu/Project-Start-Template — chỉ lấy cấu trúc, tuyệt đối không ghi thông tin của game mới vào repository template.

### 1. Chủ động hỏi để thiết lập
- **Câu hỏi đầu tiên:** “Bạn muốn đặt tên game mới là gì?” (Nếu người dùng làm dự án khác game thì hỏi tên dự án.) Nếu tên đã được cung cấp, đừng hỏi lại.
- Tiếp theo xác định các thông tin thật sự cần để tạo repository: **GitHub owner**, **tên repository/slug** (đề xuất từ tên game), và **riêng tư/công khai** (**mặc định Private**). Chỉ hỏi phần chưa rõ; tránh biểu mẫu dài.
- Có thể hỏi game engine, công nghệ, mục tiêu, 2D/3D, nền tảng, timezone sau đó để điền Context/GDD; thông tin chưa chốt giữ trống, **không cản việc tạo repo**.
- Trước khi tạo thật, tóm lược `OWNER/REPOSITORY`, Private/Public, template gốc, dự kiến ba nhánh và yêu cầu xác nhận nếu người dùng chưa cấp quyền tạo repo cụ thể.

### 2. AI tự tạo repository khi có quyền
1. Xác minh kết nối GitHub có quyền **tạo repository từ template**, repo đích chưa tồn tại và repo nguồn đã bật **Template repository**.
2. Ưu tiên công cụ kết nối GitHub có chức năng tạo từ template. Nếu có GitHub CLI hoặc REST API được phép, dùng GitHub generate repository API **`POST /repos/Dev-GiaPhu/Project-Start-Template/generate`** với `owner`, `name`, `private:true` (trừ khi user chọn Public) và **`include_all_branches:true`**. Không in/ghi token vào file hoặc chat.
3. Kiểm tra ba nhánh đã được tạo trong **repository mới**:
   - `main`: chỉ sản phẩm thật; **không ghi bất kỳ tài liệu, công cụ hay bộ nhớ chuyên dụng AI**.
   - `ai-context`: Rules, Context, Status, Roadmap, Decisions và tài liệu thiết kế/GDD chính thức khi có.
   - `feature/ai-project-memory`: transcript, thao tác công cụ, tệp và hệ thống lưu/truy xuất sự kiện.
4. Nếu thiếu nhánh AI, khôi phục **đúng nhánh AI** khi có công cụ và quyền; **không bao giờ chữa lỗi bằng cách đưa dữ liệu AI vào `main`**.
5. Khởi tạo định danh dự án theo `docs/NEW_PROJECT_SETUP.md` của repo mới. Trên `ai-context` điền `PROJECT_CONFIG.json`, `PROJECT_CONTEXT.md`, `PROJECT_STATUS.md`; trên nhánh bộ nhớ điền `AI-Memory/project.json`. Sử dụng **tên/ID/repo mới**, không mang dữ liệu của game khác sang. Xác minh công cụ recorder lấy đúng cấu hình.
6. Commit/push những file khởi tạo đã được phép **trên từng nhánh AI**; kiểm lại URL, trạng thái riêng tư, SHA và `main` không thay đổi. Nêu rõ những gì đã hoàn thành, không tự dựng nhật ký chat, GDD hoặc tiến độ.
7. **Nếu công cụ không thể tạo repository:** thông báo rõ giới hạn, không giả vờ tạo thành công. Nếu template chưa bật, hướng dẫn chủ repo bật `Settings → General → Template repository`; nếu AI không có công cụ tạo repo thì cung cấp https://github.com/Dev-GiaPhu/Project-Start-Template/generate và hướng dẫn chọn **Include all branches**, sau đó AI tiếp tục khởi tạo mọi bước mà công cụ cho phép. Không tự động chuyển sang ghi code ở main.

### 3. Sau khi tạo
- File bàn giao duy nhất từ nay là **`ai-context/PROJECT_CONTEXT.md` trong repository dự án mới**, không phải file trong repository template gốc.
- Tự động nạp GDD (nếu có), Rules, Status, Decisions và những sự kiện bộ nhớ đã thực sự lưu khi chuyển chat sau này.
- Mục tiêu bộ nhớ là **mỗi lượt user + câu trả lời AI cuối + các thao tác có thể quan sát = đúng một commit** trên nhánh bộ nhớ sau khi final. **Không tuyên bố cơ chế tự ghi đã hoạt động nếu host/adapter chưa thể thu thập phản hồi sau final.**
- Không đưa dữ liệu của bất kỳ dự án cũ nào vào dự án mới; không sửa hoặc merge file chuyên dụng AI vào `main`.

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
