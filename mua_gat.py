# mua_gat.py
# MÙA GẶT (Harvest) - chấm PHẨM CẤP dự án và theo dõi xu hướng theo thời gian
#
# ------------------------------------------------------------------
# CĂN CỨ TRONG SÁCH (đọc thẳng từ file .docx, không trích từ trí nhớ)
# ------------------------------------------------------------------
# Oahspe dùng thang PHẨM CẤP (grade) từ thấp tới 99 để đo mức tiến hóa,
# và ghi lại phẩm cấp ấy ở mỗi "mùa gặt" (harvest) định kỳ:
#
#   Sách Jehovih: "God shall cause a record to be kept... And in the times
#   of my harvest a copy of these records shall be taken up... for their
#   deliberations as to the progress and management."
#
#   Sách Asshong ghi chuỗi mùa gặt liên tiếp của một chu kỳ:
#     mùa 1: grade 92   mùa 2: grade 89   mùa 3: grade 83
#     mùa 4: grade 74   mùa 5: grade 62   mùa 6: grade 51
#     "And this was the last harvest; for none were of sufficient [grade]"
#
# Đó chính xác là đường suy thoái của một dự án không được chăm sóc: mỗi
# đợt một chút, không đợt nào thấy rõ, tới lúc nhìn lại thì đã quá muộn.
#
# ------------------------------------------------------------------
# BÀI TOÁN THẬT
# ------------------------------------------------------------------
# Mọi thứ OKA làm tới giờ chỉ trả lời "dự án ĐANG thế nào". Không có gì
# trả lời câu quan trọng hơn: "dự án đang KHỎE LÊN hay YẾU ĐI?"
#
# Một dự án 20 lỗi mà tuần trước 40 lỗi thì đang hồi phục. Cũng 20 lỗi
# mà tuần trước 5 lỗi thì đang lao dốc. Cùng một con số, hai tình
# trạng trái ngược - và không công cụ nào hiện nay nói được điều đó.

import os
import json
from datetime import datetime

import oka_config as cfg

TEN_TEP = "mua_gat.json"
CAP_TOI_DA = 99          # đúng thang Oahspe: cao nhất là grade 99


def _duong_dan(benh_nhan):
    return os.path.join(cfg.thu_muc_ho_so(benh_nhan), TEN_TEP)


def cham_pham_cap(mach, nguyen_khi, di_vat, so_vong):
    """Chấm phẩm cấp 0-99 cho dự án.

    NÓI THẲNG VỀ ĐỘ TIN CẬY: từng thành phần đều ĐẾM ĐƯỢC từ code
    (chắc chắn), nhưng TRỌNG SỐ giữa chúng là lựa chọn của người thiết
    kế, không phải chân lý. Vì vậy con số tuyệt đối ít ý nghĩa; cái
    đáng tin là XU HƯỚNG của nó qua các mùa gặt - vì mọi mùa đều chấm
    bằng đúng một thước đo.

    Trả về (pham_cap, chi_tiet_tru_diem)
    """
    files = mach["ky_uc"].get("files", {})
    tong_file = len(files) or 1

    # 1. Phình to: file quá dài thì người lẫn AI đều khó review
    so_phinh = len(mach.get("phinh", []))
    tru_phinh = min(20, (so_phinh / tong_file) * 60)

    # 2. Khí chết: hàm không ai gọi
    tong_ten = len(mach.get("noi_sinh", {})) or 1
    so_chet = len(mach.get("khi_chet", []))
    tru_chet = min(20, (so_chet / tong_ten) * 55)

    # 3. Vòng luẩn quẩn: nặng nhất, vì không gỡ được từng phần
    tru_vong = min(20, so_vong * 7)

    # 4. Dị vật: code không rõ thuộc về đâu
    tong_kham = len(nguyen_khi) + len(di_vat) or 1
    tru_di_vat = min(15, (len(di_vat) / tong_kham) * 30)

    # 5. Huyệt hiểm quá tập trung: một hàm bị gọi từ quá nhiều nơi
    huyet = mach.get("huyet_hiem", [])
    cao_nhat = huyet[0][1] if huyet else 0
    tru_huyet = min(10, cao_nhat / 8)

    tru = tru_phinh + tru_chet + tru_vong + tru_di_vat + tru_huyet
    pham_cap = max(1, round(CAP_TOI_DA - tru))

    chi_tiet = {
        "phinh_to": round(tru_phinh, 1),
        "khi_chet": round(tru_chet, 1),
        "vong_luan_quan": round(tru_vong, 1),
        "di_vat": round(tru_di_vat, 1),
        "huyet_hiem": round(tru_huyet, 1),
    }
    return pham_cap, chi_tiet


def _tai(benh_nhan):
    try:
        with open(_duong_dan(benh_nhan), "r", encoding="utf-8") as f:
            du_lieu = json.load(f)
        if isinstance(du_lieu, dict) and "cac_mua" in du_lieu:
            return du_lieu
    except (OSError, json.JSONDecodeError):
        pass
    return {"benh_nhan": benh_nhan, "cac_mua": []}


def gat(benh_nhan, pham_cap, chi_tiet, so_file):
    """Ghi lại một mùa gặt. Trả về (mua_nay, mua_truoc_hoac_None)."""
    du_lieu = _tai(benh_nhan)
    cac_mua = du_lieu["cac_mua"]
    mua_truoc = cac_mua[-1] if cac_mua else None

    mua_nay = {
        "luc": datetime.now().isoformat(timespec="seconds"),
        "pham_cap": pham_cap,
        "so_file": so_file,
        "chi_tiet": chi_tiet,
    }
    cac_mua.append(mua_nay)

    # Giữ 50 mùa gần nhất - đủ để thấy xu hướng dài, không phình vô hạn
    du_lieu["cac_mua"] = cac_mua[-50:]
    try:
        with open(_duong_dan(benh_nhan), "w", encoding="utf-8") as f:
            json.dump(du_lieu, f, indent=2, ensure_ascii=False)
    except OSError:
        pass

    return mua_nay, mua_truoc


def _xep_hang(pham_cap):
    if pham_cap >= 85:
        return "rất khỏe"
    if pham_cap >= 70:
        return "khỏe"
    if pham_cap >= 55:
        return "trung bình"
    if pham_cap >= 40:
        return "suy yếu"
    return "nguy kịch"


def ke_lai(mua_nay, mua_truoc, lich_su=None):
    """Diễn giải phẩm cấp và xu hướng."""
    cap = mua_nay["pham_cap"]
    dong = [
        f"🌾 MÙA GẶT: phẩm cấp dự án {cap}/99 ({_xep_hang(cap)}). "
        f"Trừ điểm do: " + ", ".join(
            f"{k.replace('_', ' ')} -{v}"
            for k, v in sorted(mua_nay["chi_tiet"].items(), key=lambda x: -x[1])
            if v > 0
        )
    ]

    if mua_truoc:
        chenh = cap - mua_truoc["pham_cap"]
        truoc_luc = mua_truoc["luc"][:10]
        if chenh > 0:
            dong.append(
                f"📈 KHỎE LÊN: phẩm cấp tăng {chenh} điểm so với mùa gặt "
                f"ngày {truoc_luc} ({mua_truoc['pham_cap']} → {cap})."
            )
        elif chenh < 0:
            dong.append(
                f"📉 YẾU ĐI: phẩm cấp GIẢM {abs(chenh)} điểm so với mùa gặt "
                f"ngày {truoc_luc} ({mua_truoc['pham_cap']} → {cap}). "
                f"Sách Asshong chép một chu kỳ tụt dần 92→89→83→74→62→51 rồi "
                f"kết thúc - mỗi đợt một chút, không đợt nào thấy rõ."
            )
        else:
            dong.append(f"➡️ GIỮ NGUYÊN phẩm cấp {cap} so với mùa gặt ngày {truoc_luc}.")

    if lich_su and len(lich_su) >= 3:
        chuoi = " → ".join(str(m["pham_cap"]) for m in lich_su[-6:])
        dong.append(f"🌾 Chuỗi phẩm cấp các mùa gần đây: {chuoi}")

    return dong


def lich_su(benh_nhan):
    return _tai(benh_nhan)["cac_mua"]
