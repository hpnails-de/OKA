# oka_phien.py
# CANH GIÁC PHIÊN — tự động "chuyển nhà" khi context sắp đầy
#
# ------------------------------------------------------------------
# BÀI TOÁN THẬT
# ------------------------------------------------------------------
# Context cũ được gửi lại từng lượt là điều không tránh được (cache đã
# làm nó rẻ), nhưng CONTEXT SỐNG phình mãi thì đắt thật: AI phải "chú ý"
# mọi thứ trong cửa sổ, dễ lost-in-the-middle, và phí output. Cách duy
# nhất là định kỳ CHUYỂN PHIÊN: nén phiên cũ thành ký ức, mở phiên mới
# với bản nén làm mở đầu.
#
# Vấn đề của cách làm tay: người dùng không biết phiên đang béo đến đâu,
# và khi chuyển nhà thì AI phiên mới NGƠ NGƠ vì bản tóm tắt thiếu thứ nó
# cần ngay (task đang dở, quyết định mới nhất, file đang sửa).
#
# Module này làm 2 việc:
#   1. do_lenh_phien(): đo phiên gần nhất của dự án (đọc bản ghi Claude
#      Code thật từ ~/.claude/projects/) - bao nhiêu lượt, nặng bao nhiêu
#      token, còn bao nhiêu % cửa sổ ngữ cảnh
#   2. khoan_chuyen_phien(): nếu vượt ngưỡng -> tự xuất bộ hành lý CHUYỂN
#      NHÀ gồm: ký ức xoắn ốc (quá trình) + Chân Kinh (cấu trúc) + khối
#      "bản giao phiến" nêu RÕ 3 lượt cuối - để phiên mới không ngơ ngơ.
#
# Cách dùng:
#   Python:  from oka_phien import do_lenh_phien, khoan_chuyen_phien
#   CLI:     python oka_phien.py [duong_dan_du_an]

import os
import sys

import oka_config as cfg
import xoan_oc_ky_uc
from tam_tang_core import uoc_luong_token
from ty_tang_parser import ty_tang_trung_uong

# Cửa sổ ngữ cảnh mặc định (token). Không cần chính xác - chỉ để tính %.
CUA_SO_MAC_DINH = 200_000

# Ngưỡng khuyến nghị chuyển phiên.
NGUONG_MAC_DINH = 0.70


def tim_phien_gan_nhat(duong_dan_du_an):
    """File .jsonl của phiên đang chạy/gần nhất trong thư mục dự án."""
    cac_tep = xoan_oc_ky_uc.tim_ban_ghi(duong_dan_du_an)
    return cac_tep[0] if cac_tep else None


def do_lenh_phien(duong_dan_du_an, cua_so=CUA_SO_MAC_DINH):
    """Đo sức béo của phiên gần nhất.

    Trả về dict: {tep, so_luot, token, phan_tram, muc, con_lai}
      muc: 'trang' (không có phiên) | 'xanh' | 'vang' | 'do'
    """
    tep = tim_phien_gan_nhat(duong_dan_du_an)
    if not tep:
        return {"muc": "trang", "so_luot": 0, "token": 0,
                "phan_tram": 0.0, "con_lai": cua_so, "tep": None}

    so_luot = 0
    ky_tu = 0
    with open(tep, "r", encoding="utf-8", errors="replace") as f:
        for dong in f:
            if '"type"' in dong and ('"user"' in dong or '"assistant"' in dong):
                so_luot += 1
            ky_tu += len(dong)
    token = uoc_luong_token("a" * ky_tu)  # ước lượng thô nhưng nhất quán
    phan_tram = token / cua_so * 100

    if phan_tram >= 90:
        muc = "do"
    elif phan_tram >= NGUONG_MAC_DINH * 100:
        muc = "vang"
    else:
        muc = "xanh"

    return {"tep": tep, "so_luot": so_luot, "token": token,
            "phan_tram": phan_tram, "con_lai": max(0, cua_so - token),
            "muc": muc}


def _con_cuoi_cung(duong_dan_jsonl, so_luot=3):
    """Lấy N lượt CÓ CHỮ thật cuối cùng — thứ phiên mới cần NHẤT để không
    ngơ ngơ: task đang dở đến đâu, quyết định cuối là gì."""
    su_kien = xoan_oc_ky_uc.doc_su_kien(duong_dan_jsonl)
    return "\n\n".join(
        f"[{sk['vai']}] {sk['noi_dung'][:400]}" for sk in su_kien[-so_luot:]
    )


def khoan_chuyen_phien(duong_dan_du_an, cua_so=CUA_SO_MAC_DINH,
                       nguong=NGUONG_MAC_DINH):
    """Kiểm tra phiên. Vượt ngưỡng -> tạo bộ hành lý chuyển nhà.

    Trả về (can_chuyen, bao_cao):
      can_chuyen=False: phiên còn khỏe / không có gì để đo
      can_chuyen=True : đã xuất OKA_KY_UC + OKA_CHAN_KINH, bao_cao là
                        khối dán thẳng cho phiên mới
    """
    do_lenh = do_lenh_phien(duong_dan_du_an, cua_so)
    tep = do_lenh["tep"]

    if tep is None:
        return False, (f"ℹ️ Chưa có phiên Claude Code nào trong "
                       f"'{duong_dan_du_an}'. Không có gì để đo.")

    if do_lenh["phan_tram"] < nguong * 100:
        return False, (
            f"🟢 Phiên còn khỏe: {do_lenh['so_luot']:,} lượt, "
            f"~{do_lenh['token']:,} token "
            f"({do_lenh['phan_tram']:.0f}% cửa sổ {cua_so:,}). "
            "Chưa cần chuyển nhà.")

    # --- Vượt ngưỡng: dựng hành lý ---
    ten = os.path.basename(os.path.normpath(duong_dan_du_an))

    # 1) Ký ức xoắn ốc - QUÁ TRÌNH làm việc (gộp mọi phiên)
    ky_uc_van_ban, tk = xoan_oc_ky_uc.dung_tu_du_an(
        duong_dan_du_an, gop_moi_phien=True
    )
    duong_ky_uc = None
    if ky_uc_van_ban:
        duong_ky_uc = os.path.join(duong_dan_du_an, f"OKA_KY_UC_{ten}.md")
        with open(duong_ky_uc, "w", encoding="utf-8") as f:
            f.write(ky_uc_van_ban)

    # 2) Chân Kinh - CẤU TRÚC code hiện tại
    ky_uc = ty_tang_trung_uong.tai_ky_uc(duong_dan_du_an)
    if not ky_uc.get("files"):
        ty_tang_trung_uong.tieu_hoa_toan_bo(duong_dan_du_an)
    from tam_tang_core import tam_tang_trung_uong as tam
    chan_kinh = tam.xuat_chan_kinh_cho_ai(duong_dan_du_an)
    duong_chan_kinh = os.path.join(duong_dan_du_an, f"OKA_CHAN_KINH_{ten}.md")
    with open(duong_chan_kinh, "w", encoding="utf-8") as f:
        f.write(chan_kinh)

    # 3) Bản giao phiến - lượt cuối có chữ thật, thứ phiên mới cần nhất
    ban_giao = _con_cuoi_cung(tep)

    bao_cao = (
        f"🔴 PHIÊN ĐÃ BÉO: {do_lenh['so_luot']:,} lượt, "
        f"~{do_lenh['token']:,} token ({do_lenh['phan_tram']:.0f}% cửa sổ).\n\n"
        "### 🧳 HÀNH LÝ CHUYỂN PHIÊN ###\n"
        f"1. Mở chat MỚI, dán file: {duong_chan_kinh}\n"
    )
    if duong_ky_uc:
        bao_cao += f"2. Dán thêm (nếu cần mạch việc): {duong_ky_uc}\n"
    bao_cao += (
        "\n### 📌 BẢN GIAO PHIẾN (3 lượt cuối - dán NGAY SAU hành lý) ###\n"
        f"{ban_giao}\n\n"
        "[Chuyển tiếp từ phiên trước. Bám sát file hành lý ở trên - mọi "
        "tên class/hàm trong đó là CÓ THẬT. Tiếp tục từ đúng chỗ đang dở, "
        "đừng làm lại từ đầu.]"
    )
    return True, bao_cao


if __name__ == "__main__":
    du_an = sys.argv[1] if len(sys.argv) > 1 else cfg.benh_nhan_hien_tai()
    can_chuyen, bao_cao = khoan_chuyen_phien(du_an)
    print(bao_cao)
    sys.exit(2 if can_chuyen else 0)