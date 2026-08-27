# oka_query.py
# TRUY VẤN THEO NHIỆM VỤ — bản nâng cấp "lấy đúng liều" của Chân Kinh
#
# ------------------------------------------------------------------
# BÀI TOÁN THẬT
# ------------------------------------------------------------------
# Chân Kinh nén TOÀN BỘ dự án thành 1 file để AI đọc luôn. Tốt cho người
# đọc định hướng, nhưng khi AI nhận 1 NHIỆM VỤ cụ thể (sửa 1 hàm trong
# 1 file) thì phần lớn nội dung là nhiễu: token phí, và cả đống tên hàm
# lạ khiến AI dễ chọn nhầm API. Kém hơn nữa: nếu KHÔNG có context nào,
# AI sẽ tự mò đọc 5-10 file (mỗi file 5-7k token) — chi phí vô hình.
#
# Giải pháp ở đây: AI đưa YÊU CẦU (câu hỏi / mô tả nhiệm vụ), module này:
#   1. Tách từ khóa, chấm điểm từng file theo độ khớp — chấm ngay trên
#      ký ức Tỳ Tạng đã có, KHÔNG đọc lại file để chấm
#   2. Trả về CHỈ các file liên quan: chữ ký hàm đầy đủ + các nơi gọi
#      hàm được nhắc tới + ĐOẠN CODE THẬT quanh vị trí khớp
#   3. Đo thống kê: tốn bao nhiêu token so với dán nguyên source
#
# Không cài gì thêm, không gọi LLM — đúng nguyên tắc của cả dự án.
#
# Cách dùng:
#   Python:  from oka_query import hoi; van_ban, tk = hoi("sửa boc_tach", r"C:\du_an")
#   CLI:     python oka_query.py "sửa lỗi trong boc_tach" "D:\du_an_cua_ban"

import os
import re
import sys
import unicodedata

import oka_config as cfg
from tam_tang_core import uoc_luong_token
from ty_tang_parser import ty_tang_trung_uong

try:
    from thiet_chan_pulse import thiet_chan_trung_uong
except Exception:
    thiet_chan_trung_uong = None

# Từ quá phổ biến — bỏ, không giúp định vị gì
_STOP = {
    "the", "and", "for", "with", "this", "that", "from", "into", "self",
    "của", "cho", "và", "trong", "làm", "sửa", "thêm", "xóa", "đổi",
    "hàm", "file", "dòng", "nhờ", "giúp", "lỗi", "bug", "code", "tôi",
    "muốn", "cần", "hãy", "một", "các", "những", "được", "khi", "để",
    "thành", "vào", "ra", "lại", "này", "đó", "nào", "check", "fix",
    "where", "what", "how", "please", "which", "tìm", "xem",
    "sua", "ham", "them", "xoa", "doi", "loi", "class", "def", "method",
}

_TU = re.compile(r"[A-Za-z_$][\w$]*")


def dam_bao_da_nhai(benh_nhan):
    """Ký ức rỗng thì tự nhai trọn dự án một lượt (như MCP server đã làm)."""
    ky_uc = ty_tang_trung_uong.tai_ky_uc(benh_nhan)
    if not ky_uc.get("files"):
        ky_uc = ty_tang_trung_uong.tieu_hoa_toan_bo(benh_nhan)
    return ky_uc


def bo_dau(van_ban):
    """Bỏ dấu tiếng Việt: 'bóc tách' -> 'boc tach'. Dùng NFD rồi thải
    ký tự combining - cách chuẩn không cần thư viện ngoài."""
    return "".join(
        c for c in unicodedata.normalize("NFD", van_ban)
        if unicodedata.category(c) != "Mn"
    )


def tach_tu_khoa(cau_hoi):
    """Tách từ khóa từ câu hỏi.

    BỎ DẤU TRƯỚC khi tách, để 'bóc tách' (có dấu) ra được 'boc', 'tach'
    và khớp được với định danh ASCII trong code. Chỉ giữ định danh dài
    hơn 2 ký tự, bỏ stopword."""
    khong_dau = bo_dau(cau_hoi)
    return [t for t in _TU.findall(khong_dau)
            if len(t) > 2 and t.lower() not in _STOP]


def _chua_tu(loi, tu):
    """`loi` có chứa `tu` như một từ riêng không — theo ranh giới định danh.

    'nang' KHÔNG khớp 'cum_chuc_nang' (dấu _ chặn), nhưng 'boc' khớp
    'boc_tach' (đầu chuỗi). Đây là cách sửa bug khớp nhầm substring. """
    return re.search(rf"(?<![a-z0-9_]){re.escape(tu)}", loi) is not None


def cham_diem_file(ten_khoa, tinh_hoa, tu_khoa):
    """Điểm khớp của một file với bộ từ khóa — chấm trên ký ức, KHÔNG đọc file.

    - Trùng nguyên tên file (có/không đuôi): +10
    - Trùng tên class: +8
    - Trùng tên hàm (module-level hoặc method trong class): +6
    - Tên file CHỨA từ khóa (ranh giới định danh): +5 """
    # Gom MỌI tên định nghĩa được: hàm module-level + method trong class
    cac_ten_ham = set(tinh_hoa.get("ham", {}))
    for than_cls in tinh_hoa.get("classes", {}).values():
        cac_ten_ham.update(than_cls.get("methods", {}))

    diem = 0
    ten_thap = ten_khoa.lower()
    ten_khong_duoi = os.path.splitext(ten_thap)[0]

    for tu in tu_khoa:
        t = tu.lower()
        if t == ten_thap or t == ten_khong_duoi:
            diem += 10
        elif _chua_tu(ten_thap, t):
            diem += 5
        elif t in tinh_hoa.get("classes", {}):
            diem += 8
        elif t in cac_ten_ham:
            diem += 6
    return diem


def trich_doan_code(duong_dan_file, tu_khoa, so_doan=3, dong_xung_quanh=3):
    """Đọc file thật, trích các đoạn code quanh dòng chứa từ khóa.

    Trả về [(so_dong_bat_dau, doan_code), ...] — tối đa so_doan đoạn,
    mỗi đoạn 2*dong_xung_quanh+1 dòng. Đây là lần DUY NHẤT module này
    đọc file, và chỉ đọc những file đã được chấm điểm là liên quan.
    """
    if not os.path.isfile(duong_dan_file):
        return []
    try:
        with open(duong_dan_file, "r", encoding="utf-8", errors="replace") as f:
            dong = f.readlines()
    except OSError:
        return []

    mau = [t.lower() for t in tu_khoa]
    ket_qua = []
    da_lay = set()

    for i, mot_dong in enumerate(dong):
        if len(ket_qua) >= so_doan:
            break
        duoi = mot_dong.lower()
        if not any(t in duoi for t in mau):
            continue
        dau = max(0, i - dong_xung_quanh)
        if any(dau <= d for d in da_lay):
            continue
        cuoi = min(len(dong), i + dong_xung_quanh + 1)
        khuc = "".join(dong[dau:cuoi]).rstrip()
        ket_qua.append((dau + 1, khuc))
        da_lay.add(dau)

    return ket_qua


def _nguoi_goi_cua(ten, mach):
    """Các file đang gọi `ten` — từ đồ thị Thiết Chẩn (đã dựng từ ký ức)."""
    return sorted(set(mach.get("nguoi_goi", {}).get(ten, [])))


def hoi(cau_hoi, benh_nhan=None, gioi_han_file=3, dong_xung_quanh=3):
    """API chính: trả về khối context gọn cho MỘT yêu cầu cụ thể.

    Trả về (van_ban, thong_ke):
      van_ban — chuỗi dán thẳng cho AI
      thong_ke — {tu_khoa, file_chon, token_context, token_source, giam}
    """
    benh_nhan = os.path.abspath(benh_nhan or cfg.benh_nhan_hien_tai())
    if not os.path.isdir(benh_nhan):
        return "", {"loi": f"Không tìm thấy thư mục '{benh_nhan}'"}

    ky_uc = dam_bao_da_nhai(benh_nhan)
    files = ky_uc.get("files", {})
    if not files:
        return "", {"loi": "Ký ức rỗng, không nhai được dự án."}

    tu_khoa = tach_tu_khoa(cau_hoi)
    if not tu_khoa:
        return "", {"loi": "Câu hỏi không có từ khóa định vị nào."}

    # 1) Chấm điểm trên ký ức, chọn top file
    bang_diem = []
    for khoa, tinh_hoa in files.items():
        d = cham_diem_file(khoa, tinh_hoa, tu_khoa)
        if d > 0:
            bang_diem.append((d, khoa, tinh_hoa))
    bang_diem.sort(key=lambda x: (-x[0], x[1]))
    top = bang_diem[:gioi_han_file]
    if not top:
        return "", {"loi": "Không file nào khớp từ khóa: "
                           + ", ".join(sorted(tu_khoa))}

    # 2) Các nơi gọi những hàm được nhắc tới (mượn máy Thiết Chẩn)
    nguoi_goi = {}
    if thiet_chan_trung_uong is not None:
        try:
            mach = thiet_chan_trung_uong.dung_mach_do(benh_nhan)
            for tu in tu_khoa:
                cac_noi = _nguoi_goi_cua(tu, mach)
                if cac_noi:
                    nguoi_goi[tu] = cac_noi
        except Exception:
            pass

    # 3) Dựng khối context
    khoi = [
        "### 🎯 CONTEXT CHO NHIỆM VỤ ###",
        f"Yêu cầu: {cau_hoi.strip()}",
        "Đây là CHỈ những phần của dự án liên quan tới yêu cầu. Mọi tên",
        "class/hàm dưới đây là CÓ THẬT và ĐANG TỒN TẠI — không được bịa tên khác.",
        "",
    ]

    for diem, khoa, tinh_hoa in top:
        khoi.append(f"📂 {khoa}  ({tinh_hoa.get('dong', '?')} dòng, điểm khớp {diem})")
        for ten_cls, than in tinh_hoa.get("classes", {}).items():
            ke_thua = "".join(f"({k})" for k in than.get("ke_thua", []))
            khoi.append(f"   ▸ class {ten_cls}{ke_thua}")
            for ten_m, chu_ky in than.get("methods", {}).items():
                khoi.append(f"       - {ten_m}{chu_ky}")
        for ten_ham, chu_ky in tinh_hoa.get("ham", {}).items():
            khoi.append(f"   ▸ def {ten_ham}{chu_ky}")
        khoi.append("")

        duong_dan_day = os.path.join(benh_nhan, khoa.replace("/", os.sep))
        doan = trich_doan_code(duong_dan_day, tu_khoa, dong_xung_quanh=dong_xung_quanh)
        if doan:
            khoi.append("   ── đoạn code liên quan ──")
            for so, khuc in doan:
                khoi.append(f"   [dòng {so}]")
                for d in khuc.splitlines():
                    khoi.append(f"   {d}")
            khoi.append("")

    if nguoi_goi:
        khoi.append("── AI GỌI AI (các nơi gọi những tên được nhắc tới) ──")
        for ten, cac_noi in sorted(nguoi_goi.items()):
            khoi.append(f"   {ten}() đang được gọi tại: {', '.join(cac_noi)}")
        khoi.append("")

    khoi.append("[NHIỆM VỤ]: Bám sát code trên khi thực hiện yêu cầu. Tên không")
    khoi.append("có trong đây mà cần dùng thì phải nói rõ là tạo mới.")

    van_ban = "\n".join(khoi)

    # 4) Thống kê công lực
    token_context = uoc_luong_token(van_ban)
    token_source = 0
    for khoa in files:
        duong_dan_day = os.path.join(benh_nhan, khoa.replace("/", os.sep))
        try:
            with open(duong_dan_day, "r", encoding="utf-8", errors="replace") as f:
                token_source += uoc_luong_token(f.read())
        except OSError:
            pass
    giam = (1 - token_context / max(1, token_source)) * 100

    thong_ke = {
        "tu_khoa": tu_khoa,
        "file_chon": [k for _, k, _ in top],
        "token_context": token_context,
        "token_source": token_source,
        "giam": giam,
    }
    return van_ban, thong_ke


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Cú pháp: python oka_query.py "câu hỏi / yêu cầu" [đường_dẫn_dự_án]')
        sys.exit(1)

    cau_hoi = sys.argv[1]
    bn = sys.argv[2] if len(sys.argv) > 2 else cfg.benh_nhan_hien_tai()

    van_ban, tk = hoi(cau_hoi, bn)
    if not van_ban:
        print(f"❌ {tk.get('loi', 'Không tạo được context.')}")
        sys.exit(1)

    print(van_ban)
    print("\n" + "─" * 60)
    print(f"📊 {tk['token_context']:,} token context / {tk['token_source']:,} token source "
          f"= giảm {tk['giam']:.1f}%")
    print(f"   File chọn: {', '.join(tk['file_chon'])}")