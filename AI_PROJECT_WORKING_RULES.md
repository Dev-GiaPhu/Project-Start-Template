# AI PROJECT WORKING RULES — Quy tắc chung cho mọi dự án

**Nguồn duy nhất cho quy tắc AI.** Không sao chép các điều luật dưới đây vào Context, Roadmap, GDD hoặc nhánh bộ nhớ. Quy định có hiệu lực theo phạm vi công việc; không phải lệnh để truy cập dữ liệu chưa được cấp quyền.

## 1. Nguyên tắc làm việc
- Đáp ứng đúng yêu cầu, ưu tiên dữ kiện kiểm chứng. Trước khi thay đổi file hãy xem phiên bản mới, các phụ thuộc và tác động.
- Phân biệt `ĐÃ YÊU CẦU`, `ĐÃ ĐỀ XUẤT`, `ĐÃ VIẾT`, `ĐÃ COMMIT`, `ĐÃ TEST THỰC TẾ`, `ĐÃ ĐƯỢC XÁC NHẬN` và `CHƯA BIẾT`. Không coi đề xuất là quyết định.
- Dùng tiếng Việt rõ nghĩa khi làm việc với chủ dự án, trừ khi người dùng yêu cầu ngôn ngữ khác. Không tạo câu hỏi hoặc checklist kéo dài khi nhiệm vụ đã đủ rõ.
- Không giả định nội dung dự án khác; mọi file template chỉ chứa khung, không phải trạng thái thật.
- Giữ nguyên API, tham chiếu, chức năng đang chạy; không làm lại một hệ thống chỉ vì thấy mã trên GitHub khác bản local.

## 2. CẤU TRÚC BA NHÁNH — QUY TẮC TỐI CAO
| Nhánh | Nội dung duy nhất | Không được đặt |
| --- | --- | --- |
| `main` | Code, tài nguyên và tài liệu **sản phẩm thật sự cần để build/chạy/phát hành** | Prompt, nhật ký AI, `AGENTS.md` nội bộ, Rules, GDD nội bộ AI, Memory, bộ ghi chat |
| `ai-context` | GDD/thiết kế nếu phù hợp, quy tắc, Context, tiến độ, Roadmap, quyết định, bàn giao | Code sản phẩm, transcript thô, file upload chat, tool trace |
| `feature/ai-project-memory` | Dòng event nguyên gốc, tin nhắn, tool actions, tệp, metadata, chỉ mục và công cụ ghi/truy xuất | Bản sao GDD, Rules, Context, Roadmap hoặc quyết định chuẩn |

- **Không được đưa bất kỳ file hoặc công cụ chỉ phục vụ vận hành AI lên `main`**, kể cả nếu ai đó yêu cầu đồng bộ hay merge. Không tự merge/cherry-pick/rebase nhánh AI sang `main`.
- Việc sửa **code sản phẩm thật trên `main`** là trường hợp riêng: yêu cầu xác nhận chặt chẽ trước khi ghi, gồm repository, nhánh, file, thay đổi dự kiến, kiểm thử/rủi ro và quyền thao tác. Không suy ra quyền đó từ việc có GitHub connector.
- Không force-push, viết lại lịch sử, xóa dữ liệu, thay đổi default branch hoặc dọn nhánh mà chưa được chủ dự án cho phép **rõ ràng theo từng việc**.
- Một GitHub repository **không có phân quyền đọc theo nhánh/thư mục**. Nếu các thành viên phải được tách quyền hoàn toàn, chọn một private repository riêng cho nhóm/dự án thay vì coi nhánh riêng là ranh giới bảo mật.
- Trước commit phải đọc HEAD của nhánh được phép, kiểm diff file, giữ SHA dự kiến; sau commit kiểm đích và đảm bảo nhánh bị cấm không thay đổi.

## 3. Quyền và nguyên tắc an toàn dữ liệu
- **Mặc định chỉ đọc.** Chỉ tạo/sửa/commit đúng repository, nhánh và file đã được cấp phép, không dùng quyền dự án A cho dự án B.
- Không ghi secrets, token, cookies, mật khẩu, khóa bí mật, dữ liệu nhạy cảm hoặc thông tin riêng tư chưa có quyền chia sẻ lên repository, kể cả private.
- Không tự lưu private chain-of-thought, hidden messages hoặc dữ liệu mà nền tảng không cung cấp. Không khẳng định đã thấy phần không được truy cập.
- Không tạo bản transcript giả, không thay việc thiếu log bằng diễn giải tự sinh. `capture.gap` mô tả chính xác phần không thu thập được.

## 4. Nguồn sự thật và không nhân bản
- **Thiết kế được duyệt** → GDD/spec chính thức trên `ai-context` nếu dự án có tài liệu này.
- **Ngữ cảnh kỹ thuật ổn định** → `PROJECT_CONTEXT.md`; **trạng thái hiện hành/kiểm thử** → `PROJECT_STATUS.md`; **dự kiến tương lai** → `PROJECT_ROADMAP.md`; **quyết định đã chốt** → `DECISIONS.md`.
- **Tin nhắn, thao tác tool và tệp của từng lượt** → nhánh memory; tài liệu Context chỉ **tham chiếu event/commit** khi thật sự cần.
- Khi mâu thuẫn, ưu tiên chỉ đạo trực tiếp mới nhất của chủ dự án trong phạm vi an toàn, quyết định nguồn chính thức mới nhất, mã thực người dùng cung cấp, rồi tới mã đã commit. **Báo khác biệt giữa code hiện tại và GDD**, không tự hợp nhất.
- Chỉ cập nhật docs khi có thay đổi nội dung thực sự; không commit các bản sao tóm tắt mỗi lượt vào `ai-context`.

## 5. MÃ NGUỒN & KIỂM THỬ
- Khi được yêu cầu viết/sửa code, xem file gốc và các thành phần tương tác trước. Ưu tiên gửi **file hoàn chỉnh**, không chỉ một đoạn patch khi người dùng cần thay nguyên file.
- Giữ chú thích có giá trị. Giải thích các khối xử lý quan trọng bằng tiếng Việt; mô tả thiết lập, đơn vị, tham chiếu và giới hạn của trường cấu hình/editor theo ngôn ngữ dễ hiểu. Đối với môi trường có Inspector, **các trường Inspector được sửa phải có Tooltip tiếng Việt chi tiết**; tùy project mà áp dụng hướng dẫn editor tương đương.
- Không xóa API/tính năng đang hoạt động hay chèn component/manager mới trùng chức năng mà chưa kiểm tra hệ thống hiện có.
- Chỉ nói đã compile/test nếu có công cụ hoặc người dùng xác nhận cụ thể; nêu rõ phạm vi kiểm thử, điều chưa chạy và rủi ro.
- Khi người dùng xác nhận một milestone code **chạy đúng và chưa commit**, nhắc họ checkpoint **ở đầu câu trả lời**, đề xuất commit message mô tả phần hoàn thành. Đây là **commit sản phẩm do chủ dự án quản lý**, khác với memory commit theo lượt; AI không tự commit gameplay nếu không có quyền riêng.

## 6. GDD và thiết kế (áp dụng khi dự án là game)
- Đọc GDD thật trước thiết kế/roadmap/cơ chế game. `templates/GAME_DESIGN_DOCUMENT.template.md` là file rỗng, không phải GDD đã duyệt.
- Phân biệt đã chốt, ý tưởng đang cân nhắc, đề xuất AI, code đã chạy, chưa chốt. Khi người dùng mô tả cơ chế, mục tiêu, phong cách, giới hạn, ghi nhận đúng nguồn và cập nhật GDD nếu có quyền.
- Một câu hỏi thiết kế thật sự hữu ích mỗi lượt khi cần; cho phép lựa chọn khác/ghi chú nếu dùng lựa chọn. Không liên tục hỏi khi đang xử lý tác vụ rõ ràng.
- Không biến việc duyệt khung GDD thành xác nhận tính năng đã triển khai/test; tránh scope creep và áp đặt số liệu cân bằng.

## 7. MỖI LƯỢT CHAT = MỘT COMMIT BỘ NHỚ (KHI CÓ RECORDER)
- **Đơn vị event:** mỗi thông điệp, thao tác tool, kết quả, lỗi, thay đổi file, UI payload hoặc tệp có nguồn và thời gian quan sát được được ghi dưới `turn_id`.
- **Đơn vị commit:** một user message + tất cả thao tác được phép ghi + **assistant final sau khi đã hoàn tất** = **đúng một commit trên nhánh memory**. Không commit riêng user message, không gộp các lượt, không commit khi final chưa có.
- Kiểm quyền chia sẻ, checksum SHA-256, kết quả tool, nhánh/remote, diff, tệp nhạy cảm; push non-force; chỉ báo **ĐÃ ĐỒNG BỘ** nếu xác minh SHA trên remote. Nếu thiếu dữ liệu hoặc adapter, báo **CHƯA ĐỒNG BỘ**.
- ChatGPT chính thức **không tự động xuất mọi sự kiện cho prompt**; muốn auto-commit sau câu trả lời cần host/recorder có quyền nhận final. Codex/host có thể tích hợp nếu nền tảng cung cấp event. Không được hứa đã tự hoạt động chỉ nhờ cài file Rules.
- Khi bắt đầu chat mới, đọc `PROJECT_CONTEXT.md` và các nguồn trên `ai-context`; tra `AI-Memory/MEMORY_INDEX.md` và event gốc ở nhánh memory. Nạp theo phần nếu quá giới hạn ngữ cảnh, không khẳng định đã hiểu 100% lịch sử khi dữ liệu thiếu.

## 8. BÀN GIAO & TÁI SỬ DỤNG
- **Một file bàn giao duy nhất: `ai-context/PROJECT_CONTEXT.md`**; người dùng không phải viết thêm prompt. Nó tự dẫn đến Rules, Status, Roadmap, Decisions và Memory.
- Khởi tạo mỗi dự án mới từ template bằng `Include all branches`. Không mang dữ liệu riêng của dự án cũ vào template hay dự án mới.
- Khi thay đổi luật, **chỉ** sửa file này trên `ai-context`; không lưu thêm bản Rules ở nhánh bộ nhớ.
- Nếu thiếu công cụ/permission để ghi, nói rõ, chỉ cung cấp nội dung chờ cập nhật. Không gọi thao tác chưa hoàn thành là đã đồng bộ.
