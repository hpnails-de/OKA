# gia_khoi.py
# GIẢ KHỎI - ẩn dụ Đông Y: che giấu triệu chứng khiến TRÔNG như đã khỏi
# bệnh, trong khi bệnh vẫn còn nguyên. Áp vào code: thay vì sửa lỗi thật,
# làm YẾU ĐI bài test (xóa assertion, nới lỏng điều kiện) để nó "xanh"
# (pass) - lỗi vẫn còn nguyên, chỉ là không còn ai phát hiện. Khảo sát
# developer 2026 gọi thẳng đây là AI "gaming tests" - một nghiên cứu còn
# ghi nhận "AI đôi khi ăn gian bài test" thay vì sửa lỗi thật.
#
# Vệ Khí (ve_khi_bao_ve.py) soi CỬA NGÕ bên ngoài; Giả Khỏi soi NGƯỢC LẠI -
# liệu tuyến phòng thủ (bài test) có đang tự làm yếu mình không. Dữ liệu
# lấy từ chính kho Nguyên Khí mà Thận Tạng đã cất (than_tang_backup.py) -
# không chạy lại test, không cần cài pytest/jest, chỉ ĐẾM tín hiệu khẳng
# định (assert, expect...) qua các bản backup liên tiếp của cùng một file
# test.
#
# GIỚI HẠN THẬT: đếm số giảm không phân biệt được "dọn dẹp test hợp lệ" với
# "làm yếu test để né lỗi" - hai việc nhìn giống hệt nhau qua con số. Đây
# LUÔN LUÔN là SUY ĐOÁN, không có ngoại lệ.

import os
import re
from datetime import datetime

import oka_config as cfg

MAU_TEN_TEST = re.compile(
    r"^test_.+\.py$|.+_test\.py$|.+\.(test|spec)\.(js|jsx|ts|tsx)$",
    re.IGNORECASE,
)

MAU_KHANG_DINH = re.compile(
    r"\bassert\b|\bself\.assert\w+\s*\(|\bexpect\s*\(|\.toBe\w*\s*\(|\.should\b",
    re.IGNORECASE,
)


def _la_ten_file_test(ten_file):
    return bool(MAU_TEN_TEST.match(ten_file))


def _dem_khang_dinh(noi_dung):
    return len(MAU_KHANG_DINH.findall(noi_dung))


def _doc_gio_backup(ten_ban_sao):
    """Giống hệt logic của can_tang_goc._doc_gio_backup - tên bản sao dạng
    '{ten_file}_{YYYYMMDD_HHMMSS}.bak'."""
    if not ten_ban_sao.endswith(".bak"):
        return None, None
    goc = ten_ban_sao[: -len(".bak")]
    phan = goc.rsplit("_", 2)
    if len(phan) != 3:
        return None, None
    ten_file, ngay, gio = phan
    try:
        moc = datetime.strptime(f"{ngay}_{gio}", "%Y%m%d_%H%M%S")
    except ValueError:
        return None, None
    return ten_file, moc


def quet(benh_nhan=None):
    """Tính thuần túy. Trả về [(ten_file, moc_cu, moc_moi, kd_cu, kd_moi), ...]
    cho những lần số khẳng định GIẢM giữa 2 bản backup liên tiếp của một
    file test."""
    benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
    kho = cfg.kho_nguyen_khi(benh_nhan)
    if not os.path.isdir(kho):
        return []

    theo_file = {}
    for ten in os.listdir(kho):
        ten_file, moc = _doc_gio_backup(ten)
        if ten_file is None or not _la_ten_file_test(ten_file):
            continue
        theo_file.setdefault(ten_file, []).append((moc, ten))

    phat_hien = []
    for ten_file, ds in theo_file.items():
        ds.sort(key=lambda x: x[0])
        if len(ds) < 2:
            continue

        so_lieu = []
        for moc, ten_bak in ds:
            try:
                with open(os.path.join(kho, ten_bak), "r", encoding="utf-8", errors="replace") as f:
                    noi_dung = f.read()
            except OSError:
                continue
            so_lieu.append((moc, _dem_khang_dinh(noi_dung)))

        for (moc_cu, kd_cu), (moc_moi, kd_moi) in zip(so_lieu, so_lieu[1:]):
            if kd_moi < kd_cu:
                phat_hien.append((ten_file, moc_cu, moc_moi, kd_cu, kd_moi))

    phat_hien.sort(key=lambda x: x[2], reverse=True)
    return phat_hien


def ke_lai(phat_hien, gioi_han=10):
    if not phat_hien:
        return []
    dong = [
        f"🎭 GIẢ KHỎI: {len(phat_hien)} lần số khẳng định (assert/expect) trong "
        f"file test GIẢM giữa 2 lần lưu liên tiếp - CÓ THỂ là dọn dẹp test hợp "
        f"lệ, CŨNG CÓ THỂ là làm yếu test để nó 'xanh' thay vì sửa lỗi thật. "
        f"Không phân biệt được 2 trường hợp này chỉ bằng đếm số - tự xem lại diff:"
    ]
    for ten_file, moc_cu, moc_moi, kd_cu, kd_moi in phat_hien[:gioi_han]:
        dong.append(
            f"   • {ten_file}: {kd_cu} → {kd_moi} khẳng định "
            f"({moc_cu.strftime('%Y-%m-%d %H:%M')} → {moc_moi.strftime('%Y-%m-%d %H:%M')})"
        )
    if len(phat_hien) > gioi_han:
        dong.append(f"   … và {len(phat_hien) - gioi_han} lần khác.")
    return ["\n".join(dong)]
