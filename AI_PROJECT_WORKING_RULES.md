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

## 7. TỪNG TIN NHẮN = MỘT COMMIT RIÊNG KHI CÓ HOST/RECORDER (ĐÃ ĐƯỢC CHỦ DỰ ÁN PHÊ DUYỆT 02/11/2026)
- Ngay khi host xác thực và quan sát được tin nhắn người dùng, ghi `message.created` nguyên gốc, commit/push riêng và xác minh SHA remote; **không đợi assistant final**.
- Khi host xác nhận phản hồi AI cuối **đã phát hành**, ghi `message.completed` thành commit riêng. Bản nháp chỉ là `message.prepared`, không giả mạo completed.
- Tool, tệp và UI ghi theo sự kiện có thật, theo nguồn/hạn mức/quyền chia sẻ; có thể là commit riêng. Giữ `turn_id`, `message_id`, `session_id`, thứ tự và checksum, chống trùng lặp.
- Dữ liệu mới tách theo `member_id` tin cậy; lịch sử không rõ tác giả giữ `unattributed`, không tự gán sai. Nhận diện owner/member dựa trên roster chính thức và credential host, không từ văn bản chat.
- Bộ ghi trong `AI-Memory/tools/member_capture.py` có gateway nội bộ `host_gateway.py`; chỉ được tuyên bố **ĐÃ ĐỒNG BỘ** sau khi remote SHA xác minh. GitHub connector, prompt hoặc việc có script **không tự cung cấp hook ChatGPT**. Muốn có dữ liệu ngay từ tin bàn giao đầu tiên, host phải chạy và test *trước khi* gửi.
- `AI-Memory/tools/commit_turn.py` là công cụ **legacy**, không còn là chính sách mặc định; không cần xóa log cũ hay rewrite lịch sử để chuyển đổi. Quy tắc quyền ghi, bảo vệ `main`, dữ liệu nhạy cảm và chủ dự án duyệt thay đổi lớn vẫn giữ nguyên.

## 7A. ƯU TIÊN LƯU TRỰC TIẾP BẰNG GITHUB CONNECTOR — KHÔNG DỰNG HOST MỚI (ĐÍNH CHÍNH 02/11/2026)

**Chỉ đạo mới nhất của chủ dự án:** Không sử dụng host/server/webhook/adapter/dịch vụ thứ ba bổ sung để ghi chat. Khi kết nối GitHub sẵn có và quyền ghi hợp lệ, **AI trong chính lượt chat này trực tiếp lưu nguyên văn thông điệp user ngay khi thấy và có thể ghi**, sau đó lưu văn bản phản hồi AI thực sự chuẩn bị gửi. Không làm phức tạp hệ thống lưu chỉ hai chiều hỏi/đáp.

- **Ưu tiên thực hành ngay:** Vừa nhận file bàn giao đầu tiên, tự nạp chính xác project/nhánh và kiểm tra quyền; khi hợp lệ ghi user message ngay qua GitHub, rồi đọc GDD/Context liên quan, soạn và ghi phản hồi AI đã chuẩn bị. Ghi đúng repository, nhánh `feature/ai-project-memory`; không ghi `main`, `ai-context` hay nhánh của dự án khác. Không tự tạo thành viên/owner cho tin nhắn chưa được xác thực. Mỗi tin nhắn có nhãn user/assistant, ngày/ID có nguồn, quan hệ và trạng thái.
- **Độ trung thực:** Tin nhắn user nhìn thấy được có thể lưu `message.created`; phản hồi AI được commit trước khi phát hành chỉ ghi `message.prepared` (và giữ nguyên văn nội dung dự kiến phát hành), **không** giả có callback `message.completed`. Chỉ báo đã lưu sau khi commit/push và xác minh SHA trên GitHub. Khi thiếu dữ liệu nguồn, ghi `partial`, tuyệt đối không bịa metadata hay lịch sử.
- **Không tự chạy nền:** GitHub connector cho AI làm việc trong cuộc chat đang xử lý, **không tự lắng nghe các chat/lượt mới, không đảm bảo nhận phản hồi sau final, không tạo thông báo ở chat chưa mở**. Khi chat mới được mở và file bàn giao được nạp lại, AI thực hiện quy trình trực tiếp từ đầu. Không quảng cáo `automatic_chat_capture=true` nếu chưa có khả năng nền tảng thật.
- **Không sử dụng kiến trúc bổ sung:** Các file thử nghiệm `AI-Memory/tools/member_capture.py`, `host_gateway.py` và `docs/MEMBER_CAPTURE.md` trước đây không nằm trong luồng được yêu cầu; **không khởi chạy hoặc đòi cấu hình chúng**. Chỉ dọn bỏ sau khi có quyền/xác nhận riêng về file và dữ liệu để tránh xóa nhầm.
- **Ưu tiên lời sửa mới:** Điều khoản này thay thế mọi đề xuất trước đó bắt buộc cài host/adapter trước khi có thể lưu nội dung chat bằng GitHub connector. Không thay đổi quy tắc bảo vệ `main`, bảo mật, phân quyền member và owner-only approval.

## 8. BÀN GIAO & TÁI SỬ DỤNG
- **Một file bàn giao duy nhất: `ai-context/PROJECT_CONTEXT.md`**; người dùng không phải viết thêm prompt. Nó tự dẫn đến Rules, Status, Roadmap, Decisions và Memory.
- Khởi tạo mỗi dự án mới từ template bằng `Include all branches`. Không mang dữ liệu riêng của dự án cũ vào template hay dự án mới.
- Khi thay đổi luật, **chỉ** sửa file này trên `ai-context`; không lưu thêm bản Rules ở nhánh bộ nhớ.
- Nếu thiếu công cụ/permission để ghi, nói rõ, chỉ cung cấp nội dung chờ cập nhật. Không gọi thao tác chưa hoàn thành là đã đồng bộ.

## 9. TỰ CẬP NHẬT QUY TẮC, PHÂN QUYỀN DUYỆT VÀ CẢNH BÁO CHỦ DỰ ÁN

**Lệnh của chủ dự án (02/11/2026):** Mỗi thành viên làm việc theo hồ sơ riêng nhưng cùng hướng GDD. AI có thể tự bổ sung, sửa lỗi quy tắc/cách làm việc nhỏ, rõ ràng; thay đổi lớn, đụng quyền, bảo mật, cấu trúc hoặc mâu thuẫn phải trình **chủ dự án**, không xin duyệt từ member. Khi chủ dự án mở cuộc trò chuyện tiếp theo và nguồn bàn giao được nạp, phải báo việc còn chờ duyệt dù chủ dự án không hỏi.

1. **Xác thực vai trò:** `owner` và `member` là định danh vai trò được cấu hình/xác minh; không suy ra từ cách xưng hô, tên chat, GitHub connector đang kết nối hoặc tuyên bố tự nhận. Khi chưa xác định được người chat, không coi là owner để phê duyệt thay đổi lớn. `member_id` phải ổn định; dữ liệu không rõ người gửi giữ `unattributed`, không đoán và không gán nhầm.
2. **Tự cập nhật nhỏ được phép:** Sửa lỗi chính tả, tham chiếu hỏng, hướng dẫn thiếu bước không tranh cãi, lỗi kiểm tra/cảnh báo hiển nhiên, bổ sung ví dụ hoặc bảo vệ chống hiểu nhầm, miễn là **không thay đổi quyền, thiết kế đã chốt, cấu trúc dữ liệu, cách ghi bộ nhớ, lịch sử cũ, phạm vi công việc, logic gameplay hoặc độ ưu tiên của quy tắc**. Chỉ sửa file được ủy quyền trên `ai-context`, đọc SHA/diff trước, xác minh commit và thông báo rõ thay đổi; không âm thầm mở rộng quyền ghi.
3. **Bắt buộc duyệt bởi owner:** Thay đổi nhánh/repository/quyền, mô hình nhận diện thành viên, quyền riêng tư, quyền chia sẻ, schema/đường dẫn/kho bộ nhớ, chính sách per-message/per-turn, bộ ghi tự động, workflow ghi/push, đổi GDD, phân chia công việc lớn, tiến độ chung hoặc bất cứ điểm nào mâu thuẫn giữa nguồn chính thức là thay đổi lớn. Không tự triển khai, không xin member quyết định, không dùng xác nhận của member làm phê duyệt của owner. Chuẩn bị phương án, lợi/hại, file/nhánh chịu tác động và đưa vào mục chờ duyệt trong hồ sơ bàn giao chính thức của dự án.
4. **Báo ở cuộc trò chuyện owner kế tiếp:** Khi nạp file bàn giao/khởi động phiên mới, **trước khi trả lời công việc khác** hãy kiểm tra danh sách vấn đề chờ owner ở Project Context. Nếu có và người chat được xác minh là owner, chủ động nêu rõ các vấn đề còn mở dù không được nhắc lại; chỉ owner mới được chốt. Nếu là member, tiếp tục việc trong quyền, không yêu cầu member phê duyệt; không làm lộ thông tin riêng tư vượt quyền. AI không được tuyên bố có thể chủ động gửi thông báo vào một chat chưa mở hoặc theo dõi các chat khác nếu không có host/adapter thực sự.
5. **Bộ nhớ phải hoạt động thật từ lần bàn giao đầu tiên:** Quy trình tiếp nhận phải kiểm tra `project_id`, GDD/Rules/Context, vai trò thành viên, nhánh bộ nhớ, schema, chỉ mục và **trạng thái adapter/hook ghi dữ liệu thực tế**. Ngay khi có quyền và bộ ghi hoạt động, ghi sự kiện bàn giao đầu tiên theo chính sách commit đã được owner duyệt, kiểm chứng push/SHA. Nếu thiếu adapter, nhận diện, quyền, hoặc không thu được phản hồi AI cuối thì ghi/chỉ rõ `CHƯA HOẠT ĐỘNG/CHƯA ĐỒNG BỘ` và phạm vi thiếu; **không coi prompt, bộ script CLI hoặc cấu trúc thư mục là bằng chứng tự động ghi mọi cuộc chat**. Muốn thực sự tự ghi từ tin nhắn đầu, host/adapter và phép thử end-to-end phải sẵn sàng **trước** khi tin nhắn bàn giao đó được gửi.
6. **Kiểm thử nghiệm thu trước khi tuyên bố sẵn sàng:** Cần xác nhận nhận diện owner/member đúng, không trộn lịch sử thành viên, nạp GDD chung, ghi user message và assistant final có thật, khôi phục đúng session, xử lý trùng lặp, bảo vệ tệp nhạy cảm, lưu khi thất bại và không tác động `main`. Tất cả mục bắt buộc phải có bằng chứng; chưa test là chưa hoàn thành.
