# FB AI Manager — hướng dẫn chạy nhanh

Tool web local (Flask) giúp bạn dùng AI (Groq / Gemini / Claude) viết bài rồi
đăng thẳng lên Facebook Page của bạn, qua Facebook Graph API.

## Chạy trên Windows (khuyên dùng — không cần mở terminal/VSCode)
1. Cài Python tại python.org/downloads (nhớ tick "Add Python to PATH").
2. Giải nén thư mục này ra một chỗ dễ nhớ.
3. Bấm đúp file `MO_FB_AI.bat` ở thư mục cha (nếu bạn giải nén nguyên repo OKA).
   Lần đầu chạy sẽ hơi lâu vì tool tự tạo **môi trường ảo riêng**
   (`fb_ai_manager/venv/`) rồi cài thư viện vào đó — không đụng tới Python hệ
   thống của bạn. Những lần sau mở lại rất nhanh.
4. Trình duyệt tự mở `http://127.0.0.1:5050`.

## Chạy trên macOS / Linux (không cần mở terminal/VSCode)
Bấm đúp file `MO_FB_AI.sh` ở thư mục cha (macOS: chuột phải → Open, chọn cho
phép chạy nếu bị chặn lần đầu). Tool cũng tự tạo môi trường ảo riêng như trên.

Hoặc chạy tay qua terminal:
```bash
cd fb_ai_manager
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python run.py
```

## Các bước dùng thử
1. Vào **Cài đặt** → nhập API key của Groq/Gemini/Claude (chọn 1 cái cũng được).
2. Vẫn ở **Cài đặt** → thêm trang Facebook: cần **Page ID** + **Page Access
   Token** (không phải access token cá nhân). Trang Cài đặt trong tool có
   hướng dẫn từng bước lấy token qua `developers.facebook.com` + Graph API
   Explorer.
3. Vào **Tạo & đăng bài** → nhập chủ đề → bấm "Sinh nội dung" → xem/sửa →
   bấm "Đăng ngay" hoặc chọn giờ rồi "Lên lịch".
4. Vào **Lịch sử** để xem lại các bài đã đăng/lên lịch/thất bại.

## Lưu ý bảo mật
- Toàn bộ API key và Facebook token chỉ lưu trong file
  `data/fb_ai_manager.db` ngay trong thư mục này — không gửi đi đâu khác
  ngoài chính nhà cung cấp AI bạn chọn (khi sinh nội dung) và Facebook (khi
  đăng bài).
- Đừng chia sẻ file `data/fb_ai_manager.db` cho ai — nó chứa key/token của bạn.
- Tool chỉ chạy trên máy bạn (`127.0.0.1`), không có ai khác truy cập được
  trừ khi bạn tự mở cổng 5050 ra ngoài.
