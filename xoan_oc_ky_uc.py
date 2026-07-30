# xoan_oc_ky_uc.py
# XOẮN ỐC KÝ ỨC - giữ được ngữ cảnh TỪ ĐẦU ĐẾN CUỐI mà không phình token
#
# ------------------------------------------------------------------
# BÀI TOÁN THẬT
# ------------------------------------------------------------------
# Hội thoại với AI dài ra thì cửa sổ ngữ cảnh đầy. Cách xử lý phổ biến
# hiện nay có hai lối, cả hai đều dở:
#   CẮT PHẮNG  - vứt hẳn phần cũ. Mất sạch, không cứu được.
#   TÓM MỘT CỤC - nén toàn bộ quá khứ thành một đoạn tóm tắt duy nhất.
#       Đỡ hơn, nhưng mọi thứ bị nén ĐỀU NHAU: chuyện 5 phút trước và
#       chuyện 5 tiếng trước cùng bị bóp thành một dòng như nhau.
#
# Trí nhớ người KHÔNG hoạt động vậy. Hôm qua thì nhớ từng giờ, tuần
# trước nhớ từng ngày, năm ngoái nhớ từng tháng. Độ chi tiết giảm dần
# theo hàm mũ khi lùi về quá khứ - chứ không cắt phựt, cũng không đều.
#
# ------------------------------------------------------------------
# XOẮN ỐC FIBONACCI GIẢI BÀI TOÁN NÀY THẾ NÀO
# ------------------------------------------------------------------
# Đặc tính hình học của xoắn ốc vàng: mỗi vòng phủ diện tích lớn gấp
# φ lần vòng trước, NHƯNG vẫn chỉ chiếm cùng một góc quét. Nghĩa là
# vòng ngoài ôm được vùng rộng hơn rất nhiều mà "không tốn thêm chỗ".
#
# Áp vào ký ức: chia quá khứ thành các TẦNG có kích thước Fibonacci
# (1, 1, 2, 3, 5, 8, 13, 21, 34...) tính từ hiện tại lùi về, rồi cho
# MỖI TẦNG cùng một hạn mức token.
#
#   Tầng 0 (mới nhất, 1 lượt)   -> giữ nguyên văn
#   Tầng 1 (1 lượt trước đó)    -> giữ nguyên văn
#   Tầng 2 (2 lượt)             -> nén nhẹ
#   Tầng 3 (3 lượt)             -> nén vừa
#   Tầng 8 (21 lượt)            -> chỉ còn các mốc chính
#   Tầng 15 (610 lượt)          -> chỉ còn vài từ khóa
#
# HỆ QUẢ TOÁN HỌC - đây mới là chỗ đắt:
# Fibonacci tăng theo hàm mũ (F(n) ≈ φⁿ/√5), nên số tầng cần để phủ
# N lượt chỉ là O(log_φ N). Với 6000 lượt chỉ cần ~18 tầng. Mỗi tầng
# ~200 token thì TOÀN BỘ hội thoại 6000 lượt gói trong ~3600 token,
# mà vẫn còn dấu vết của lượt đầu tiên.
#
# Nói cho công bằng: cái làm nên hiệu quả ở đây là NGUYÊN LÝ NÉN
# THEO HÀM LOG của quá khứ, không phải phép màu của con số Fibonacci.
# Dãy 1,2,4,8,16 (lũy thừa 2) cũng cho kết quả tương tự. Fibonacci
# được chọn vì tỷ lệ φ ≈ 1.618 tăng CHẬM HƠN gấp đôi, nên chuyển tiếp
# giữa các tầng mượt hơn - chi tiết mất dần chứ không rơi đột ngột.

import re
import os
import json
import glob

try:
    from ngon_ngu import t
except Exception:                      # dùng độc lập, không có ngon_ngu
    def t(khoa):
        return {
            "xo_tieu_de": "KÝ ỨC XOẮN ỐC (xa → gần, càng gần càng chi tiết)",
            "xo_tang": "Tầng", "xo_luot": "lượt", "xo_nguyen_van": "nguyên văn",
            "xo_nen": "nén còn ≤", "xo_ky_tu": "ký tự",
        }.get(khoa, khoa)


def day_fibonacci(tong_can_phu):
    """Sinh dãy Fibonacci vừa đủ phủ hết số lượt cần nhớ."""
    day = [1, 1]
    while sum(day) < tong_can_phu:
        day.append(day[-1] + day[-2])
    return day


def chia_tang(su_kien):
    """Chia danh sách sự kiện thành các tầng Fibonacci, MỚI NHẤT trước.

    Trả về [(chi_so_tang, [su_kien...]), ...] với tầng 0 là mới nhất.
    """
    con_lai = list(su_kien)
    cac_tang = []
    for i, kich_thuoc in enumerate(day_fibonacci(len(con_lai))):
        if not con_lai:
            break
        lay = con_lai[-kich_thuoc:] if kich_thuoc <= len(con_lai) else con_lai
        con_lai = con_lai[: len(con_lai) - len(lay)]
        cac_tang.append((i, lay))
    return cac_tang


# --- Nhận diện câu "có tín hiệu" để giữ lại khi nén ---
_TIN_HIEU = re.compile(
    r"("
    r"[A-Za-z]:\\[^\s]+|/[a-z]+/[^\s]+"        # đường dẫn file
    r"|\b\w+\.(py|js|jsx|ts|tsx|md|json)\b"     # tên file
    r"|\bbug\b|\blỗi\b|\bsửa\b|\bfix\b|\bsai\b" # sửa lỗi
    r"|\bquyết định\b|\bchọn\b|\bđổi\b"          # quyết định
    r"|\d[\d.,]*\s*(%|token|MH/s|file|dòng)"    # số liệu
    r")", re.IGNORECASE,
)


def _cham_diem(cau):
    """Câu càng nhiều tín hiệu càng đáng giữ khi nén."""
    return len(_TIN_HIEU.findall(cau))


def nen(van_ban, han_muc_ky_tu):
    """Nén một đoạn về hạn mức, ưu tiên giữ câu nhiều tín hiệu.

    Không gọi LLM, không cần thư viện - đúng nguyên tắc không-cài-đặt
    của cả dự án. Đây là nén TRÍCH CHỌN (extractive): chọn ra câu đáng
    giữ nhất, chứ không viết lại.
    """
    van_ban = re.sub(r"\s+", " ", van_ban).strip()
    if len(van_ban) <= han_muc_ky_tu:
        return van_ban

    cau = re.split(r"(?<=[.!?\n])\s+", van_ban)
    # Giữ thứ tự gốc nhưng chọn theo điểm: xếp hạng rồi sắp lại theo vị trí
    xep = sorted(
        enumerate(cau), key=lambda x: (-_cham_diem(x[1]), len(x[1]))
    )
    chon, do_dai = [], 0
    for vi_tri, c in xep:
        if do_dai + len(c) > han_muc_ky_tu:
            continue
        chon.append((vi_tri, c))
        do_dai += len(c) + 1
        if do_dai >= han_muc_ky_tu * 0.9:
            break

    if not chon:
        return van_ban[:han_muc_ky_tu] + "…"
    return " ".join(c for _, c in sorted(chon))


def dung_ky_uc(su_kien, han_muc_moi_tang=600, so_tang_nguyen_van=2):
    """Dựng ký ức xoắn ốc.

    su_kien: list dict {'vai': 'user'/'assistant', 'noi_dung': str}
             theo thứ tự thời gian (cũ -> mới).
    han_muc_moi_tang: số ký tự tối đa cho mỗi tầng.
    so_tang_nguyen_van: mấy tầng mới nhất giữ nguyên văn.

    Trả về (van_ban_ky_uc, thong_ke)
    """
    if not su_kien:
        return "", {"so_tang": 0, "so_su_kien": 0}

    cac_tang = chia_tang(su_kien)
    khoi = []

    for chi_so, nhom in cac_tang:
        gop = "\n".join(
            f"[{sk.get('vai', '?')}] {sk.get('noi_dung', '')}" for sk in nhom
        )
        if chi_so < so_tang_nguyen_van:
            than = gop
            nhan = t("xo_nguyen_van")
        else:
            # MỖI TẦNG CÙNG MỘT HẠN MỨC - đây mới đúng hình học xoắn ốc:
            # mỗi vòng phủ vùng rộng gấp φ lần nhưng chiếm CÙNG một góc quét.
            #
            # Bản đầu tôi cho hạn mức GIẢM dần theo độ cũ, thành ra phạt kép:
            # tầng xa vốn đã chứa nhiều nội dung hơn lại còn bị bóp chặt hơn.
            # Đo trên hội thoại thật: 709 lượt bị nén còn 118 ký tự, ra toàn
            # mảnh vụn rời rạc, vô dụng. Hạn mức đều thì tầng xa vẫn được
            # nguyên một đoạn văn - nén mạnh nhưng còn đọc hiểu được.
            than = nen(gop, han_muc_moi_tang)
            nhan = f'{t("xo_nen")}{han_muc_moi_tang} {t("xo_ky_tu")}'
        khoi.append((chi_so, len(nhom), nhan, than))

    # In từ XA tới GẦN để đọc theo dòng thời gian tự nhiên
    dong = [f'### 🌀 {t("xo_tieu_de")} ###', ""]
    for chi_so, so_sk, nhan, than in reversed(khoi):
        dong.append(f'┈┈ {t("xo_tang")} {chi_so} · {so_sk} {t("xo_luot")} · {nhan} ┈┈')
        dong.append(than)
        dong.append("")

    thong_ke = {
        "so_tang": len(cac_tang),
        "so_su_kien": len(su_kien),
        "ky_tu_goc": sum(len(sk.get("noi_dung", "")) for sk in su_kien),
    }
    van_ban = "\n".join(dong)
    thong_ke["ky_tu_ky_uc"] = len(van_ban)
    return van_ban, thong_ke


# ====================================================================
# ĐỌC BẢN GHI HỘI THOẠI THẬT
#
# Claude Code lưu bản ghi mỗi dự án tại ~/.claude/projects/<slug>/*.jsonl
# với slug = đường dẫn dự án, mọi ký tự không phải chữ/số đổi thành '-'.
#   E:\backup4.2026\OKA_System   ->  E--backup4-2026-OKA-System
#   C:\Projects_tool\TOOL_X      ->  C--Projects-tool-TOOL-X
# ====================================================================

def _slug_du_an(duong_dan_du_an):
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(duong_dan_du_an))


def tim_ban_ghi(duong_dan_du_an):
    """Tìm các file .jsonl bản ghi hội thoại của một dự án.

    Trả về list đường dẫn, mới nhất trước. Rỗng nếu chưa có phiên nào.
    """
    goc = os.path.join(os.path.expanduser("~"), ".claude", "projects")
    thu_muc = os.path.join(goc, _slug_du_an(duong_dan_du_an))
    if not os.path.isdir(thu_muc):
        return []
    tep = glob.glob(os.path.join(thu_muc, "*.jsonl"))
    return sorted(tep, key=os.path.getmtime, reverse=True)


def _lay_chu(noi_dung):
    """Rút phần chữ từ trường content (str, hoặc list các khối)."""
    if isinstance(noi_dung, str):
        return noi_dung
    if isinstance(noi_dung, list):
        manh = []
        for b in noi_dung:
            if isinstance(b, str):
                manh.append(b)
            elif isinstance(b, dict):
                if b.get("type") == "text":
                    manh.append(b.get("text", ""))
                elif b.get("type") == "tool_use":
                    manh.append(f"[dùng công cụ {b.get('name', '?')}]")
                elif b.get("type") == "tool_result":
                    manh.append("[kết quả công cụ]")
        return " ".join(manh)
    return ""


def doc_su_kien(duong_dan_jsonl):
    """Đọc một file bản ghi -> list sự kiện theo thứ tự thời gian."""
    su_kien = []
    try:
        f = open(duong_dan_jsonl, encoding="utf-8", errors="replace")
    except OSError:
        return su_kien
    with f:
        for dong in f:
            try:
                d = json.loads(dong)
            except (json.JSONDecodeError, ValueError):
                continue
            if d.get("type") not in ("user", "assistant"):
                continue
            msg = d.get("message") or {}
            chu = _lay_chu(msg.get("content", d.get("content", ""))).strip()
            if chu:
                su_kien.append({"vai": d["type"], "noi_dung": chu})
    return su_kien


def dung_tu_du_an(duong_dan_du_an, han_muc_moi_tang=700,
                  so_tang_nguyen_van=2, gop_moi_phien=True):
    """Dựng ký ức xoắn ốc từ bản ghi hội thoại THẬT của một dự án.

    gop_moi_phien=True thì gộp tất cả các phiên lại theo thời gian, để
    nhớ được cả những phiên trước chứ không riêng phiên gần nhất.

    Trả về (van_ban, thong_ke) - van_ban rỗng nếu không tìm thấy bản ghi.
    """
    cac_tep = tim_ban_ghi(duong_dan_du_an)
    if not cac_tep:
        return "", {"so_tang": 0, "so_su_kien": 0, "so_phien": 0}

    if not gop_moi_phien:
        cac_tep = cac_tep[:1]

    su_kien = []
    # Đọc từ phiên CŨ nhất trước để dòng thời gian đúng chiều
    for tep in reversed(cac_tep):
        su_kien.extend(doc_su_kien(tep))

    van_ban, thong_ke = dung_ky_uc(
        su_kien, han_muc_moi_tang=han_muc_moi_tang,
        so_tang_nguyen_van=so_tang_nguyen_van,
    )
    thong_ke["so_phien"] = len(cac_tep)
    return van_ban, thong_ke
