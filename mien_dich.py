# mien_dich.py
# HỆ MIỄN DỊCH - trí nhớ kháng thể, chống TÁI NHIỄM
#
# ------------------------------------------------------------------
# Y LÝ
# ------------------------------------------------------------------
# Cơ thể có hai tuyến phòng thủ:
#   MIỄN DỊCH BẨM SINH - gặp lạ là đánh, không cần biết là ai. Nhanh
#       nhưng không học được gì. (Tương đương: Vọng Chẩn, Thiết Chẩn -
#       mỗi lần khám là soi lại từ đầu, không nhớ lần trước.)
#   MIỄN DỊCH THÍCH ỨNG - GHI NHỚ mầm bệnh đã gặp. Lần sau cùng loại
#       xâm nhập, tế bào nhớ nhận ra ngay và phản ứng mạnh hơn nhiều.
#       Đây chính là nguyên lý của vắc-xin.
#
# ------------------------------------------------------------------
# BÀI TOÁN THẬT
# ------------------------------------------------------------------
# Đây đúng là bài toán gốc mà tool này sinh ra để giải: "AI làm lúc đầu
# thì ổn, dự án lớn lên thì nó sửa chỗ này hỏng chỗ kia".
#
# Cái tệ nhất không phải lỗi mới - mà là lỗi CŨ QUAY LẠI. Bạn đã sửa
# một vấn đề, vài tuần sau nhờ AI làm việc khác, nó vô tình dựng lại y
# hệt vấn đề đó. Không ai nhớ nổi "cái này từng sửa rồi" - kể cả bạn,
# kể cả AI (AI không có ký ức giữa các phiên).
#
# Mọi công cụ phân tích tĩnh đều CHỈ NHÌN HIỆN TẠI. Chúng không thể
# nói "vấn đề này từng bị sửa rồi, nay quay lại".
#
# Hệ Miễn Dịch ghi lại mọi vấn đề Thượng Trí từng phát hiện dưới dạng
# "kháng thể" (một dấu vân tay của vấn đề). Sau này:
#   - Vấn đề biến mất  -> đánh dấu ĐÃ KHỎI, giữ kháng thể lại
#   - Vấn đề quay lại  -> TÁI NHIỄM, báo động đỏ kèm ngày từng khỏi
#
# Đây là thứ chỉ làm được khi công cụ có TRÍ NHỚ QUA THỜI GIAN, mà
# OKA thì có sẵn (mỗi bệnh nhân một hồ sơ riêng trên đĩa).

import os
import json
import hashlib
import re
from datetime import datetime

import oka_config as cfg

TEN_TEP = "khang_the.json"


def _duong_dan(benh_nhan):
    return os.path.join(cfg.thu_muc_ho_so(benh_nhan), TEN_TEP)


def _van_tay(van_ban):
    """Dấu vân tay của một vấn đề.

    Phải BỎ QUA các con số hay thay đổi (số nơi gọi, số dòng, tỷ lệ %),
    nếu không thì '6 nơi gọi' và '7 nơi gọi' bị coi là hai vấn đề khác
    nhau, và không bao giờ nhận ra được tái nhiễm.
    """
    loi = re.sub(r"\d+([.,]\d+)?%?", "#", van_ban)
    loi = re.sub(r"\s+", " ", loi).strip()
    return hashlib.sha1(loi.encode("utf-8")).hexdigest()[:16]


def _tai(benh_nhan):
    try:
        with open(_duong_dan(benh_nhan), "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
        if isinstance(du_lieu, dict) and "khang_the" in du_lieu:
            return du_lieu
    except (OSError, json.JSONDecodeError):
        pass
    return {"benh_nhan": benh_nhan, "khang_the": {}}


def _luu(benh_nhan, du_lieu):
    try:
        with open(_duong_dan(benh_nhan), "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


def ghi_nhan(benh_nhan, cac_nhan_dinh):
    """Đối chiếu đợt khám này với trí nhớ kháng thể.

    cac_nhan_dinh: list [(do_tin_cay, van_ban), ...] của Thượng Trí.
    Trả về list câu cảnh báo TÁI NHIỄM (rỗng nếu không có).
    """
    du_lieu = _tai(benh_nhan)
    kho = du_lieu["khang_the"]
    hom_nay = datetime.now().isoformat(timespec="seconds")

    dang_co = {}
    for do_tin_cay, van_ban in cac_nhan_dinh:
        # Câu "không phát hiện gì" không phải một vấn đề, đừng ghi nhớ
        if van_ban.lstrip().startswith("🟢"):
            continue
        dang_co[_van_tay(van_ban)] = (do_tin_cay, van_ban)

    tai_nhiem = []

    # 1. Vấn đề đang có: mới tinh, hay là kẻ cũ quay lại?
    for ma, (do_tin_cay, van_ban) in dang_co.items():
        cu = kho.get(ma)
        if cu is None:
            kho[ma] = {
                "tom_tat": van_ban[:150],
                "lan_dau": hom_nay,
                "lan_gan_nhat": hom_nay,
                "so_lan_tai_nhiem": 0,
                "dang_mac": True,
                "khoi_luc": None,
            }
        elif not cu.get("dang_mac"):
            # Đã từng khỏi mà nay quay lại - ĐÂY là thứ đáng báo động
            cu["so_lan_tai_nhiem"] = cu.get("so_lan_tai_nhiem", 0) + 1
            cu["dang_mac"] = True
            cu["lan_gan_nhat"] = hom_nay
            khoi_luc = (cu.get("khoi_luc") or "?")[:10]
            tai_nhiem.append(
                f"🦠 TÁI NHIỄM (lần thứ {cu['so_lan_tai_nhiem']}): vấn đề này "
                f"ĐÃ TỪNG được xử lý xong ngày {khoi_luc}, nay quay lại. "
                f"Rất có thể một thay đổi gần đây đã dựng lại nó — kiểm tra "
                f"kỹ trước khi vá lần nữa. → {van_ban[:110]}"
            )
        else:
            cu["lan_gan_nhat"] = hom_nay

    # 2. Vấn đề từng có mà nay không thấy nữa -> đánh dấu đã khỏi,
    #    NHƯNG GIỮ LẠI kháng thể. Đây chính là điểm cốt lõi: xóa đi thì
    #    lần sau nó quay lại ta lại tưởng là lỗi mới.
    for ma, muc in kho.items():
        if muc.get("dang_mac") and ma not in dang_co:
            muc["dang_mac"] = False
            muc["khoi_luc"] = hom_nay

    _luu(benh_nhan, du_lieu)
    return tai_nhiem


def thong_ke(benh_nhan):
    """Vài con số cho báo cáo."""
    kho = _tai(benh_nhan)["khang_the"]
    return {
        "tong_khang_the": len(kho),
        "dang_mac": sum(1 for m in kho.values() if m.get("dang_mac")),
        "da_khoi": sum(1 for m in kho.values() if not m.get("dang_mac")),
        "tung_tai_nhiem": sum(
            1 for m in kho.values() if m.get("so_lan_tai_nhiem", 0) > 0
        ),
    }


def ke_lai_thong_ke(benh_nhan):
    tk = thong_ke(benh_nhan)
    if tk["tong_khang_the"] == 0:
        return []
    dong = [
        f"🧬 TRÍ NHỚ MIỄN DỊCH: đã ghi {tk['tong_khang_the']} kháng thể "
        f"({tk['dang_mac']} vấn đề đang mắc, {tk['da_khoi']} đã khỏi)."
    ]
    if tk["tung_tai_nhiem"]:
        dong.append(
            f"🧬 Trong đó {tk['tung_tai_nhiem']} vấn đề từng khỏi rồi TÁI PHÁT "
            f"trở lại - đây là những chỗ dễ hỏng lại nhất của dự án."
        )
    return dong
