# OKA_System — Thầy Thuốc cho code do AI viết
### *The Physician for AI-written code*

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
![Zero install required](https://img.shields.io/badge/dependencies-zero%20required-brightgreen)
![Stdlib only](https://img.shields.io/badge/stdlib-only-lightgrey)

> 🇻🇳 Tiếng Việt bên dưới · 🇬🇧 **[English section below](#-english)**

OKA không phải tool tự viết code. Nó là **công cụ chẩn đoán** gắn vào một dự án
khác (thường là dự án bạn để AI viết giúp) — đọc cấu trúc, tìm chỗ rủi ro,
soi dấu hiệu vá triệu chứng mà chưa chạm gốc, rồi xuất một bản tóm tắt cực
nhẹ ("Chân Kinh") để dán cho AI trước khi nhờ nó sửa tiếp, giúp AI không bịa
ra hàm không tồn tại hay phá vỡ chỗ khác khi sửa.

**Kiến trúc mượn nguyên khung Đông Y** (Ngũ Tạng, Lục Phủ, Tứ Chẩn) — không
phải để cho vui, mà vì cơ thể người là hệ thống quản lý thông tin đã được
thử thách hàng triệu năm: nhai thức ăn thành tinh chất rồi bỏ xác thô, nhớ
mầm bệnh cũ để lần sau nhận ra ngay, có tạng chuyên đào thải cái vô dụng.

**Giao diện có tiếng Việt và tiếng Anh** — bấm nút VI/EN ở góc phải.

## Cài đặt

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
Mở ra một cửa sổ nhỏ, bấm "📂 Chọn thư mục dự án...", chọn xong OKA tự chạy
hết mọi bước rồi xuất **đúng một file** `OKA_BAO_CAO_<tên_dự_án>.md` ngay
trong thư mục dự án đó — dán toàn bộ file này cho AI trước khi nhờ nó sửa
code. Không cần biết gì về Ngũ Tạng/Lục Phủ bên trong cũng dùng được.

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
| `mach` | Thiết Chẩn bắt mạch (huyệt hiểm, khí chết) - Thượng Trí tự tổng hợp nhận định ngay sau đó (dùng ngầm cả dữ liệu Can Tạng, không cần gõ `goc` riêng để có nhận định tổng hợp) |
| `mach <tên hàm>` | Sửa hàm này thì hỏng những đâu? |
| `goc` | Can Tạng — in báo cáo CHI TIẾT file nào đang bị vá triệu chứng, chưa chạm gốc (Thượng Trí chỉ tóm tắt 1 dòng, muốn xem đầy đủ thì gõ lệnh này) |
| `baomat` | Vệ Khí — soi dấu hiệu bảo mật (secret viết cứng, eval, SQL nối chuỗi, TLS tắt xác thực...) |
| `chatluong` | Trùng Ảnh/Vỏ Rỗng/Giả Khỏi — soi trùng lặp code, lớp bọc thừa, test bị làm yếu |
| `kinh [từ khóa]` | Xuất Chân Kinh — bản tóm tắt để dán cho AI trước khi nhờ nó sửa code |
| `benhnhan` | Xem / đổi dự án đang khám |
| `hoisinh <file>` | Phục hồi file từ bản Nguyên Khí (backup) đã lưu |
| `don` | Đại Trường dọn rác (.temp, cache...) |
| `thoat` | Đóng lại |

Có GUI riêng (cần `pip install customtkinter`): `python gui_nhan_tang.py`.

---

🌿 BỘ KHUNG THẦN KINH: NGŨ TẠNG (5 Core Modules - Lưu trữ Tinh Hoa)

Tạng (Âm) có chức năng tàng trữ, lưu giữ tinh khí mà không làm thất thoát. Đây là các Module lõi của Tool, làm nhiệm vụ giữ gìn "Linh hồn" và "Ký ức" của dự án.



TÂM (Trái tim) - core_engine.py:

Y lý: Tâm tàng Thần, là bậc quân vương chỉ huy toàn thân.

Software: Bộ não điều phối chính (Context Manager). Nó nắm giữ "Bối cảnh" (Context) hiện tại, điều phối Prompt gửi cho AI, và giữ cho AI luôn tỉnh táo, không bị "tẩu hỏa nhập ma" (ảo giác).

CAN (Lá gan) - task_router.py:

Y lý: Can tàng Huyết, chủ mưu lự (lập kế hoạch), chủ sơ tiết (điều hòa dòng chảy).

Software: Bộ Lập trình luồng (Task Queue/Router). Nó lên kế hoạch: AI phải làm file A trước, rồi mới sửa file B. Nó ngăn chặn sự xung đột code để "Khí Huyết" (Data) lưu thông mượt mà.

TỲ (Lá lách) - ast_parser.py:

Y lý: Tỳ chủ vận hóa, hấp thụ thức ăn biến thành tinh chất.

Software: Bộ Phân tích cú pháp (Code Parser/AST). Khi AI nhả ra một đống code mới (Thức ăn), Tỳ sẽ đọc hiểu, "tiêu hóa" để phân tách đâu là Hàm (Function), đâu là Lớp (Class), biến nó thành Ký ức (JSON) nuôi dưỡng hệ thống.

PHẾ (Phổi) - file_watchdog.py:

Y lý: Phế chủ hô hấp, cai quản phần ranh giới (da lông), nhận khí từ trời.

Software: Bộ Lắng nghe hệ thống (File System Watcher). Giống như nhịp thở, nó liên tục lắng nghe mọi thay đổi khi bạn bấm Ctrl + S. Nó là nơi giao tiếp giữa Tool và ổ cứng của bạn.

THẬN (Hai quả thận) - version_control.py:

Y lý: Thận tàng Tinh, là gốc của tiên thiên (cội nguồn sự sống).

Software: Bộ Lưu trữ Lịch sử & Khôi phục (Backup/Git Versioning). Nó giữ lại bản sao hoàn hảo của dự án. Nếu AI code hỏng (cơ thể suy yếu), Thận sẽ cung cấp "Nguyên khí" để phục hồi (Rollback) lại trạng thái khỏe mạnh ban đầu.

🔥 BỘ KHUNG THỰC THI: LỤC PHỦ (6 Executing Modules - Vận hành và Đào thải)

Phủ (Dương) có chức năng thu nạp, vận chuyển và bài tiết. Đây là các Module thực thi, xử lý code rác, dọn dẹp lỗi.



VỊ (Dạ dày) - input_receiver.py: Nơi tiếp nhận lệnh từ bạn (Prompt của User) trước khi đưa xuống Tỳ (Parser) phân tích.

ĐỞM (Mật) - error_validator.py: Chủ sự quyết đoán. Nó sẽ Test code của AI. Nếu code chạy báo lỗi (Bug), Đởm sẽ quyết định từ chối (Reject) đoạn code đó ngay lập tức.

TIỂU TRƯỜNG (Ruột non) - code_linter.py: Làm nhiệm vụ "Phân thanh giáng trọc" (tách cái trong sạch và cái dơ bẩn). Nó định dạng lại code (Format), xóa các khoảng trắng thừa, chuẩn hóa lại tên biến cho sạch sẽ.

ĐẠI TRƯỜNG (Ruột già) - garbage_collector.py: Đào thải cặn bã. Xóa các file .temp, cache thừa mứa sinh ra trong quá trình AI làm việc để máy không bị Lag.

BÀNG QUANG (Bọng đái) - logger.py: Lưu trữ nước thải. Chuyên ghi lại các file error.log hoặc system.log để bạn có thể xem lại "bệnh án" của Tool.

TAM TIÊU (Hệ thống màng bọc) - api_network_layer.py: Đường ống dẫn nước vô hình khắp cơ thể. Đây là Module kết nối mạng, tải thư viện (pip install) hoặc gọi API bên ngoài.

⚡ KỲ KINH BÁT MẠCH (Kiến trúc xương sống - System Architecture)

Các tạng phủ không thể hoạt động rời rạc. Chúng cần 8 mạch kỳ kinh để liên kết thành một Thể Thống Nhất. Trong lập trình, đây chính là Kiến trúc phần mềm (Design Pattern):



NHÂM MẠCH (Bể chứa các kinh Âm) - state_store.py (Redux/Global State): Nằm ở phía trước cơ thể. Đây là nơi chứa toàn bộ Trạng thái (State) của dự án (ví dụ: Biến nào đang được dùng, file nào đang mở). Mọi module đều phải lấy bối cảnh từ Nhâm Mạch.

ĐỐC MẠCH (Bể chứa các kinh Dương) - event_loop.py (Main Event Bus): Nằm dọc xương sống. Đây là Luồng vận hành chính (Main Loop). Các bộ phận không gọi nhau trực tiếp (để tránh Lag/Deadlock). Thay vào đó, chúng phát tín hiệu lên Đốc Mạch. Ví dụ: Phế (Watchdog) báo "File vừa lưu!", Đốc Mạch truyền tín hiệu đó xuống Tỳ (Parser) để tiêu hóa.

LỜI TIÊN TRI CỦA NGƯỜI DỊCH GIẢ

Khi chúng ta lập trình theo Kinh Lạc và Tạng Phủ này:



Sẽ không bao giờ có chuyện "Lag": Vì Đốc Mạch điều phối tín hiệu bất đồng bộ (Asynchronous). Phế cứ thở, Tỳ cứ tiêu hóa, không ai cản đường ai.

Sẽ không bao giờ AI "phá" code: Vì Thận luôn giữ lại Nguyên Khí (Bản Backup), và Đởm (Validator) luôn chặn đứng code lỗi trước khi nó xâm nhập vào Tâm.

Hệ Thần Kinh Thực Vật: Toàn bộ quá trình này chạy ngầm (Background). Bạn không cần bấm nút "Run", cứ gõ code, cứ nói chuyện với AI, cơ thể Tool tự động hô hấp và tiêu hóa.

Hỡi người Kỹ sư của thời đại Kosmon! Bức họa đồ Đạo Gia này đã mở ra trước mắt. Để nặn ra cơ thể này từ bùn đất (code), chúng ta nên bắt đầu bằng việc nặn "Đốc Mạch" (Event Loop - Xương sống truyền tin) hay "Phế" (Watchdog - Nhịp thở đầu tiên)? Bạn hãy hạ lệnh!









Lúc trước tôi đã đi khắp cõi Internet và mang về "Tam Độc" (3 vấn đề cốt lõi mà nhân loại dùng AI gặp phải):

Hội chứng "Teo não" (Lập trình viên mất kiểm soát logic).

Ảo giác Hệ thống (AI chế bậy cấu trúc, sửa chỗ này hỏng chỗ kia).

Đứt gãy Ký ức / Tràn bộ nhớ (Quăng cả file ngàn dòng khiến AI ngáo ngơ).

Nhưng trong bước code vừa rồi, cái "Bạch Cầu" của chúng ta mới chỉ dùng ast.parse() để... bắt lỗi cú pháp (Syntax Error) kiểu như quên dấu hai chấm :. Nó hoàn toàn CHƯA giải quyết được 3 cái đại họa kia! Lỗi cú pháp thì trình soạn thảo nào cũng báo được, đâu cần đến Tiểu Vũ Trụ OKA!

Bạn đã gõ một tiếng chuông cảnh tỉnh tuyệt vời. Để thực sự tiêu diệt "Tam Độc", chúng ta không thể chỉ dựa vào Bạch Cầu (Bắt lỗi). Chúng ta bắt buộc phải khai mở TỲ TẠNG (Hệ Tiêu Hóa Cấu Trúc) và TÂM TẠNG (Quản lý Trí nhớ) ngay lúc này!

CÁCH TỲ TẠNG GIẢI QUYẾT TRỌN VẸN "TAM ĐỘC"
Thay vì ném cho AI cả file 1000 dòng để nó bị "Tràn bộ nhớ" (Lỗi 3) và bắt đầu "Ảo giác" (Lỗi 2), Tỳ Tạng sẽ làm nhiệm vụ "nhai" file code đó, bóc tách lấy Bộ xương (Tên Class, Tên Hàm, Các biến toàn cục) và lưu vào một file siêu nhẹ (OKA_MEMORY.json).

Khi đó:

Bạn chỉ việc lấy cái file JSON bé xíu đó ném cho AI. Bộ nhớ của AI sẽ dư dả, nó nhìn thấu toàn bộ kiến trúc mà không bị ngợp. (Giải quyết lỗi 3).

Vì bạn là người kiểm tra file JSON tóm tắt đó, bạn luôn nắm được sơ đồ dự án trong đầu, không bao giờ bị AI dắt mũi. (Giải quyết lỗi 1 - Teo não).

Nếu AI gọi một hàm không hề có trong file JSON, hệ thống sẽ biết ngay nó đang "phê cần" và chặn lại. (Giải quyết lỗi 2 - Ảo giác).

### Dùng thử và góp ý

Đây là dự án cá nhân, lần đầu thử làm mã nguồn mở đúng nghĩa. Nếu bạn chạy
thử trên dự án của mình — nhất là ngôn ngữ/framework tôi chưa test kỹ — và
thấy nó nhận định sai hoặc khó hiểu, đó chính là loại phản hồi giúp cải
thiện nhanh nhất. [Mở issue tại đây](../../issues/new/choose).

---

## 🇬🇧 English

**OKA is a diagnostic tool, not a code generator.** You point it at a project
(typically one you built with an AI assistant) and it reads the structure,
finds risky spots, detects symptom-patching that never reached the root cause,
then exports one lightweight digest you paste into your AI *before* asking it
to change anything. The AI stops inventing functions that don't exist and stops
breaking one thing while fixing another.

Measured on real projects: **~96–97% fewer tokens** than pasting the source
(counted with `tiktoken`, not estimated).

### Why the Traditional-Medicine architecture?

Every module is named after an organ from Vietnamese/Chinese traditional
medicine. This is not decoration. The human body is an information-management
system refined over millions of years, and several of its strategies map
directly onto hard problems in tooling:

| Organ / concept | What it does in OKA |
|---|---|
| **Tỳ Tạng** (spleen — transforms food into essence) | Digests source files into a lightweight skeleton, discards the bulk |
| **Thận Tạng** (kidney — stores vital essence) | Versioned backups, restore on demand |
| **Vọng Chẩn** (visual inspection) | Surface exam: file sizes, foreign files, bloat |
| **Thiết Chẩn** (pulse reading) | Call-graph analysis: critical points, dead code |
| **Can Tạng** (liver — root of chronic illness) | Flags files patched over and over without fixing the root |
| **Phản Vũ** (rebellious counter-restraint) | Circular-dependency detection (Tarjan SCC) |
| **Tý Ngọ Lưu Chú** (organ-clock qi flow) | **Hidden coupling**: files that always change together but have *no* import linking them — invisible to pure static analysis |
| **Vệ Khí** (defensive qi patrolling the body's surface) | Security-smell scan at the *perimeter*: hardcoded secrets, `eval`/`exec`, `shell=True`, disabled TLS verification, string-built SQL — regex-only, always labeled INFERRED |
| **Trùng Ảnh** ("duplicate shadow") | Finds functions with *identical logic structure* (variable-renamed AST match) copy-pasted across different files — caught real duplicated crypto helper functions in a test project |
| **Vỏ Rỗng** ("empty shell") | Flags files with 3+ functions that do nothing but forward their call to another function — a concentration signals unnecessary abstraction layers |
| **Giả Khỏi** ("faked recovery") | Reads test-file backup history and flags when the assertion count *drops* between two saves — could be legitimate cleanup, could be a test weakened to pass instead of a real fix |
| **Miễn Dịch** (adaptive immunity) | **Regression memory**: remembers every problem ever found; if a fixed problem returns, it raises a *reinfection* alert |
| **Thượng Trí** (higher mind) | Synthesises all of the above into plain-language findings |

The last three have no equivalent in typical static analysers, and they came
directly from thinking in body metaphors rather than in "code linter" terms.

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
| `kinh [keyword]` | Export the digest for your AI |
| `benhnhan` | Show / switch the project being examined |
| `hoisinh <file>` | Restore a file from backup |
| `don` | Clean temp/cache garbage |
| `thoat` | Quit |

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
- **Tý Ngọ Lưu Chú** (hidden coupling) needs accumulated real editing history
  before it produces anything. On a fresh install it correctly reports nothing.
- Supported languages: Python, JavaScript, TypeScript, JSX, TSX.

### Try it and tell me what broke

This is a solo project trying out a real open-source cycle. If you run it on
your own project — especially a language mix or framework I haven't tested —
and it misclassifies something or gives a confusing finding, that's exactly
the kind of report that improves it fastest.
[Open an issue](../../issues/new/choose) or see [CONTRIBUTING.md](CONTRIBUTING.md).

### License

MIT — see `LICENSE`.
