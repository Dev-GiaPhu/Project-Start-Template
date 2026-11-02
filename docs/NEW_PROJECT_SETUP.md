# BẮT ĐẦU MỘT DỰ ÁN MỚI TỪ TEMPLATE

## 0. Tạo dự án bằng **một file duy nhất** (cách sử dụng ưu tiên)

- Trong chat mới, người dùng chỉ cần **gửi `ai-context/PROJECT_CONTEXT.md` từ repository template**; không cần viết prompt.
- AI sẽ **hỏi tên game đầu tiên**, rồi hỏi đúng những thông tin tạo repo còn thiếu như owner, slug và Private/Public (mặc định Private).
- AI kiểm tra quyền GitHub và tạo repository trực tiếp từ template **với `include_all_branches=true`** nếu công cụ hỗ trợ và người dùng đã xác nhận.
- AI tự khởi tạo cấu hình trên `ai-context` và `feature/ai-project-memory` của repo mới; không đưa file AI lên `main`. Không yêu cầu người dùng làm thay những bước mà AI thực sự có công cụ thực hiện.
- Nếu chưa có quyền/tính năng tạo repo, AI giải thích đúng trở ngại, cung cấp liên kết GitHub tạo từ template để người dùng thực hiện riêng bước đó và tiếp tục hỗ trợ khởi tạo.
- **Đừng hứa tự ghi mọi cuộc chat:** một file hướng dẫn không thay được bộ ghi thu thập phản hồi sau final.

## 1. Tạo repository
1. Chủ template bật **Settings → General → Template repository** trên repository nguồn (bước quản trị làm một lần).
2. Vào repository mẫu → **Use this template → Create a new repository**.
3. **BẮT BUỘC chọn `Include all branches`**, nếu không GitHub chỉ sao chép `main`, khiến `ai-context` và nhánh bộ nhớ không tồn tại.
4. Đặt tên repo dự án mới, nên chọn **Private** nếu trao đổi/tệp nhóm không công khai. Không fork và không merge ba nhánh.
5. Xác minh đúng ba branch: `main`, `ai-context`, `feature/ai-project-memory`.

**Lưu ý:** Những nhánh tạo từ GitHub Template có lịch sử không liên quan nhau; không mở PR/merge giữa các nhánh để chuyển AI docs vào `main`.

## 2. Điền định danh thật vào đúng nhánh (dùng local git hoặc AI có quyền)
```bash
git clone https://github.com/OWNER/NEW_PROJECT.git
cd NEW_PROJECT
git fetch origin
git switch ai-context
python3 tools/initialize_context.py --repo OWNER/NEW_PROJECT --project-id new-project-id --name "Tên dự án" --type software --timezone UTC --approved
python3 tools/validate_context.py
git add PROJECT_CONFIG.json PROJECT_CONTEXT.md PROJECT_STATUS.md
git commit -m "docs(context): initialize project identity"
git push origin ai-context
git switch feature/ai-project-memory
python3 AI-Memory/tools/initialize_memory.py --repo OWNER/NEW_PROJECT --project-id new-project-id --timezone UTC --approved
python3 AI-Memory/tools/validate_memory.py
git add AI-Memory/project.json
git commit -m "chore(memory): initialize project archive identity"
git push origin feature/ai-project-memory
git switch main
```

Ở bước này **`main` không bị thêm tài liệu AI**. Chỉ commit đúng file config của từng nhánh; không tự commit những file code khác.

## 3. Chốt ngữ cảnh dự án
1. Trên `ai-context`, mô tả mục tiêu/công nghệ/phụ thuộc **có thật** vào `PROJECT_CONTEXT.md`.
2. Điền `PROJECT_STATUS.md`, `PROJECT_ROADMAP.md`, `DECISIONS.md` đúng nguồn, không bịa.
3. Nếu là game, tạo file GDD chính thức trên `ai-context` **sau khi được chủ dự án cho phép**, có thể dựa trên `templates/GAME_DESIGN_DOCUMENT.template.md`; template đó không được coi là GDD đã chốt.
4. Mời thành viên có quyền repo; không đưa token hoặc transcript cá nhân vào file công khai.

## 4. Bàn giao cuộc chat mới
Chỉ cần tải lên **`PROJECT_CONTEXT.md` từ nhánh `ai-context`**. File này đã có sẵn hướng dẫn AI tự tìm các nguồn khác và ghi rõ khi không truy cập được.

## 5. Bộ nhớ nguyên gốc và 1 commit/lượt
- Cấu trúc đã sẵn sàng; chạy `AI-Memory/tools/record_cli.py` khi đã có nguồn sự kiện thật và quyền chia sẻ.
- `AI-Memory/tools/commit_turn.py` kiểm một user message, một assistant final và các sự kiện cùng `turn_id` trước khi tạo commit/push.
- **Không tự động phát sinh mọi bản ghi ChatGPT/Codex chỉ vì dùng template**. Cần adapter sau khi phản hồi kết thúc hoặc nhập export. Không có dữ liệu thì không tạo log giả.
- GitHub Template **không tự nhân bản repository permissions, secrets hoặc cài đặt connector** theo cách có thể thay thế bước cấp quyền. Kiểm tra lại từng tài khoản.

## 6. Vận hành và kiểm thử
```bash
git switch ai-context
python3 tools/validate_context.py
git switch feature/ai-project-memory
python3 AI-Memory/tools/validate_memory.py
python3 -m unittest discover -s AI-Memory/tests -p 'test_*.py' -v
```

Đừng đưa bất kỳ file nào từ `ai-context` hoặc `feature/ai-project-memory` sang `main`. **Nếu đã quên chọn Include all branches, tạo lại repo từ template đúng cách hoặc yêu cầu AI có quyền khôi phục hai nhánh từ template nguồn; không chép AI docs vào main để chữa lỗi.**
