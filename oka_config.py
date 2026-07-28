# oka_config.py
# SỔ BỆNH ÁN - Nơi ghi danh Bệnh Nhân và phân định Nhà Thầy Thuốc với Nhà Bệnh Nhân
#
# Lý do tồn tại: Trước đây các Tạng Phủ đều dùng os.getcwd() - tức "thư mục đang đứng".
# Điều đó khiến Thầy Thuốc tự uống thuốc của Bệnh Nhân: bệnh án của mọi dự án
# bị đổ chung vào một file, khám người thứ hai là xóa mất người thứ nhất.

import os
import re
import sys
import json
import hashlib

# ==============================================================
#  KHAI KHIẾU - Mở đường cho chữ nghĩa đi ra màn hình
#
#  Máy cũ chạy console UTF-8 nên không ai thấy vấn đề. Máy mới dùng
#  bảng mã cp1252, gặp emoji là chết ngay từ dòng print đầu tiên.
#  Phải mở khiếu trước khi bất kỳ Tạng Phủ nào cất tiếng.
# ==============================================================
for _luong in (sys.stdout, sys.stderr):
    try:
        _luong.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, OSError):
        pass   # môi trường không cho đổi thì thôi, errors='replace' lo phần còn lại

# ==============================================================
#  NHÀ THẦY THUỐC - Cố định theo vị trí file này, không đổi
#  dù bạn khởi động OKA từ bất kỳ thư mục nào
# ==============================================================
NHA_THAY_THUOC = os.path.dirname(os.path.abspath(__file__))

# Mỗi bệnh nhân một phòng hồ sơ riêng
PHONG_HO_SO = os.path.join(NHA_THAY_THUOC, "HO_SO_BENH_AN")

# Sổ ghi danh sách bệnh nhân đang theo dõi
SO_GHI_DANH = os.path.join(NHA_THAY_THUOC, "OKA_BENH_NHAN.json")

# Nhật ký chung của Thầy Thuốc (Bàng Quang ghi vào đây)
NHAT_KY_THAY_THUOC = os.path.join(NHA_THAY_THUOC, "OKA_system.log")

# ==============================================================
#  TÀ KHÍ - Những thư mục tuyệt đối không khám
#  (dùng chung cho Vọng Chẩn, Thiết Chẩn, Tỳ Tạng)
# ==============================================================
TA_KHI_DIRS = {
    'venv', 'env', '.venv', 'node_modules', '.git', '__pycache__',
    'site-packages', 'dist', 'build', '.idea', '.vscode',
    'KHO_NGUYEN_KHI', 'HO_SO_BENH_AN',
    '.next', '.nuxt', '.turbo', 'coverage', '.parcel-cache',
}

# Các đuôi file Tỳ Tạng biết "nhai" (rút chữ ký hàm/class/import). Python
# dùng ast thật (chính xác); JS/TS/JSX/TSX dùng regex nhẹ (thô hơn nhưng
# không cần cài thư viện nặng như tree-sitter - giữ đúng triết lý "không
# cần cài gì thêm" của cả dự án).
CAC_DUOI_HO_TRO = {'.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs'}

# ==============================================================
#  Y LỆNH - Các thói quen điều trị (bật/tắt hành vi của Tool)
# ==============================================================

# Tiểu Trường tự ghi đè file source của bệnh nhân để gọt khoảng trắng.
# MẶC ĐỊNH TẮT: Thầy Thuốc không tự tay sửa người bệnh khi chưa được phép.
TU_DONG_GOT_GIUA = False

# Ngưỡng cảnh báo file phình to (Vọng Chẩn)
NGUONG_PHINH_TO = 350

# Số bản Nguyên Khí (backup) giữ lại tối đa cho mỗi file
SO_BAN_NGUYEN_KHI_GIU = 10

# --- Can Tạng: ngưỡng "tái phát" (Anthony William - gan quá tải là gốc của
# phần lớn bệnh mãn tính; chữa triệu chứng mãi không chạm gốc thì tái đi tái
# lại). Một file bị cất Nguyên Khí (tức đổi cấu trúc thật) từ NGUONG_TAI_PHAT
# lần trở lên trong KHUNG_GIO_QUA_TAI giờ gần đây -> nghi đang vá triệu chứng.
NGUONG_TAI_PHAT = 3
KHUNG_GIO_QUA_TAI = 24


def _slug(duong_dan):
    """Biến đường dẫn dự án thành tên thư mục hồ sơ an toàn.

    Vân tay phải BẤT BIẾN giữa các lần chạy. Dùng hash() của Python là hỏng:
    nó bị ngẫu nhiên hóa lại mỗi tiến trình, nên mỗi lần khởi động lại sinh ra
    một hồ sơ mới và ký ức cũ vĩnh viễn thất lạc.
    """
    ten = os.path.basename(os.path.normpath(duong_dan)) or "vo_danh"
    ten = re.sub(r'[^0-9A-Za-z_.-]', '_', ten)
    goc = os.path.normcase(os.path.abspath(duong_dan)).encode('utf-8')
    van_tay = hashlib.sha1(goc).hexdigest()[:8]
    return f"{ten}_{van_tay}"


def thu_muc_ho_so(duong_dan_du_an):
    """Phòng hồ sơ riêng của một bệnh nhân"""
    ho_so = os.path.join(PHONG_HO_SO, _slug(duong_dan_du_an))
    os.makedirs(ho_so, exist_ok=True)
    return ho_so


def duong_dan_ky_uc(duong_dan_du_an):
    """File ký ức (cấu trúc code) của riêng bệnh nhân này"""
    return os.path.join(thu_muc_ho_so(duong_dan_du_an), "ky_uc.json")


def kho_nguyen_khi(duong_dan_du_an):
    """Kho backup của riêng bệnh nhân này"""
    kho = os.path.join(thu_muc_ho_so(duong_dan_du_an), "KHO_NGUYEN_KHI")
    os.makedirs(kho, exist_ok=True)
    return kho


def la_ta_khi(duong_dan):
    """Đường dẫn này có nằm trong vùng Tà Khí không?"""
    phan = os.path.normpath(duong_dan).split(os.sep)
    return any(p in TA_KHI_DIRS for p in phan)


# ==============================================================
#  GHI DANH BỆNH NHÂN
# ==============================================================

def _doc_so():
    if os.path.exists(SO_GHI_DANH):
        try:
            with open(SO_GHI_DANH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"benh_nhan": [], "hien_tai": None}


def _ghi_so(so):
    with open(SO_GHI_DANH, 'w', encoding='utf-8') as f:
        json.dump(so, f, indent=4, ensure_ascii=False)


def ghi_danh(duong_dan_du_an, chon_luon=True):
    """Nhận một dự án vào danh sách bệnh nhân đang theo dõi"""
    duong_dan = os.path.abspath(duong_dan_du_an)
    if not os.path.isdir(duong_dan):
        return None

    so = _doc_so()
    if duong_dan not in so["benh_nhan"]:
        so["benh_nhan"].append(duong_dan)
    if chon_luon or not so.get("hien_tai"):
        so["hien_tai"] = duong_dan
    _ghi_so(so)
    thu_muc_ho_so(duong_dan)
    return duong_dan


def danh_sach_benh_nhan():
    return _doc_so().get("benh_nhan", [])


def benh_nhan_hien_tai():
    """Bệnh nhân đang được theo dõi. Nếu chưa có ai, Thầy Thuốc tự khám mình."""
    so = _doc_so()
    hien_tai = so.get("hien_tai")
    if hien_tai and os.path.isdir(hien_tai):
        return hien_tai

    # Chưa có bệnh nhân nào còn sống -> tự khám chính mình
    return ghi_danh(NHA_THAY_THUOC)


def chon_benh_nhan(duong_dan_du_an):
    """Chuyển sang khám một bệnh nhân khác"""
    return ghi_danh(duong_dan_du_an, chon_luon=True)


def tim_benh_nhan_cua(duong_dan_file):
    """Một file vừa đổi thuộc về bệnh nhân nào?"""
    file_abs = os.path.abspath(duong_dan_file)
    ung_vien = None
    for bn in danh_sach_benh_nhan():
        if file_abs.startswith(bn + os.sep):
            # Chọn đường dẫn khớp sâu nhất (dự án lồng nhau)
            if ung_vien is None or len(bn) > len(ung_vien):
                ung_vien = bn
    return ung_vien or benh_nhan_hien_tai()
