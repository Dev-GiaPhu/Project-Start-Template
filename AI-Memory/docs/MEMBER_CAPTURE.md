> **KHÔNG SỬ DỤNG — PHƯƠNG ÁN LỊCH SỬ:** Chủ dự án đã loại bỏ host/server/webhook bên ngoài. Phương án được dùng là lưu trực tiếp qua GitHub connector trong từng lượt chat có quyền. File này chỉ giữ để đối chiếu lịch sử, không phải hướng dẫn bắt buộc. Xem Rules trên ai-context, mục ưu tiên lưu trực tiếp.

# Bộ ghi host theo từng thành viên — hướng dẫn tích hợp và nghiệm thu

**Trạng thái:** Mã bộ ghi đã được đưa vào nhánh memory và đã qua các phép thử Git remote mô phỏng; **CHƯA** có ChatGPT host callback thực tế được kết nối. Không tuyên bố mọi tin nhắn trên ChatGPT hiện đang tự đồng bộ.

## Kiến trúc

- Nguồn duy nhất về thành viên/vai trò: `ai-context:TEAM/MEMBERS.json`; `member_id` dạng slug ổn định, chủ dự án có vai trò `owner`. Không dùng lời tự nhận trong chat để cấp quyền.
- Cấu hình bí mật *ngoài repository*: `AI_CAPTURE_KEYS_JSON` là JSON ánh xạ SHA-256 token -> `{"member_id":"...", "role":"owner|member"}`. Host cấp token ngẫu nhiên tối thiểu 32 ký tự và đặt trong `AI_CAPTURE_TOKEN`. Không commit token hoặc digest vào repo.
- Bộ ghi nằm tại `AI-Memory/tools/member_capture.py`, cổng nội bộ `AI-Memory/tools/host_gateway.py`. Chỉ một Git checkout/worker ghi tại một thời điểm; nhiều máy cùng lúc cần hàng đợi tập trung và xử lý tranh chấp Git trước khi sản xuất.
- Nhật ký mới: `AI-Memory/members/<member_id>/conversations/YYYY/MM/DD/<session-id>/`. Chỉ mục riêng: `members/<member_id>/indexes/{capture,sessions}.json`; file gốc theo hash trong `members/<member_id>/objects/`. Lịch sử cũ ở `AI-Memory/conversations/` không tự phân loại lại; giữ nguyên và tra dưới dạng `unattributed`.
- Một `message.created` của user và một `message.completed` đã phát hành của assistant là **hai commit riêng**, ngay khi host thực sự cung cấp từng event. Tool/UI/attachment ghi theo event quan sát được. Kiểm `ls-remote` SHA sau khi push không force. Từ chối `message.completed` nếu không có `published: true`.
- `ai-context` chứa GDD chung, phân công và tiến độ. **Không đưa log chat vào GDD hay Project Context**, không đưa tài liệu AI vào `main`.

## Thiết lập trên máy host / server được ủy quyền

1. Xác định chủ dự án và các member thật sự, kích hoạt họ trong `ai-context:TEAM/MEMBERS.json`. Một GitHub login trên repo không tự chứng minh danh tính phiên ChatGPT.
2. Dùng clone riêng có đủ hai nhánh, giữ checkout tại `feature/ai-project-memory`; xác nhận `git show ai-context:TEAM/MEMBERS.json` đọc được roster mới nhất và `git push origin feature/ai-project-memory` có quyền. Máy host phải có Git identity và credential riêng, không đưa token vào transcript.
3. Tạo secret token ngẫu nhiên (tối thiểu 32 ký tự) cho từng thành viên. Lưu SHA-256(token) và mapping member_id/role trong secret config `AI_CAPTURE_KEYS_JSON` trên host; token gốc chỉ host/client tin cậy giữ. Không nhận dạng member từ `member_id` do client gửi.
4. Nếu host hỗ trợ gọi CLI trên từng callback, đặt JSON vào stdin và gọi:
   `python3 AI-Memory/tools/member_capture.py --payload-file -`.
   Nếu host chỉ hỗ trợ HTTP, chạy `python3 AI-Memory/tools/host_gateway.py` trong môi trường có secret; POST nội bộ `http://127.0.0.1:8765/v1/events`, header `Authorization: Bearer <token>`. Chỉ public qua HTTPS reverse proxy đã bảo vệ; không expose HTTP thô.
5. **Trước khi gửi bản bàn giao đầu tiên**, host phải đăng ký callback khi user message vừa đến và callback assistant final sau khi được phát hành. Cũng cần callback tool/file/UI nếu muốn ghi các loại đó. Không có hook ChatGPT chính thức tích hợp sẵn chỉ bằng việc cài repository này.
6. Gửi bản bàn giao **thử nghiệm** qua host. Sau khi nhận HTTP/CLI status `synced`, kiểm SHA trên remote và nội dung đúng thư mục member. Gửi lại cùng `message_id` phải trả `duplicate`, không tạo commit mới. Kiểm member khác không thể ghi chéo. Gửi assistant final phải là commit thứ hai. Chỉ khi kiểm thử qua host thật hoàn tất mới bật cờ sẵn sàng.

## Event JSON do host cung cấp

```json
{
  "kind": "message.created",
  "message_id": "host-message-0001",
  "conversation_id": "host-conversation-abc",
  "actor": "user",
  "text": "Bản bàn giao đầu tiên",
  "turn_id": "turn-001",
  "title": "Bàn giao dự án",
  "source_complete": true
}
```

Khi final đã được phát hành, host gửi event mới với `kind=message.completed`, `actor=assistant`, `published=true`, `message_id` thật và `conversation_id` giữ nguyên. Không được gửi `published=true` trước khi phát hành hoặc tự dựng transcript/sự kiện. `occurred_at` chỉ điền nếu nguồn cung cấp thời gian có múi giờ thật. `attachments` tùy chọn: các mục `{"name":"file.png","base64":"..."}` tối đa 8 MiB/tệp và 16 tệp/event. Lọc dữ liệu bí mật và chỉ lưu tệp được phép trước khi đưa tới host.

## Điều kiện nghiệm thu

- Host đã xác thực owner/member và không nhầm bộ nhớ.
- Tạo và push hai commit riêng cho user message, assistant final từ nguồn có thật; mỗi lần xác minh remote SHA.
- Bản bàn giao đầu tiên được ghi **trước khi AI xử lý phần tiếp theo** khi host hỗ trợ và có mạng.
- Các thao tác tool/tệp được ghi đúng mức host thực sự cung cấp; chỗ thiếu đánh dấu `partial`, không bịa.
- Token sai/giả mạo role hoặc ghi chéo member đều bị từ chối; nhân đôi message không tạo commit mới.
- Không thay đổi `main`; không đồng nhất quyền xem thư mục với bảo mật: thành viên có quyền đọc cùng GitHub repo có thể xem tất cả transcript. Cần repo riêng nếu phải phân quyền truy cập dữ liệu cứng.

**Chưa nghiệm thu:** Việc ChatGPT trên giao diện hiện tại tự gọi webhook/CLI. Việc đó đòi hỏi triển khai host/adapter được phép, không thể kích hoạt bằng prompt hoặc GitHub connector thuần.
