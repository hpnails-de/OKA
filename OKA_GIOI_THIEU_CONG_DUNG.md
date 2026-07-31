# OKA — Tool làm được gì, chưa làm được gì

*Tài liệu này viết trung thực theo đúng tinh thần của tool: có số liệu đo
thật thì trích số liệu thật, chỗ nào chưa kiểm chứng thì nói rõ là chưa.
Cập nhật lúc: sau khi hoàn thành module Vệ Khí, Trùng Ảnh/Vỏ Rỗng/Giả Khỏi,
Xoắn Ốc Ký Ức, và MCP server (2026-07-31).*

---

## 1. TÓM TẮT MỘT DÒNG

OKA đọc một dự án code (thường do AI viết/sửa), tìm chỗ rủi ro, rồi xuất
một bản tóm tắt cực nhẹ để dán cho AI trước khi nhờ nó sửa tiếp — giúp AI
không bịa hàm không tồn tại và không sửa chỗ này hỏng chỗ kia.

---

## 2. ĐÃ LÀM ĐƯỢC (kiểm chứng thật, không phải thiết kế trên giấy)

### 2.1. Nén ngữ cảnh — giá trị cốt lõi

- Đo bằng `tiktoken` thật (không ước lượng): **~93-97% ít token hơn** so với
  ném cả source code cho AI, tùy dự án.
- **Xoắn Ốc Ký Ức**: nén cả lịch sử HỘI THOẠI với AI (không phải code) theo
  tầng Fibonacci — đo trên chính phiên làm việc này: 3.723 lượt, 476.581 ký
  tự → còn 8.719 ký tự (~3.971 token), giảm **98,2%**, mà vẫn giữ được dấu
  vết từ lượt đầu tiên.

### 2.2. Chẩn đoán cấu trúc

- **Tỳ Tạng**: tiêu hóa file Python (AST thật) và JS/TS/JSX/TSX (regex nhẹ)
  thành bộ xương (tên hàm/lớp), tự đào thải ký ức của file đã xóa/đổi tên.
- **Vọng Chẩn**: phân biệt code chính chủ / file lạ / file phình to.
- **Thiết Chẩn**: đồ thị gọi hàm — biết "sửa hàm này thì hỏng những đâu",
  tìm huyệt hiểm (gọi nhiều nơi) và khí chết (không ai gọi).
- **Can Tạng**: file nào bị sửa cấu trúc dồn dập trong thời gian ngắn —
  dấu hiệu đang vá triệu chứng chứ chưa chạm gốc.
- **Phản Vũ**: dò vòng phụ thuộc luẩn quẩn (import A→B→A) bằng thuật toán
  Tarjan thật, dựng từ câu lệnh import thật (không suy diễn theo tên).
- **Tý Ngọ Lưu Chú**: liên kết ẩn — file luôn đổi cùng nhau nhưng KHÔNG hề
  import nhau (thứ mà công cụ phân tích tĩnh thuần túy không thấy được).

### 2.3. Ba mảng mới, xuất phát từ khảo sát developer thật 2026

- **Vệ Khí**: soi dấu hiệu bảo mật ở cửa ngõ — secret viết cứng, `eval`,
  `shell=True`, TLS tắt xác thực, SQL nối chuỗi. Đã bắt được thật 24 dấu
  hiệu trên một dự án thật (TOOL_YOUTUBE_NEW), gồm cả secret viết cứng.
- **Trùng Ảnh**: hàm có cấu trúc logic giống hệt nhau (sau khi chuẩn hóa
  tên biến) bị copy-paste ở nhiều file. Đã bắt được thật: 3 hàm mã hóa
  `bech32_*` bị nhân bản 3 nơi trong tool_bitcoin.
- **Vỏ Rỗng**: file có nhiều hàm chỉ làm mỗi việc gọi lại hàm khác — dấu
  hiệu thừa tầng trừu tượng không cần thiết.
- **Giả Khỏi**: đọc lịch sử backup của file test, báo khi số `assert` GIẢM
  giữa hai lần lưu — có thể là dọn dẹp hợp lệ, cũng có thể là làm yếu test
  để nó "xanh" thay vì sửa lỗi thật.

### 2.4. Trí nhớ dài hạn của chính OKA

- **Miễn Dịch**: nhớ mọi vấn đề từng phát hiện; nếu vấn đề đã "khỏi" mà
  quay lại thì báo "tái nhiễm".
- **Mùa Gặt**: chấm điểm sức khỏe dự án 0-99 mỗi lần khám, so với lần
  trước, biết xu hướng đang tốt lên hay xấu đi.
- **Thận Tạng**: backup có phiên bản, phục hồi được file cũ.

### 2.5. Tổng hợp và trình bày

- **Thượng Trí**: gộp mọi tín hiệu rời rạc ở trên thành nhận định bằng
  ngôn ngữ tự nhiên, luôn gắn nhãn **CHẮC CHẮN** (đếm thẳng từ code) hoặc
  **SUY ĐOÁN** (quy tắc/mẫu, có thể sai) — không trộn lẫn hai loại vào
  chung một giọng chắc nịch.
- **Mandala SVG**: sơ đồ cụm chức năng vẽ tay bằng SVG, không cần
  matplotlib/graphviz.

### 2.6. Ba cách dùng

- **GUI** một-cú-click (`oka_don_gian.py`, hoặc bấm đúp `MO_OKA.bat` trên
  Windows) — song ngữ Việt/Anh, không cần biết dòng lệnh.
- **CLI** (`main_kosmon.py`) — linh hoạt hơn, có lệnh riêng cho từng module.
- **MCP server** (`oka_mcp_server.py`) — Claude gọi thẳng 6 công cụ giữa
  cuộc trò chuyện, không cần bạn tự chạy script rồi copy-paste. Đã kiểm
  chứng chạy thật, không chỉ cài đặt xong để đó.

### 2.7. Nguyên tắc không cài đặt

Toàn bộ GUI/CLI **chạy được ngay với Python chuẩn**, không cần pip install
gì. Mọi thư viện ngoài (watchdog, customtkinter, tiktoken, mcp) đều tùy
chọn với chế độ rút gọn khi thiếu — trừ MCP server (dùng tính năng nặng
hơn, tách riêng `requirements-mcp.txt`, có ghi rõ trong README).

---

## 3. CHƯA LÀM ĐƯỢC / CẦN CẢI TIẾN — nói thẳng

### 3.1. Giới hạn về mặt kỹ thuật (khó tránh khỏi, không phải lỗi)

- **Không hiểu LOGIC bên trong hàm** — chỉ thấy cấu trúc (tên, số dòng, ai
  gọi ai). Không trả lời được "hàm này có bug không", chỉ trả lời "hàm này
  ai gọi, đổi nó thì ảnh hưởng đâu".
- **JS/TS dùng regex, không phải AST thật** — Python dùng `ast` chuẩn, đáng
  tin hơn hẳn. JS/TS có thể bỏ sót cấu trúc phức tạp (destructuring lồng
  nhau, decorator lạ...).
- **Vệ Khí không phân tích luồng dữ liệu thật** (taint analysis) — chỉ
  khớp mẫu. Báo `eval(x)` là đáng ngờ dù `x` có thể là hằng số vô hại. Đã
  gặp báo giả thật (`api_key="lm-studio"` — placeholder, không phải secret).
- **Trùng Ảnh chỉ hỗ trợ Python** — vì cần AST thật để chuẩn hóa tên biến.
  Dự án JS/TS thuần sẽ không được soi trùng lặp.
- **Giả Khỏi không phân biệt được** "dọn dẹp test hợp lệ" với "làm yếu
  test để né lỗi" — hai việc nhìn giống hệt nhau qua con số assertion.
- **Tý Ngọ Lưu Chú và Giả Khỏi cần lịch sử sửa đổi THẬT tích lũy dần** —
  cài mới hoặc chỉ mới chạy OKA vài lần thì đúng là báo trống, không phải lỗi.

### 3.2. Lỗ hổng vừa tự phát hiện, chưa sửa

- **Xoắn Ốc Ký Ức lãng phí ký tự ở tầng xa**: các lượt chỉ gọi công cụ
  (Bash/Edit/Read) bị liệt kê thành cụm rác `[assistant] [dùng công cụ
  Bash] [user] [kết quả công cụ]` lặp lại nhiều lần, chiếm mất hạn mức ký
  tự quý giá mà không mang thông tin gì. Nên gộp thành thống kê ("đã dùng
  Bash 6 lần") thay vì liệt kê từng lượt.

### 3.3. Chưa được kiểm chứng đầy đủ

- **MCP server mới viết trong ngày, mới test qua 1 lần gọi tool trực
  tiếp** (`oka_context`) — CHƯA test qua một client MCP thật đang chạy
  liên tục nhiều lượt (Claude Desktop/Claude Code thật), chưa biết có vấn
  đề gì khi gọi liên tiếp nhiều tool trong một phiên dài hay không.
- **Không có bộ unit test tự động chính thức** — mọi kiểm chứng trong dự
  án này đều làm bằng tay: viết ví dụ biết trước đáp án, chạy trên 3 dự án
  thật, đọc lại kết quả. Không có `pytest`/CI nào tự chạy lại mỗi khi sửa
  code — nếu ai đó sửa nhầm, phải tự phát hiện bằng cách chạy lại thủ công.
- **Cộng đồng**: repo public nhưng 0 sao, 0 issue, 0 người dùng ngoài tác
  giả tính đến giờ — mọi phát hiện lỗi/báo giả trong tài liệu này đều do
  chính tác giả/AI tự tìm, CHƯA có ai bên ngoài thử và xác nhận độc lập.

### 3.4. Việc đã thiết kế nhưng chưa viết (xem `OKA_QUYET_DINH.md` mục 5)

Đông Y có Tứ Chẩn (4 phép khám) — OKA mới xong 2:

| Phép | Trạng thái |
|---|---|
| 望 Vọng (nhìn sắc diện) | ✅ Xong |
| 切 Thiết (bắt mạch) | ✅ Xong |
| 聞 Văn (nghe/ngửi — code smell qua log lỗi runtime thật) | ⬜ Chưa viết |
| 問 Vấn (hỏi tiền sử — đọc git history) | ⬜ Chưa viết |

Ngoài ra còn 2 ý tưởng đã ghi nhận nhưng chưa làm: một tiến trình nền tự
gộp/tỉa ký ức lỗi thời (giống não củng cố ký ức lúc ngủ), và một cơ chế tự
biết dừng đúng lúc khi quá tải thay vì ráng gánh.

---

## 4. ƯU TIÊN GỢI Ý CHO VÒNG TIẾP THEO

1. **Sửa rác tool-call trong Xoắn Ốc Ký Ức** — dễ làm, lợi ích rõ, đã biết
   chính xác chỗ cần sửa.
2. **Test MCP server qua client thật** (Claude Desktop hoặc phiên Claude
   Code khác) thay vì chỉ gọi hàm Python trực tiếp — để chắc chắn nó chạy
   ổn trong tình huống dùng thật, không chỉ trong môi trường kiểm thử.
3. **Viết bộ test tự động** (dù nhẹ) cho các thuật toán cốt lõi (chuẩn hóa
   AST của Trùng Ảnh, thuật toán Tarjan của Phản Vũ...) — để lỗi tương lai
   bị bắt ngay, không phải đợi chạy tay trên dự án thật mới phát hiện.
4. **Văn Chẩn** (nghe log lỗi runtime) — mảnh còn thiếu lớn nhất trong Tứ
   Chẩn, và là loại tín hiệu hoàn toàn khác 3 phép kia (động, không tĩnh).
