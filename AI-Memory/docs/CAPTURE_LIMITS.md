# Giới hạn nền tảng và quyền riêng tư

- **Không có hook mặc định** để bắt mọi tin nhắn và mọi thao tác trong ChatGPT chính thức chỉ bằng prompt hoặc GitHub connector. Bộ ghi event chỉ nhận được những gì adapter/host hoặc export cung cấp.
- Với Codex hoặc hệ thống có SDK/host app, có thể xây adapter lắng nghe tool events và final; **template chưa đi kèm adapter tự hoạt động 24/7**.
- Không được lưu hidden chain-of-thought, thông điệp hệ thống riêng tư, bí mật, cookie, token hoặc nội dung cá nhân chưa được phép chia sẻ.
- Bản export ChatGPT có thể chỉ chứa biểu diễn message, không có binary tệp gốc hoặc mọi sự kiện UI/tool. Phải đánh dấu thiếu, không bịa.
- GitHub không vô hạn dung lượng hay quota. Kho archive chia file/chunk 8 MiB để hạn chế kích thước đối tượng Git nhưng không bảo đảm chứa vô hạn dữ liệu.
- Khi dự án sử dụng private repo, quyền đọc GitHub áp dụng theo **repository**, không phải theo nhánh. Có nhóm cần phân quyền riêng thì tạo repository private bộ nhớ khác.
