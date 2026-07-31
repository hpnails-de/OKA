# 📜 SỔ QUYẾT ĐỊNH - OKA SYSTEM

> Đọc file này trước tiên khi quay lại dự án sau một thời gian dài.
> Code lưu được **cái gì**. File này lưu **tại sao**.
>
> Lý do file này ra đời: tháng 07/2026, tác giả mở lại dự án sau ~2 tháng và
> **không nhớ nổi mình viết tool này để làm gì**. Trớ trêu thay, đó chính là
> căn bệnh mà tool sinh ra để chữa. `ky_uc.json` ghi được mọi class và hàm,
> nhưng không ghi được một chữ nào về mục đích.

---

## 0. TÊN GỌI

**OKA = Oahspe Kosmon Architect.**
- **Oahspe** — cuốn sách nguồn cảm hứng kiến trúc (đã dùng ẩn dụ tương tự
  cho tool đào Bitcoin trước OKA).
- **Kosmon** — thời đại tri thức/thức tỉnh mà Oahspe nói tới.
- **Architect** — vai trò của CẢ NGƯỜI DÙNG lẫn tool: người vạch bản thiết
  kế, phân chia Lục Phủ Ngũ Tạng, giữ trật tự cho hệ thống số của mình.
  Không phải OKA tự kiến trúc hộ bạn — nó cung cấp bản đồ để BẠN làm kiến
  trúc sư tốt hơn.

---

## 1. HAI MỤC ĐÍCH GỐC

**Mục đích A — Nén ngữ cảnh (phương pháp).**
Làm sao để AI nhớ được nhiều ngữ cảnh dự án hơn mà tốn ít token hơn.
Ý tưởng nền: cơ thể sống chỉ **tàng trữ tinh hoa**, không tàng trữ thức ăn thô.
Tỳ Tạng nhai file source thành bộ xương nhẹ; Tâm Tạng gom bộ xương thành
Chân Kinh súc tích để đưa cho AI, thay vì ném cả nghìn dòng code.

**Mục đích B — Khám bệnh (đích đến).**
OKA là **thầy thuốc đi khám cho các dự án khác** của tác giả — những tool được
viết bằng AI, lúc đầu chạy ngon nhưng khi phình to thì AI bắt đầu
"sửa chỗ này hỏng chỗ kia". OKA không phải nhật ký của riêng nó.

**Hai mục đích này là một.** A là phương pháp, B là đích đến: muốn chẩn bệnh cho
một dự án lớn mà không đốt sạch token thì bắt buộc phải nén ngữ cảnh thật giỏi.
Đây là hai mặt Âm Dương của cùng một tool.

*Bằng chứng trong code (nếu sau này lại quên):* `main_kosmon.py` từng chú thích
đường dẫn đích là **"Bệnh nhân chính"**; `vong_chan_diagnostic.py` chứa từ khóa
`tab_`, `suno_` — dấu vết của các dự án khác, không hề tồn tại trong OKA.

---

## 2. TAM ĐỘC — BA CĂN BỆNH CẦN TRỊ

1. **Teo não** — lập trình viên mất quyền kiểm soát logic dự án của chính mình.
2. **Ảo giác hệ thống** — AI bịa ra hàm/class không tồn tại, sửa A làm hỏng B.
3. **Đứt gãy ký ức** — ném cả file nghìn dòng làm AI tràn bộ nhớ và loạn.

> Ghi chú quan trọng: **"Teo não" không đến từ việc dùng AI.** Nó đến từ việc
> *bỏ cuộc không duyệt nữa vì quá mệt*. AI đẻ 500 dòng trong 10 giây, người đọc
> mất 1 tiếng — nút cổ chai chuyển từ "viết" sang "duyệt". Đó là lý do
> **diff cấu trúc** (mục 4.3) quan trọng hơn vẻ ngoài của nó rất nhiều.

---

## 3. NHỮNG QUYẾT ĐỊNH KIẾN TRÚC ĐÃ CHỐT

**3.1. Ẩn dụ Đông Y là triết lý thiết kế, không phải cách đặt tên cho vui.**
Giữ nguyên hệ thống tên Tạng Phủ. Nó là cách tác giả tư duy về hệ thống.

**3.2. Đốc Mạch (event bus) thay vì gọi thẳng.**
Các Tạng không gọi nhau trực tiếp mà phát tín hiệu lên xương sống, để tránh
phụ thuộc chằng chịt. *Mỗi Tạng tự nối dây thần kinh của mình khi được import* —
không để `main`/`gui` nối hộ, vì trước đây hai nơi nối hai kiểu, sinh ra nối
trùng và nối sót.

**3.3. Bổ sung quan hệ KHẮC bên cạnh quan hệ SINH.**
Ngũ Hành có Sinh (nuôi dưỡng) và Khắc (kiềm chế). Bus cũ chỉ có Sinh nên
không có cách nào hãm một Tạng chạy loạn. Nay `bus.khac()` hãm được một luồng khí.

**3.4. Nhâm Mạch giữ CON TRỎ, không giữ bản sao.**
Theo cách Hippocampus vận hành: nó không chứa ký ức, nó chỉ đánh chỉ mục rồi
trỏ về nơi ký ức thật nằm. Sao chép thành hai bản là tự chuốc lệch pha.

**3.5. Mỗi bệnh nhân một hồ sơ riêng** (`HO_SO_BENH_AN/<tên>_<vân tay>/`).
Trước đây mọi bệnh án đổ chung vào một `OKA_MEMORY.json` trong nhà thầy thuốc,
nên khám bệnh nhân thứ hai là xóa mất bệnh nhân thứ nhất.

**3.6. Mọi đường dẫn neo vào `__file__`, tuyệt đối không dùng `os.getcwd()`.**
Tool này từng được chép từ máy cũ sang máy mới. `getcwd()` phụ thuộc chỗ bạn
đứng lúc gõ lệnh — đổi máy, đổi ổ, đổi thư mục là hỏng.

**3.7. Thầy thuốc không tự tay sửa người bệnh.**
`cfg.TU_DONG_GOT_GIUA = False`. Tiểu Trường từng tự ghi đè file source của
bệnh nhân mỗi lần lưu — nguy hiểm khi người ta đang mở file đó trong editor.
Muốn bật thì tự chịu trách nhiệm.

**3.8. Đo đạc phải trung thực.**
Lọc lấy 1 file thì so với source của đúng file đó. Đem Chân Kinh một file so với
source cả dự án sẽ ra "tiết kiệm 100%" — tự khen dối lòng. Số thật hiện tại:
**~90%** cho một file, **~95%** cho cả dự án.

---

## 4. BA CƠ CHẾ CỐT LÕI (và nguyên lý đằng sau)

**4.1. Cổng Prediction-error** — `ty_tang_parser.py`
Não chỉ ghi nhớ mạnh khi có **bất ngờ**; thông tin lặp lại đúng như dự đoán gần
như không được ghi thêm gì. Nên: vân tay cấu trúc không đổi thì **không ghi ký ức,
không backup, không log**. Sửa comment hay thêm dấu cách không đáng sinh một bản sao.
*Đây là cơ chế tiết kiệm tài nguyên rẻ nhất và hiệu quả nhất của tool.*

**4.2. Thiết Chẩn — bắt mạch** — `thiet_chan_pulse.py`
Trả lời câu hỏi đắt giá nhất: *"sửa hàm này thì hỏng những đâu?"* — tức trị
thẳng bệnh "sửa chỗ này hỏng chỗ kia". Vọng Chẩn chỉ nhìn được da lông
(đếm dòng, đoán tên); muốn biết khí huyết chạy đường nào thì phải bắt mạch.
Nó bắt mạch **trên ký ức Tỳ Tạng đã tiêu hóa sẵn, không đọc lại file** — đúng
tinh thần nhớ nhiều mà tốn ít.

> Bài học đã trả giá: phải đếm cả **tham chiếu** (callback đưa đi gửi), không chỉ
> **lời gọi thẳng**. Bản đầu chỉ đếm lời gọi nên kết oan 22 callback là "code chết"
> — mù hoàn toàn trước kiến trúc event-driven của chính dự án này. Sửa xong còn 6.

**4.3. Diff cấu trúc thay vì diff dòng** — `TyTang.so_sanh()`
Báo *"+2 hàm, −1 hàm, đổi chữ ký 1 chỗ"* thay vì bắt đọc 500 dòng.
Duyệt trong 10 giây thay vì 1 tiếng → **giữ lại được quyền làm chủ**, tức trị
tận gốc bệnh "teo não" ở mục 2.

---

## 5. TỨ CHẨN — LỘ TRÌNH CÒN LẠI

Đông Y có bốn phép khám. Hiện mới xong hai:

| Phép | Y lý | Phần mềm | Trạng thái |
|---|---|---|---|
| **望 Vọng** | Nhìn sắc diện | Đếm dòng, cấu trúc thư mục, tên file | ✅ `vong_chan_diagnostic.py` |
| **切 Thiết** | Bắt mạch, biết khí huyết trong | Đồ thị gọi hàm, huyệt hiểm, khí chết | ✅ `thiet_chan_pulse.py` |
| **聞 Văn** | Nghe tiếng, **ngửi mùi** | **Code smell**, đọc log lỗi runtime | ⬜ chưa có |
| **問 Vấn** | Hỏi tiền sử bệnh | Đọc git history + chính file này | ⬜ chưa có |

> Trùng hợp đáng nhớ: phương Tây gọi code kém là **"code smell" — mùi code**.
> Đông Y gọi phép chẩn qua mùi là **Văn chẩn**. Hai nền văn minh cách nhau vạn
> dặm, cùng dùng khứu giác để mô tả bệnh.

**Còn thiếu (đã thiết kế, chưa viết):**
- **Can Tạng** `task_router.py` — Can chủ sơ tiết. Hàng đợi công việc phải có
  điểm đóng dứt khoát, nếu không task dồn ứ sinh "Can khí uất kết".
- **Tốn ☴** — tiến trình nền củng cố ký ức: gộp entry ít dùng, tỉa cái lỗi thời
  (giống não củng cố ký ức lúc ngủ).
- **Cấn ☶** — biết dừng đúng lúc: ngắt mạch khi quá tải thay vì ráng gánh.

---

## 6. CÁCH DÙNG

```bash
python main_kosmon.py                      # khám bệnh nhân đã ghi danh lần trước
python main_kosmon.py "D:\du_an_cua_ban"   # nhận bệnh nhân mới
python gui_nhan_tang.py                    # bản giao diện (cần customtkinter)
```

Khẩu lệnh: `nhai` → `kham` → `mach` → `kinh`.
Bắt mạch một hàm cụ thể: `mach ten_ham`.

Tool **chạy được ngay không cần cài gì**. Cài thêm để mạnh hơn:

```bash
pip install watchdog customtkinter
```

- Thiếu `watchdog` → Phế chuyển sang "thở chậm" (quét mỗi 3 giây) thay vì chết.
- Thiếu `customtkinter` → chỉ mất giao diện, bản dòng lệnh vẫn đủ tính năng.

---

## 7. BẪY ĐÃ SẬP — ĐỪNG SẬP LẠI

**Đừng dùng `hash()` của Python để đặt tên thư mục.** Nó bị ngẫu nhiên hóa lại
mỗi tiến trình, nên mỗi lần khởi động sinh một hồ sơ mới và ký ức cũ thất lạc
vĩnh viễn. Dùng `hashlib.sha1`. *(Đã sập một lần.)*

**Console Windows mặc định là cp1252, không nuốt nổi emoji.** Máy cũ chạy UTF-8
nên không ai thấy vấn đề; sang máy mới là chết ngay dòng `print` đầu tiên.
`oka_config.py` đã khai khiếu UTF-8 cho stdout — **phải nạp nó trước mọi thứ khác**.
*(Đã sập một lần.)*

**Đừng quên tăng `PHIEN_BAN_TINH_HOA`** khi nâng cấp Tỳ Tạng. Nếu không, chính
cổng Prediction-error sẽ khóa luôn bản nâng cấp — ký ức cũ trông vẫn "y nguyên"
nên không bao giờ được nhai lại. *(Suýt sập.)*

**Đừng dùng `py_compile` để kiểm tra code bệnh nhân.** Nó đẻ ra `__pycache__`
ngay trong nhà người ta — vừa khám vừa xả rác. Dùng `compile()` trong bộ nhớ.
