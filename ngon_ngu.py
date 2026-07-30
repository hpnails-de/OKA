# ngon_ngu.py
# Đa ngôn ngữ - Việt / English
#
# Giữ mọi câu chữ giao diện ở MỘT chỗ. Trước đây chữ nằm rải rác khắp file
# GUI, muốn thêm một ngôn ngữ là phải lục từng dòng.
#
# Lưu ý cố ý: tên các Tạng Phủ (Tỳ, Tâm, Thiết Chẩn, Chân Kinh...) KHÔNG
# dịch sang tiếng Anh theo nghĩa đen mà giữ nguyên phiên âm kèm chú thích -
# đây là thuật ngữ riêng của hệ thống, dịch ra "Spleen Organ" thì vừa buồn
# cười vừa mất nghĩa. Cách này giống việc thế giới giữ nguyên "chi", "yin
# yang", "chakra" thay vì dịch.

import json
import os

TEP_CAI_DAT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "oka_ngon_ngu.json"
)

MAC_DINH = "vi"

BAN_DICH = {
    # ---------------- Giao diện chính ----------------
    "tieu_de_app": {
        "vi": "OKA — Thầy Thuốc Cho Code",
        "en": "OKA — The Physician for Code",
    },
    "phu_de": {
        "vi": "Thầy Thuốc Cho Code",
        "en": "The Physician for Code",
    },
    "mo_ta": {
        "vi": "Khám một dự án, xuất ra một file duy nhất để dán cho AI — "
              "giúp AI hiểu cấu trúc mà tốn rất ít token.",
        "en": "Diagnose a project and export a single file to paste into your "
              "AI — it grasps the structure at a fraction of the tokens.",
    },
    "chua_chon": {
        "vi": "Chưa chọn thư mục nào",
        "en": "No folder selected yet",
    },
    "nut_chon": {
        "vi": "📂  Chọn thư mục…",
        "en": "📂  Choose folder…",
    },
    "nut_dang_kham": {
        "vi": "⏳  Đang khám…",
        "en": "⏳  Examining…",
    },
    "hop_thoai_chon": {
        "vi": "Chọn thư mục dự án cần khám",
        "en": "Choose the project folder to examine",
    },

    # ---------------- Ô số liệu ----------------
    "o_so_file": {"vi": "File đã đọc", "en": "Files read"},
    "o_token_goc": {"vi": "Token nếu dán cả source", "en": "Tokens if pasting all source"},
    "o_token_moi": {"vi": "Token của Chân Kinh", "en": "Tokens of the digest"},
    "o_tiet_kiem": {"vi": "Tiết kiệm", "en": "Saved"},

    # ---------------- Trạng thái ----------------
    "bat_dau": {"vi": "Đang bắt đầu…", "en": "Starting…"},
    "b_nhai": {
        "vi": "Đang tiêu hóa dự án (Tỳ Tạng)…",
        "en": "Digesting the project (Ty Tang — the digester)…",
    },
    "b_kham": {
        "vi": "Đang nhìn sắc diện (Vọng Chẩn)…",
        "en": "Inspecting appearance (Vong Chan — visual exam)…",
    },
    "b_mach": {
        "vi": "Đang bắt mạch + tổng hợp (Thiết Chẩn + Thượng Trí)…",
        "en": "Reading the pulse + synthesising (Thiet Chan + Thuong Tri)…",
    },
    "b_goc": {
        "vi": "Đang soi gốc quá tải (Can Tạng)…",
        "en": "Looking for root overload (Can Tang — the liver)…",
    },
    "b_chan_kinh": {
        "vi": "Đang xuất Chân Kinh…",
        "en": "Exporting the digest…",
    },
    "b_mandala": {"vi": "Đang vẽ Mandala…", "en": "Drawing the Mandala…"},
    "da_luu": {"vi": "✅  Đã lưu:", "en": "✅  Saved:"},
    "co_loi": {"vi": "❌  Có lỗi xảy ra.", "en": "❌  Something went wrong."},

    # ---------------- Kết quả ----------------
    "cho_ket_qua": {
        "vi": "Kết quả chẩn đoán sẽ hiện ở đây.",
        "en": "Diagnosis results will appear here.",
    },
    "diem_chu_y": {"vi": "điểm cần chú ý:", "en": "points to note:"},
    "khong_rui_ro": {
        "vi": "✅  Không phát hiện rủi ro nổi bật.",
        "en": "✅  No notable risks found.",
    },
    "khong_to_hop": {
        "vi": "Không có tổ hợp rủi ro nào đáng báo động.",
        "en": "No risk combination worth alarming about.",
    },

    # ---------------- Nút chân trang ----------------
    "nut_mo_file": {"vi": "📄  Mở file báo cáo", "en": "📄  Open report file"},
    "nut_mo_thu_muc": {"vi": "📁  Mở thư mục", "en": "📁  Open folder"},
    "nut_chep": {
        "vi": "📋  Chép nội dung để dán cho AI",
        "en": "📋  Copy content to paste into AI",
    },
    "da_chep": {
        "vi": "✓  Đã chép! Dán cho AI ngay được",
        "en": "✓  Copied! Ready to paste into your AI",
    },
    "loi_doc_file": {
        "vi": "Không đọc được file báo cáo:",
        "en": "Could not read the report file:",
    },
    "loi_kham": {"vi": "Khám bệnh thất bại:", "en": "Examination failed:"},
    "loi": {"vi": "Lỗi", "en": "Error"},

    # ---------------- Tiêu đề báo cáo ----------------
    "bc_tieu_de": {
        "vi": "Báo cáo khám bệnh OKA",
        "en": "OKA diagnostic report",
    },
    "bc_huong_dan": {
        "vi": "Dán TOÀN BỘ file này cho AI trước khi nhờ nó sửa code trong dự án -\n"
              "AI sẽ biết trước cấu trúc thật, chỗ nào rủi ro, chỗ nào là rác,\n"
              "thay vì phải đọc lại từng file một.",
        "en": "Paste this ENTIRE file into your AI before asking it to change code -\n"
              "it will know the real structure, where the risks are and what is dead\n"
              "weight, instead of re-reading every file.",
    },
    "bc_so_do": {
        "vi": "Sơ đồ trực quan:",
        "en": "Visual diagram:",
    },
    "bc_mo_bang": {
        "vi": "(mở bằng trình duyệt)",
        "en": "(open in a browser)",
    },
    "bc_do_tin_cay": {
        "vi": "Mỗi nhận định có gắn nhãn độ tin cậy: **CHẮC CHẮN** = đếm được từ\n"
              "code, không cãi được; **SUY ĐOÁN** = dựa trên quy tắc phỏng đoán,\n"
              "cần tự kiểm lại trước khi hành động.",
        "en": "Every finding carries a confidence tag: **CERTAIN** = counted straight\n"
              "from the code, not arguable; **INFERRED** = based on heuristics, verify\n"
              "it yourself before acting on it.",
    },
}


def _doc_cai_dat():
    try:
        with open(TEP_CAI_DAT, "r", encoding="utf-8") as f:
            return json.load(f).get("ngon_ngu", MAC_DINH)
    except (OSError, json.JSONDecodeError, AttributeError):
        return MAC_DINH


_hien_tai = _doc_cai_dat()


def dat(ma):
    """Đổi ngôn ngữ và ghi nhớ cho lần chạy sau."""
    global _hien_tai
    if ma not in ("vi", "en"):
        return
    _hien_tai = ma
    try:
        with open(TEP_CAI_DAT, "w", encoding="utf-8") as f:
            json.dump({"ngon_ngu": ma}, f)
    except OSError:
        pass          # không ghi được thì vẫn đổi cho phiên hiện tại


def lay():
    return _hien_tai


def t(khoa):
    """Lấy câu chữ theo ngôn ngữ đang chọn.

    Thiếu bản dịch thì trả về chính khóa - hiện ra chữ lạ còn hơn là app
    vỡ vì KeyError.
    """
    muc = BAN_DICH.get(khoa)
    if not muc:
        return khoa
    return muc.get(_hien_tai) or muc.get(MAC_DINH) or khoa


# --- Bổ sung cho Xoắn Ốc Ký Ức ---
BAN_DICH.update({
    "xo_tieu_de": {
        "vi": "KÝ ỨC XOẮN ỐC (xa → gần, càng gần càng chi tiết)",
        "en": "SPIRAL MEMORY (far → near, detail increases toward the present)",
    },
    "xo_tang": {"vi": "Tầng", "en": "Tier"},
    "xo_luot": {"vi": "lượt", "en": "turns"},
    "xo_nguyen_van": {"vi": "nguyên văn", "en": "verbatim"},
    "xo_nen": {"vi": "nén còn ≤", "en": "compressed to ≤"},
    "xo_ky_tu": {"vi": "ký tự", "en": "chars"},
})
