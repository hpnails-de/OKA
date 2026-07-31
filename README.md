# OKA_System — Thầy Thuốc cho code do AI viết
### *The Physician for AI-written code*

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
![Zero install required](https://img.shields.io/badge/dependencies-zero%20required-brightgreen)
![Stdlib only](https://img.shields.io/badge/stdlib-only-lightgrey)

> 🇻🇳 Tiếng Việt bên dưới · 🇬🇧 **[English section below](#-english)**

**OKA = Oahspe Kosmon Architect.** *Oahspe* (cuốn kinh sách nguồn cảm hứng
kiến trúc), *Kosmon* (thời đại tri thức/thức tỉnh mà Oahspe nói tới), và
*Architect* — vai trò của cả người dùng lẫn tool: người vạch bản thiết kế,
phân chia Lục Phủ Ngũ Tạng, giữ trật tự cho hệ thống số của mình.

OKA không phải tool tự viết code. Nó là **công cụ chẩn đoán** gắn vào một dự án
khác (thường là dự án bạn để AI viết giúp) — đọc cấu trúc, tìm chỗ rủi ro,
soi dấu hiệu vá triệu chứng mà chưa chạm gốc, rồi xuất một bản tóm tắt cực
nhẹ ("Chân Kinh") để dán cho AI trước khi nhờ nó sửa tiếp, giúp AI không bịa
ra hàm không tồn tại hay phá vỡ chỗ khác khi sửa.

**Kiến trúc mượn khung Đông Y** (Ngũ Tạng, Lục Phủ, Tứ Chẩn) làm ẩn dụ thiết
kế — mỗi module core đặt tên theo một tạng phủ, vì cơ thể sống là một hệ
quản lý thông tin đã được thử nghiệm hàng triệu năm (chỉ giữ lại tinh hoa,
đào thải cái vô dụng, nhớ mầm bệnh cũ). Đây là ẩn dụ giúp tác giả tư duy về
kiến trúc, **không phải quảng cáo** — phần "Giới hạn thật" bên dưới liệt kê
rõ những gì tool CHƯA làm được.

**Giao diện có tiếng Việt và tiếng Anh** — bấm nút VI/EN ở góc phải.

---

## 🐣 Dành cho người mới — chưa từng lập trình cũng làm được

Làm theo đúng 5 bước này, không cần biết gì về lập trình:

**Bước 1 — Cài Python** (nếu máy chưa có)
Vào [python.org/downloads](https://www.python.org/downloads/), tải bản mới
nhất, chạy file cài đặt. **Quan trọng:** ở màn hình đầu tiên, tick vào ô
**"Add Python to PATH"** trước khi bấm Install — bỏ qua bước này thì các
bước sau sẽ báo lỗi.

**Bước 2 — Tải OKA về máy**
Vào trang [github.com/hpnails-de/OKA](https://github.com/hpnails-de/OKA),
bấm nút xanh **"Code"** → **"Download ZIP"**. Giải nén file zip ra một chỗ
dễ nhớ (ví dụ Desktop).

**Bước 3 — Mở OKA**
Vào đúng thư mục vừa giải nén, **bấm đúp vào file `MO_OKA.bat`**. Một cửa
sổ đen sẽ hiện lên kiểm tra Python, rồi một cửa sổ nhỏ của OKA sẽ mở ra.
(Nếu cửa sổ đen báo chưa có Python, quay lại Bước 1.)

**Bước 4 — Khám dự án**
Trong cửa sổ OKA, bấm **"📂 Chọn thư mục dự án..."**, chọn đúng thư mục dự
án bạn muốn AI giúp sửa. Đợi vài giây tới vài phút (tùy dự án lớn nhỏ) —
thanh tiến trình sẽ báo đang làm gì.

**Bước 5 — Dùng kết quả**
Xong việc, OKA lưu một file `OKA_BAO_CAO_<tên_dự_án>.md` NGAY TRONG thư mục
dự án đó. Bấm nút **"📋 Copy nội dung"** trong cửa sổ OKA (hoặc tự mở file
đó bằng Notepad), rồi dán toàn bộ vào khung chat với AI (Claude, ChatGPT...)
kèm câu đại loại: *"Đây là bối cảnh dự án tôi, đọc trước khi giúp tôi sửa
code nhé."*

Chỉ vậy thôi — không cần hiểu Ngũ Tạng/Lục Phủ, không cần gõ lệnh gì.

---

## Cài đặt (cho ai muốn tự chạy bằng dòng lệnh, hoặc dùng macOS/Linux)

Chỉ cần Python 3.9+ và thư viện chuẩn — **không bắt buộc cài gì thêm**.
Hai thư viện dưới đây là tùy chọn, thiếu vẫn chạy được (tự chuyển sang chế độ
rút gọn):

```bash
pip install -r requirements.txt   # tùy chọn: bản CLI không cần cũng chạy được
```

## Cách dùng nhanh nhất — không cần gõ lệnh gì

```bash
python oka_don_gian.py
```
(Trên Windows, bấm đúp `MO_OKA.bat` làm đúng việc này, không cần mở dòng lệnh.)

Mở ra một cửa sổ nhỏ, bấm "📂 Chọn thư mục dự án...", chọn xong OKA tự chạy
hết mọi bước rồi xuất file `OKA_BAO_CAO_<tên_dự_án>.md` ngay trong thư mục
dự án đó — dán toàn bộ file này cho AI trước khi nhờ nó sửa code.

## Cách dùng qua dòng lệnh (linh hoạt hơn, cho ai quen terminal)

```bash
# Lần đầu, hoặc muốn đổi sang khám dự án khác:
python main_kosmon.py "duong/dan/toi/du_an_can_kham"

# Lần sau, khám lại đúng dự án vừa khám gần nhất (không cần gõ lại đường dẫn):
python main_kosmon.py
```

Sau khi khởi động, gõ lệnh tại dấu nhắc `👉 Nhập lệnh:` (gõ `lenh` để xem lại
bảng đầy đủ bất cứ lúc nào):

| Lệnh | Chức năng |
|---|---|
| `nhai` | Tỳ Tạng tiêu hóa toàn bộ dự án — **luôn làm lệnh này trước tiên** |
| `kham` | Vọng Chẩn — nhìn sắc diện: file nào chính chủ, file nào lạ, file nào phình to |
| `mach` | Thiết Chẩn bắt mạch (huyệt hiểm, khí chết) - Thượng Trí tự tổng hợp nhận định ngay sau đó |
| `mach <tên hàm>` | Sửa hàm này thì hỏng những đâu? |
| `goc` | Can Tạng — file nào đang bị vá triệu chứng, chưa chạm gốc |
| `baomat` | Vệ Khí — soi dấu hiệu bảo mật (secret viết cứng, eval, SQL nối chuỗi, TLS tắt xác thực...) |
| `chatluong` | Trùng Ảnh/Vỏ Rỗng/Giả Khỏi — soi trùng lặp code, lớp bọc thừa, test bị làm yếu |
| `canbang` | Cân Bằng Âm Dương — lời gọi hàm không có định nghĩa tương ứng |
| `nhoky` | Xoắn Ốc Ký Ức — nén lịch sử hội thoại đã có với AI về dự án này |
| `kinh [từ khóa]` | Xuất Chân Kinh — bản tóm tắt để dán cho AI trước khi nhờ nó sửa code |
| `benhnhan` | Xem / đổi dự án đang khám |
| `hoisinh <file>` | Phục hồi file từ bản Nguyên Khí (backup) đã lưu |
| `don` | Đại Trường dọn rác (.temp, cache...) |
| `thoat` | Đóng lại |

## Dùng qua MCP — để Claude tự gọi OKA, không cần copy-paste

Ngoài GUI và CLI ở trên, OKA còn có thể chạy như một **MCP server**
(`oka_mcp_server.py`) — Claude Code (hoặc Claude Desktop) gọi thẳng các
công cụ chẩn đoán trong lúc trò chuyện, thay vì bạn phải tự mở terminal
chạy `python oka_don_gian.py` rồi copy nội dung báo cáo dán vào chat.

Đây là tính năng **nặng hơn hẳn** so với phần còn lại của dự án (gói `mcp`
kéo theo hơn chục gói phụ thuộc như uvicorn/starlette), nên tách riêng khỏi
`requirements.txt` — hoàn toàn không cần nếu bạn chỉ dùng GUI/CLI bình thường.

**Cài đặt:**
```bash
pip install -r requirements-mcp.txt
```

**Đăng ký với Claude Code:** sao chép [`oka.mcp.json.example`](oka.mcp.json.example)
thành `.mcp.json` trong dự án bạn muốn Claude khám (hoặc gộp vào cấu hình
MCP hiện có), sửa đường dẫn `args` thành đường dẫn tuyệt đối thật tới
`oka_mcp_server.py` trên máy bạn:

```json
{
  "mcpServers": {
    "oka": {
      "command": "python",
      "args": ["/duong/dan/toi/OKA_System/oka_mcp_server.py"]
    }
  }
}
```

**6 công cụ có sẵn:**

| Tool | Tương đương lệnh CLI | Chức năng |
|---|---|---|
| `oka_context` | `nhai` + `mach` + `kinh` | Đọc cấu trúc + cảnh báo rủi ro — gọi tool này ĐẦU TIÊN |
| `oka_impact` | `mach <tên hàm>` | Sửa hàm này thì hỏng những đâu? |
| `oka_security_scan` | `baomat` | Vệ Khí — dấu hiệu bảo mật |
| `oka_root_cause` | `goc` | Can Tạng — file nào bị vá triệu chứng lặp lại |
| `oka_quality_scan` | `chatluong` | Trùng Ảnh/Vỏ Rỗng/Giả Khỏi |
| `oka_balance_check` | `canbang` | Cân Bằng Âm Dương — lời gọi hàm không có định nghĩa |
| `oka_chat_memory` | `nhoky` | Xoắn Ốc Ký Ức — nén lại lịch sử hội thoại đã có với AI về dự án này |

`oka_chat_memory` chỉ đọc được bản ghi của **Claude Code/Claude** (file
`.jsonl` lưu tại `~/.claude/projects/`) — không đọc được lịch sử chat của
Gemini/ChatGPT vì các nơi đó không lưu transcript ra máy theo cách này.

## Kiến trúc — tên module thật trong code (không phải bản thiết kế mơ)

Mỗi hàng dưới đây là một **file thật** trong repo, không phải ý tưởng chưa
viết:

| Ẩn dụ Đông Y | File thật | Làm gì |
|---|---|---|
| **Tỳ Tạng** (lá lách — tiêu hóa) | `ty_tang_parser.py` | Tiêu hóa file source thành bộ xương nhẹ (tên hàm/lớp), bỏ phần thân |
| **Thận Tạng** (thận — tàng tinh) | `than_tang_backup.py` | Backup có phiên bản, phục hồi khi cần |
| **Vọng Chẩn** (nhìn sắc diện) | `vong_chan_diagnostic.py` | Khám bề mặt: kích thước file, file lạ, file phình to |
| **Thiết Chẩn** (bắt mạch) | `thiet_chan_pulse.py` | Đồ thị gọi hàm: điểm trọng yếu, code chết |
| **Can Tạng** (gan — gốc bệnh mãn) | `can_tang_goc.py` | Đánh dấu file bị vá đi vá lại mà không chạm gốc |
| **Phản Vũ** (khắc chế ngược) | `phan_vu_vong.py` | Dò vòng phụ thuộc luẩn quẩn (thuật toán Tarjan) |
| **Tý Ngọ Lưu Chú** (khí huyết theo giờ) | `ty_ngo_luu_chu.py` | Liên kết ẩn: file luôn đổi cùng nhau mà KHÔNG hề import nhau |
| **Vệ Khí** (khí phòng vệ ngoài bì mao) | `ve_khi_bao_ve.py` | Soi dấu hiệu bảo mật ở cửa ngõ: secret viết cứng, eval, SQL nối chuỗi... |
| **Trùng Ảnh** (bóng trùng) | `trung_anh.py` | Hàm có cấu trúc logic giống hệt nhau bị copy-paste ở nhiều file |
| **Vỏ Rỗng** (lớp bọc rỗng) | `vo_rong.py` | File có nhiều hàm chỉ gọi lại hàm khác, không thêm logic — dấu hiệu thừa tầng |
| **Giả Khỏi** (giả vờ đã khỏi) | `gia_khoi.py` | Bài test bị làm yếu (giảm assertion) thay vì sửa lỗi thật |
| **Cân Bằng Âm Dương** | `am_duong_can_bang.py` | Lời gọi hàm (Dương) không có định nghĩa tương ứng (Âm) — AI gọi hàm/phương thức không tồn tại |
| **Miễn Dịch** (trí nhớ miễn dịch) | `mien_dich.py` | Nhớ lại vấn đề cũ; báo "tái nhiễm" nếu nó quay lại |
| **Mùa Gặt** (chấm phẩm cấp) | `mua_gat.py` | Điểm sức khỏe 0-99 mỗi lần khám, so với lần trước |
| **Xoắn Ốc Ký Ức** (ký ức Fibonacci) | `xoan_oc_ky_uc.py` | Nén lịch sử hội thoại AI theo tầng, để phiên AI mới đọc lại được mạch việc |
| **Thượng Trí** (trí tổng hợp) | `thuong_tri_tong_hop.py` | Gộp mọi tín hiệu trên thành nhận định bằng ngôn ngữ tự nhiên |

Ba module cuối cùng của nhóm "chất lượng cấu trúc" (Trùng Ảnh/Vỏ Rỗng/Giả
Khỏi) và Vệ Khí ra đời từ khảo sát developer thật năm 2026 (40% nói AI làm
tăng nợ kỹ thuật vì code trùng lặp; ~1/4 code AI sinh ra có lỗ hổng bảo mật
đã biết) — không phải suy đoán chủ quan.

## Nhãn độ tin cậy — đọc phần này trước khi tin bất kỳ nhận định nào

Mọi nhận định trong báo cáo đều gắn nhãn:

- **CHẮC CHẮN** — đếm thẳng từ code (số lần gọi, số dòng, vòng import). Không
  cãi được.
- **SUY ĐOÁN** — dựa trên quy tắc/mẫu, CÓ THỂ SAI, và báo cáo luôn nói rõ vì
  sao có thể sai. Ví dụ: "code chết" không thấy được hàm gọi động, gọi qua
  route web, hay là entry point.

Công cụ nào trình bày mọi nhận định với cùng một giọng chắc nịch sẽ khiến
người đọc mất lòng tin vào TẤT CẢ chúng, kể cả chỗ đúng. OKA cố tình tách
riêng hai loại này.

## Giới hạn thật — nói thẳng để bạn không kỳ vọng sai

- Bản tóm tắt cho AI chỉ có **cấu trúc, không có logic**: giúp AI không bịa
  tên hàm và biết chỗ nào rủi ro, nhưng KHÔNG mô tả một hàm cụ thể làm gì
  bên trong.
- JS/TS dùng **regex nhẹ**, không phải AST thật (AST thật cần cài
  tree-sitter, phá nguyên tắc không-cài-đặt). Python dùng module `ast`
  thật của chính Python.
- Vệ Khí/Trùng Ảnh/Vỏ Rỗng/Giả Khỏi/Cân Bằng Âm Dương đều dựa trên mẫu/số
  đếm — KHÔNG phân tích luồng dữ liệu thật, KHÔNG chạy test thật. Luôn có
  thể báo giả.
- **Cân Bằng Âm Dương** cố ý CHỈ xét lời gọi tên trần và `self.method()`
  trong lớp không kế thừa — bỏ qua `module.foo()`/`obj.foo()` vì cần suy
  luận kiểu dữ liệu mới xác minh đúng được. Thà bỏ sót còn hơn báo sai.
- **Tý Ngọ Lưu Chú** và **Giả Khỏi** cần lịch sử sửa đổi thật tích lũy dần
  mới có gì để báo — cài mới thì đúng là báo trống, không phải lỗi.
- Ngôn ngữ hỗ trợ: Python, JavaScript, TypeScript, JSX, TSX.
- Đây KHÔNG phải công cụ bảo mật/QA thay thế cho rà soát bảo mật hay chạy
  test thật — nó chỉ gợi ý chỗ ĐÁNG xem lại trước.

### Dùng thử và góp ý

Đây là dự án cá nhân, lần đầu thử làm mã nguồn mở đúng nghĩa. Nếu bạn chạy
thử trên dự án của mình — nhất là ngôn ngữ/framework tôi chưa test kỹ — và
thấy nó nhận định sai hoặc khó hiểu, đó chính là loại phản hồi giúp cải
thiện nhanh nhất. [Mở issue tại đây](../../issues/new/choose).

---

## 🇬🇧 English

**OKA = Oahspe Kosmon Architect.** *Oahspe* (the book that inspired the
architecture), *Kosmon* (the age of awakened knowledge Oahspe describes),
and *Architect* — the role of both the user and the tool: the one who
draws the blueprint and keeps order across a digital system.

**OKA is a diagnostic tool, not a code generator.** You point it at a project
(typically one you built with an AI assistant) and it reads the structure,
finds risky spots, detects symptom-patching that never reached the root cause,
then exports one lightweight digest you paste into your AI *before* asking it
to change anything. The AI stops inventing functions that don't exist and stops
breaking one thing while fixing another.

Measured on real projects: **~96–97% fewer tokens** than pasting the source
(counted with `tiktoken`, not estimated).

Every module is named after a concept from Vietnamese/Chinese traditional
medicine — that's a design metaphor the author thinks in, **not marketing**.
See "Honest limitations" below for what the tool does *not* do.

### 🐣 For complete beginners — no programming knowledge needed

**Step 1 — Install Python** (if you don't have it)
Go to [python.org/downloads](https://www.python.org/downloads/), download
the latest version, run the installer. **Important:** on the first screen,
check **"Add Python to PATH"** before clicking Install — skipping this
makes every later step fail.

**Step 2 — Download OKA**
Go to [github.com/hpnails-de/OKA](https://github.com/hpnails-de/OKA), click
the green **"Code"** button → **"Download ZIP"**. Unzip it somewhere easy to
find (e.g. your Desktop).

**Step 3 — Open OKA**
On Windows: go into the unzipped folder and **double-click `MO_OKA.bat`**.
A black window checks for Python, then OKA's window opens.
On macOS/Linux: open a terminal in that folder and run `python3 oka_don_gian.py`.

**Step 4 — Examine your project**
Click **"Choose folder…"**, pick the project you want your AI to help with.
Wait a few seconds to a few minutes depending on project size — a progress
bar shows what it's doing.

**Step 5 — Use the result**
OKA saves a file named `OKA_BAO_CAO_<project>.md` directly inside that
project's folder. Click **"Copy content"** in the OKA window (or open the
file yourself in a text editor), then paste the whole thing into your chat
with an AI (Claude, ChatGPT...) with something like: *"This is my project's
context, read it before helping me modify the code."*

That's it — no need to understand the organ metaphors, no commands to type.

### Why the Traditional-Medicine architecture?

Every module is named after an organ from Vietnamese/Chinese traditional
medicine. This is not decoration. The human body is an information-management
system refined over millions of years, and several of its strategies map
directly onto hard problems in tooling:

| Organ / concept | Real file | What it does in OKA |
|---|---|---|
| **Tỳ Tạng** (spleen — transforms food into essence) | `ty_tang_parser.py` | Digests source files into a lightweight skeleton, discards the bulk |
| **Thận Tạng** (kidney — stores vital essence) | `than_tang_backup.py` | Versioned backups, restore on demand |
| **Vọng Chẩn** (visual inspection) | `vong_chan_diagnostic.py` | Surface exam: file sizes, foreign files, bloat |
| **Thiết Chẩn** (pulse reading) | `thiet_chan_pulse.py` | Call-graph analysis: critical points, dead code |
| **Can Tạng** (liver — root of chronic illness) | `can_tang_goc.py` | Flags files patched over and over without fixing the root |
| **Phản Vũ** (rebellious counter-restraint) | `phan_vu_vong.py` | Circular-dependency detection (Tarjan SCC) |
| **Tý Ngọ Lưu Chú** (organ-clock qi flow) | `ty_ngo_luu_chu.py` | **Hidden coupling**: files that always change together with *no* import linking them |
| **Vệ Khí** (defensive qi at the body's surface) | `ve_khi_bao_ve.py` | Security-smell scan at the perimeter: hardcoded secrets, `eval`, `shell=True`, disabled TLS... |
| **Trùng Ảnh** ("duplicate shadow") | `trung_anh.py` | Functions with identical logic structure copy-pasted across files |
| **Vỏ Rỗng** ("empty shell") | `vo_rong.py` | Files with several functions that only forward to another function — unnecessary abstraction |
| **Giả Khỏi** ("faked recovery") | `gia_khoi.py` | Test assertions thinned over time instead of the bug being fixed |
| **Cân Bằng Âm Dương** (Yin-Yang balance) | `am_duong_can_bang.py` | A function call (Yang) with no matching definition (Yin) anywhere — AI calling something that doesn't exist |
| **Miễn Dịch** (adaptive immunity) | `mien_dich.py` | Regression memory: a fixed problem reappearing raises a *reinfection* alert |
| **Mùa Gặt** (harvest) | `mua_gat.py` | 0–99 health grade each scan, trend vs the previous one |
| **Xoắn Ốc Ký Ức** (Fibonacci memory spiral) | `xoan_oc_ky_uc.py` | Compresses your AI conversation history so a new session can pick up where you left off |
| **Thượng Trí** (higher mind) | `thuong_tri_tong_hop.py` | Synthesises all of the above into plain-language findings |

Vệ Khí and the three "structural quality" modules (Trùng Ảnh/Vỏ Rỗng/Giả
Khỏi) came directly from real 2026 developer-survey data — 40% of developers
report AI increases technical debt through duplicate/unnecessary code, and
roughly a quarter of AI-generated code contains a known security
vulnerability — not personal speculation.

### Install

Python 3.9+ and the standard library. **Nothing else is required.**
Every third-party library is optional with a graceful fallback:

```bash
pip install -r requirements.txt   # optional
```

- missing `watchdog` → falls back to polling every 3s
- missing `customtkinter` → use the plain-tkinter GUI (always available)
- missing `tiktoken` → falls back to a ~4-chars-per-token estimate

### Quick start (no commands to memorise)

```bash
python oka_don_gian.py
```

A window opens. Click **Choose folder…**, pick your project, and OKA runs the
whole examination, then writes:

- `OKA_BAO_CAO_<project>.md` — the report to paste into your AI
- `OKA_MANDALA_<project>.svg` — a diagram of functional clusters (open in a browser)

Use the **VI / EN** buttons in the top-right to switch language.

### Command-line usage

```bash
python main_kosmon.py "/path/to/your/project"   # first time, or to switch project
python main_kosmon.py                            # re-examine the last project
```

| Command | What it does |
|---|---|
| `nhai` | Digest the whole project — **always run this first** |
| `kham` | Visual exam: owned code vs foreign files, bloated files |
| `mach` | Pulse: critical functions, dead code, cycles, synthesis |
| `mach <name>` | If I change this function, what breaks? |
| `goc` | Which files are being patched repeatedly without a real fix |
| `baomat` | Security-smell scan: hardcoded secrets, eval, string-built SQL, disabled TLS verification... |
| `chatluong` | Duplicate logic across files, unnecessary wrapper concentration, tests weakened over time |
| `canbang` | Function calls with no matching definition anywhere (Yin-Yang balance) |
| `nhoky` | Compress the conversation history you've had with your AI about this project |
| `kinh [keyword]` | Export the digest for your AI |
| `benhnhan` | Show / switch the project being examined |
| `hoisinh <file>` | Restore a file from backup |
| `don` | Clean temp/cache garbage |
| `thoat` | Quit |

### Using it via MCP — let Claude call OKA directly, no copy-paste

Besides the GUI and CLI above, OKA can also run as an **MCP server**
(`oka_mcp_server.py`) — Claude Code (or Claude Desktop) calls the
diagnostic tools directly mid-conversation, instead of you opening a
terminal, running `python oka_don_gian.py`, and pasting the report back in.

This is **noticeably heavier** than the rest of the project (the `mcp`
package pulls in a dozen-plus dependencies like uvicorn/starlette), so it's
kept out of `requirements.txt` — not needed at all if you only use the GUI/CLI.

**Install:**
```bash
pip install -r requirements-mcp.txt
```

**Register with Claude Code:** copy [`oka.mcp.json.example`](oka.mcp.json.example)
to `.mcp.json` in the project you want Claude to examine (or merge into
your existing MCP config), and change `args` to the real absolute path to
`oka_mcp_server.py` on your machine:

```json
{
  "mcpServers": {
    "oka": {
      "command": "python",
      "args": ["/path/to/OKA_System/oka_mcp_server.py"]
    }
  }
}
```

**6 available tools:**

| Tool | Equivalent CLI command | What it does |
|---|---|---|
| `oka_context` | `nhai` + `mach` + `kinh` | Structure + risk warnings — call this one FIRST |
| `oka_impact` | `mach <name>` | If I change this function, what breaks? |
| `oka_security_scan` | `baomat` | Vệ Khí — security-smell scan |
| `oka_root_cause` | `goc` | Can Tạng — files being patched repeatedly without a real fix |
| `oka_quality_scan` | `chatluong` | Trùng Ảnh/Vỏ Rỗng/Giả Khỏi |
| `oka_balance_check` | `canbang` | Yin-Yang balance — function calls with no matching definition |
| `oka_chat_memory` | `nhoky` | Compress the conversation history you've had with your AI about this project |

`oka_chat_memory` only reads **Claude Code/Claude** transcripts (the `.jsonl`
files under `~/.claude/projects/`) — it cannot read Gemini/ChatGPT chat
history since those don't save transcripts to disk this way.

### Confidence labels — read these

Every finding is tagged:

- **CERTAIN** — counted straight from the code (call counts, line counts,
  import cycles). Not arguable.
- **INFERRED** — heuristics that *can be wrong*, and the report says why.
  Example: "dead code" cannot see functions called dynamically, via web
  routes, or as entry points.

Tools that present every finding with equal confidence train you to distrust
all of them. This one tells you which is which.

### Honest limitations

- The digest gives **structure, not logic**. It stops the AI hallucinating
  names and shows where the risk is; it does not describe what a function
  actually does inside.
- JS/TS parsing uses **lightweight regex**, not a real AST (that would require
  installing tree-sitter, breaking the zero-install rule). Python uses the real
  `ast` module.
- Vệ Khí/Trùng Ảnh/Vỏ Rỗng/Giả Khỏi/Cân Bằng Âm Dương are pattern/count-based
  — they do **not** analyze real data flow and do **not** run your actual
  test suite. False positives are always possible.
- **Cân Bằng Âm Dương** deliberately only checks bare-name calls and
  `self.method()` inside non-inheriting classes — it skips `module.foo()`/
  `obj.foo()` since verifying those needs real type inference. Under-flagging
  is the safe direction here, not over-flagging.
- **Tý Ngọ Lưu Chú** and **Giả Khỏi** need accumulated real editing history
  before they produce anything. On a fresh install they correctly report
  nothing — that's expected, not a bug.
- Supported languages: Python, JavaScript, TypeScript, JSX, TSX.
- This is **not** a replacement for a real security review or running your
  test suite — it only points at places worth a second look.

### Try it and tell me what broke

This is a solo project trying out a real open-source cycle. If you run it on
your own project — especially a language mix or framework I haven't tested —
and it misclassifies something or gives a confusing finding, that's exactly
the kind of report that improves it fastest.
[Open an issue](../../issues/new/choose) or see [CONTRIBUTING.md](CONTRIBUTING.md).

### License

MIT — see `LICENSE`.
