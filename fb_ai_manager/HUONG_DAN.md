# FB AI Manager — hướng dẫn chạy nhanh

Tool web local (Flask) giúp bạn dùng AI (Groq / Gemini / Claude) viết bài rồi
đăng thẳng lên Facebook Page của bạn, qua Facebook Graph API.

## Chạy trên Windows
1. Cài Python tại python.org/downloads (nhớ tick "Add Python to PATH").
2. Giải nén thư mục này ra một chỗ dễ nhớ.
3. Bấm đúp file `MO_FB_AI.bat` ở thư mục cha (nếu bạn giải nén nguyên repo OKA),
   hoặc mở terminal trong thư mục `fb_ai_manager` rồi chạy:
   ```
   pip install -r requirements.txt
   python run.py
   ```
4. Trình duyệt tự mở `http://127.0.0.1:5050`.

## Chạy trên macOS / Linux
```bash
cd fb_ai_manager
pip install -r requirements.txt
python3 run.py
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
