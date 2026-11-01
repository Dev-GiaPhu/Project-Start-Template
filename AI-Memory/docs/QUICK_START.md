# Tạo phiên, ghi sự kiện và lưu GitHub

**Điều kiện:** Python 3.11+, Git checkout nhánh `feature/ai-project-memory`, remote `origin` trỏ repository dự án thật, GitHub write permission, dữ liệu đã được phép chia sẻ. Bộ ghi không tự thu thập mọi chat nếu chưa có adapter tích hợp.

## 1. Khởi tạo đúng dự án (chỉ một lần)
```bash
git switch feature/ai-project-memory
python3 AI-Memory/tools/initialize_memory.py --repo OWNER/PROJECT --project-id project-slug --timezone UTC --approved
python3 AI-Memory/tools/validate_memory.py
git add AI-Memory/project.json
git commit -m "chore(memory): initialize archive for project"
git push origin feature/ai-project-memory
```

## 2. Ghi một lượt có dữ liệu thực
```bash
python3 AI-Memory/tools/record_cli.py new --platform codex --title "Tên phiên" --approved
# Sao chép đường dẫn in ra lệnh trên vào SESSION:
SESSION="conversations/YYYY/MM/DD/SESSION-ID"
TURN="turn-1"

python3 AI-Memory/tools/record_cli.py append --session "$SESSION" --turn-id "$TURN" --kind message.created --actor user --text-file user-message.txt --approved
python3 AI-Memory/tools/record_cli.py append --session "$SESSION" --turn-id "$TURN" --kind tool.call --actor assistant --tool-call-id c1 --json-file tool-request.json --approved
python3 AI-Memory/tools/record_cli.py append --session "$SESSION" --turn-id "$TURN" --kind tool.result --actor tool --tool-call-id c1 --json-file tool-result.json --approved
python3 AI-Memory/tools/record_cli.py attach --session "$SESSION" --turn-id "$TURN" --file attachment.pdf --approved

# Chỉ sau khi AI thực sự trả lời xong:
python3 AI-Memory/tools/record_cli.py append --session "$SESSION" --turn-id "$TURN" --kind message.completed --actor assistant --text-file assistant-final.md --approved
python3 AI-Memory/tools/commit_turn.py --session "$SESSION" --turn-id "$TURN" --approved
```

`commit_turn.py` từ chối branch/remote sai, final còn thiếu, sự kiện trộn lượt và dữ liệu không toàn vẹn; tạo commit sau khi phản hồi hoàn tất và kiểm tra SHA remote. `--no-push` chỉ dùng khi kiểm thử local: **chưa đồng bộ GitHub**.

## 3. Truy xuất, kiểm tra và khôi phục file
```bash
python3 AI-Memory/tools/validate_memory.py
python3 AI-Memory/tools/record_cli.py verify
python3 AI-Memory/tools/record_cli.py search --query "từ khóa"
python3 AI-Memory/tools/record_cli.py replay --session "$SESSION" --all
python3 AI-Memory/tools/record_cli.py restore --session "$SESSION" --sha256 "<HASH>" --output "/duong-dan-ngoai-repo/file"
```

## 4. Nhập lịch sử ChatGPT export khi được phép
```bash
python3 AI-Memory/tools/import_chatgpt.py export.zip --list
python3 AI-Memory/tools/import_chatgpt.py export.zip --conversation-id "<ID_THỰC>" --approved
```

Import là **bộ ghi một lần cho dữ liệu nguồn có sẵn**, không bảo đảm có mọi tool trace, file bytes, session edits hoặc thời gian gốc. Không commit toàn bộ ZIP xuất tài khoản hoặc chat không thuộc dự án.

## 5. Tích hợp tự động
Để thật sự có **một commit cho mỗi lượt mà người dùng không cần thao tác**, cần host/adapter có quyền đọc message và tool events, rồi gọi `commit_turn.py` sau khi nhận **assistant final**. Phần này phụ thuộc nền tảng, **chưa được bật mặc định trong template**. Ghi rõ trạng thái thiếu thay vì tuyên bố đã lưu.
