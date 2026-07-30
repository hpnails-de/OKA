# ty_ngo_luu_chu.py
# TÝ NGỌ LƯU CHÚ (子午流注) - tìm LIÊN KẾT ẨN theo dòng thời gian
#
# Y lý: khí huyết chảy qua mười hai kinh theo giờ, mỗi canh giờ một tạng
# vượng. Hai tạng cùng vượng một khung giờ thì có quan hệ với nhau, dù
# trên cơ thể chúng không hề nối liền nhau.
#
# ------------------------------------------------------------------
# BÀI TOÁN THẬT MÀ MODULE NÀY GIẢI
# ------------------------------------------------------------------
# Mọi phân tích tĩnh (kể cả Thiết Chẩn, kể cả Graphify) chỉ thấy được
# quan hệ CÓ MỐI NỐI TRONG CODE: A import B, A gọi hàm của B.
#
# Nhưng vô số phụ thuộc THẬT lại KHÔNG có mối nối nào:
#   - File A đọc khóa "voice_id" trong JSON mà file B ghi ra
#   - Hàm ở A phải sửa mỗi khi schema ở B đổi
#   - Hai file cùng phải khớp một quy ước đặt tên
#
# Đây đúng là loại lỗi khiến "AI sửa chỗ này hỏng chỗ kia" - vì KHÔNG
# CÓ ĐƯỜNG NÀO trong code để lần ra.
#
# Cách bắt: Thận Tạng đã lưu sẵn dấu thời gian mọi lần file đổi cấu
# trúc. Nếu A và B LUÔN đổi cùng nhau mà giữa chúng không có import
# nào -> gần như chắc chắn có ràng buộc ngầm.
#
# GIỚI HẠN PHẢI BIẾT: đây là suy luận thống kê, không phải bằng chứng.
# Hai file cùng đổi có thể chỉ vì bạn tình cờ dọn dẹp cả hai một lượt.
# Vì vậy kết quả luôn mang nhãn SUY ĐOÁN, và cần số lần lặp lại đủ nhiều.

import os
from datetime import datetime, timedelta
from collections import defaultdict
from itertools import combinations

import oka_config as cfg

# Hai lần cất Nguyên Khí cách nhau dưới ngần này thì coi như CÙNG một
# phiên sửa. Đặt 30 phút: đủ rộng để gộp một lượt sửa có suy nghĩ, đủ
# hẹp để không gộp nhầm hai buổi làm việc khác nhau.
KHOANG_CUNG_PHIEN = timedelta(minutes=30)

# Số phiên tối thiểu mà hai file phải cùng xuất hiện. Dưới ngưỡng này
# thì rất có thể chỉ là trùng hợp.
NGUONG_CUNG_DOI = 3

# Tỷ lệ tối thiểu: trong các phiên có A, bao nhiêu phần trăm cũng có B.
NGUONG_TY_LE = 0.6

# ------------------------------------------------------------------
# LOẠI PHIÊN QUÉT HÀNG LOẠT - bẫy đã mắc phải thật
# ------------------------------------------------------------------
# Lần chạy đầu tiên module này báo 1176 "liên kết ẩn" trên một dự án 49
# file - vô lý. Nguyên nhân: cả 3 "phiên" đều là lệnh 'nhai' quét TOÀN
# BỘ dự án, mà quét toàn bộ thì Thận Tạng cất Nguyên Khí cho MỌI file
# cùng một lúc. Thế là cặp file nào cũng "cùng đổi 3/3 lần".
#
# Người sửa code thật chỉ đụng vài file một lượt. Phiên nào đụng quá
# nhiều file thì đó là máy quét, không phải người sửa - phải loại bỏ,
# nếu không toàn bộ phép phân tích thành vô nghĩa.
SO_FILE_TOI_DA_MOT_PHIEN = 15
TY_LE_TOI_DA_MOT_PHIEN = 0.30      # hoặc quá 30% dự án


def _doc_moc_thoi_gian(benh_nhan):
    """Đọc kho Nguyên Khí -> [(ten_file, thời điểm), ...]"""
    kho = cfg.kho_nguyen_khi(benh_nhan)
    if not os.path.isdir(kho):
        return []

    moc = []
    for ten in os.listdir(kho):
        if not ten.endswith(".bak"):
            continue
        goc = ten[: -len(".bak")]
        phan = goc.rsplit("_", 2)
        if len(phan) != 3:
            continue
        ten_file, ngay, gio = phan
        # Thận Tạng đặt tên theo BASENAME nên file trùng tên ở khác thư
        # mục sẽ lẫn vào nhau -> bỏ qua, giống cách Can Tạng đang làm.
        if ten_file in {"__init__.py", "index.js", "index.ts"}:
            continue
        try:
            moc.append((ten_file, datetime.strptime(f"{ngay}_{gio}", "%Y%m%d_%H%M%S")))
        except ValueError:
            continue
    return moc


def gom_phien(moc):
    """Gom các lần sửa gần nhau về thời gian thành từng PHIÊN.

    Trả về list các set tên file. Mỗi set = các file cùng đổi trong một
    phiên làm việc.
    """
    if not moc:
        return []

    moc = sorted(moc, key=lambda x: x[1])
    cac_phien = []
    phien_hien_tai = {moc[0][0]}
    moc_truoc = moc[0][1]

    for ten_file, thoi_diem in moc[1:]:
        if thoi_diem - moc_truoc <= KHOANG_CUNG_PHIEN:
            phien_hien_tai.add(ten_file)
        else:
            cac_phien.append(phien_hien_tai)
            phien_hien_tai = {ten_file}
        moc_truoc = thoi_diem

    cac_phien.append(phien_hien_tai)
    # Phiên chỉ có 1 file thì không nói lên quan hệ nào
    return [p for p in cac_phien if len(p) >= 2]


def loc_phien_nguoi_sua(cac_phien, tong_so_file):
    """Bỏ các phiên quá lớn - đó là máy quét toàn bộ, không phải người sửa."""
    nguong = SO_FILE_TOI_DA_MOT_PHIEN
    if tong_so_file:
        nguong = min(nguong, max(2, int(tong_so_file * TY_LE_TOI_DA_MOT_PHIEN)))
    return [p for p in cac_phien if len(p) <= nguong]


def _co_moi_noi_trong_code(a, b, canh, files):
    """A và B có import lẫn nhau không? (a, b là BASENAME)"""
    def cac_khoa(ten_ngan):
        return [k for k in files if os.path.basename(k.replace("\\", "/")) == ten_ngan]

    khoa_a, khoa_b = cac_khoa(a), cac_khoa(b)
    for ka in khoa_a:
        for kb in khoa_b:
            if kb in canh.get(ka, ()) or ka in canh.get(kb, ()):
                return True
    return False


def soi_lien_ket_an(benh_nhan, mach, canh_phu_thuoc):
    """Tìm cặp file luôn đổi cùng nhau mà code KHÔNG hề nối chúng.

    Trả về [(file_a, file_b, so_lan_cung, so_phien_co_a_hoac_b), ...]
    """
    files = mach["ky_uc"].get("files", {})
    cac_phien = loc_phien_nguoi_sua(
        gom_phien(_doc_moc_thoi_gian(benh_nhan)), len(files)
    )
    if len(cac_phien) < NGUONG_CUNG_DOI:
        return []          # chưa đủ lịch sử NGƯỜI SỬA để nói gì có nghĩa

    dem_cung = defaultdict(int)
    dem_rieng = defaultdict(int)
    for phien in cac_phien:
        for f in phien:
            dem_rieng[f] += 1
        for a, b in combinations(sorted(phien), 2):
            dem_cung[(a, b)] += 1

    ket_qua = []
    for (a, b), so_cung in dem_cung.items():
        if so_cung < NGUONG_CUNG_DOI:
            continue
        # Tỷ lệ Jaccard: cùng nhau / (tổng số phiên có ít nhất một trong hai)
        hop = dem_rieng[a] + dem_rieng[b] - so_cung
        if hop <= 0 or so_cung / hop < NGUONG_TY_LE:
            continue
        if _co_moi_noi_trong_code(a, b, canh_phu_thuoc, files):
            continue       # đã có import nối - không phải liên kết ẩn
        ket_qua.append((a, b, so_cung, hop))

    ket_qua.sort(key=lambda x: (-x[2], x[0]))
    return ket_qua


def ke_lai(ket_qua, gioi_han=5):
    """Diễn giải thành câu chữ."""
    dong = []
    for a, b, so_cung, hop in ket_qua[:gioi_han]:
        dong.append(
            f"🕰️ LIÊN KẾT ẨN: '{a}' và '{b}' đã {so_cung}/{hop} lần đổi cấu "
            f"trúc trong CÙNG một phiên làm việc, nhưng trong code KHÔNG hề "
            f"có import nào nối chúng. Nhiều khả năng chúng ràng buộc nhau "
            f"ngầm (chung một khóa JSON, chung quy ước đặt tên, chung schema) "
            f"- sửa một bên mà quên bên kia là hỏng."
        )
    if len(ket_qua) > gioi_han:
        dong.append(f"🕰️ (còn {len(ket_qua) - gioi_han} cặp liên kết ẩn nữa)")
    return dong
