# cum_chuc_nang.py
# GOM CỤM CHỨC NĂNG - chia dự án thành các "tạng phủ" tự nhiên của nó.
#
# Vì sao cần: Chân Kinh trước đây liệt kê file theo thứ tự bảng chữ cái -
# AI (và người) đọc xong biết có những gì nhưng không biết cái gì thuộc về
# cái gì. Một dự án 110 file mà liệt kê phẳng thì vẫn khó nắm bố cục.
#
# Cách làm: KHÔNG cần thư viện ngoài (networkx/Leiden). Dùng thuật toán
# "lan truyền nhãn" (label propagation) - mỗi file ban đầu mang nhãn riêng,
# rồi lặp nhiều vòng, mỗi vòng file đổi sang nhãn phổ biến nhất trong đám
# hàng xóm (những file nó gọi / gọi nó). Vài vòng là các file gắn bó chặt
# tự dồn về chung một nhãn. Đơn giản, không phụ thuộc, đủ tốt.

import os
from collections import Counter, defaultdict


def dung_do_thi_file(mach):
    """Từ mạch đồ của Thiết Chẩn -> đồ thị mức FILE (ai gọi file nào).

    mach: kết quả của thiet_chan_pulse.dung_mach_do()
    Trả về: {file: {file_hang_xom: trọng_số}}
    """
    noi_sinh = mach["noi_sinh"]       # tên hàm -> [file định nghĩa]
    ky_uc = mach["ky_uc"]

    hang_xom = defaultdict(Counter)
    for khoa, tinh_hoa in ky_uc.get("files", {}).items():
        for ten_goi in tinh_hoa.get("goi", []):
            for file_dinh_nghia in noi_sinh.get(ten_goi, []):
                if file_dinh_nghia == khoa:
                    continue          # tự gọi mình thì không tính là quan hệ
                hang_xom[khoa][file_dinh_nghia] += 1
                hang_xom[file_dinh_nghia][khoa] += 1
    return hang_xom


def lan_truyen_nhan(hang_xom, cac_file, so_vong=12):
    """Label propagation. Trả về {file: nhãn_cụm}.

    Duyệt theo thứ tự CỐ ĐỊNH (đã sắp xếp) thay vì ngẫu nhiên, để chạy
    hai lần trên cùng dữ liệu cho cùng kết quả - báo cáo mà mỗi lần chạy
    một khác thì không ai tin được.
    """
    nhan = {f: i for i, f in enumerate(sorted(cac_file))}

    for _ in range(so_vong):
        co_doi = False
        for f in sorted(cac_file):
            ke = hang_xom.get(f)
            if not ke:
                continue
            phieu = Counter()
            for hx, trong_so in ke.items():
                if hx in nhan:
                    phieu[nhan[hx]] += trong_so
            if not phieu:
                continue
            # Hòa phiếu thì chọn nhãn nhỏ nhất - để kết quả tất định
            cao_nhat = max(phieu.values())
            nhan_moi = min(n for n, v in phieu.items() if v == cao_nhat)
            if nhan_moi != nhan[f]:
                nhan[f] = nhan_moi
                co_doi = True
        if not co_doi:
            break                      # đã ổn định, khỏi lặp thêm
    return nhan


def _dat_ten_cum(cac_file, hang_xom=None):
    """Đặt tên cụm: thư mục chung + file trung tâm.

    Chỉ lấy thư mục chung là chưa đủ - một dự án hay có hai ba cụm cùng nằm
    trong 'backend', in ra trùng tên thì người đọc không phân biệt nổi. Nên
    kèm theo file "trung tâm" (nhiều quan hệ nhất) làm dấu nhận biết.
    """
    thu_muc = [os.path.dirname(f) for f in cac_file]
    chung = ""
    if thu_muc and all(thu_muc):
        try:
            chung = os.path.commonpath(thu_muc)
        except ValueError:
            chung = ""

    trung_tam = ""
    if hang_xom:
        trung_tam = max(
            cac_file,
            key=lambda f: sum(hang_xom.get(f, {}).values()),
        )
        trung_tam = os.path.basename(trung_tam)

    if chung and trung_tam:
        return f"{chung}  ·  quanh {trung_tam}"
    if chung:
        return chung
    if trung_tam:
        return f"quanh {trung_tam}"
    return f"gốc dự án ({len(cac_file)} file)"


def gom_cum(mach, toi_thieu=2):
    """Gom file thành các cụm chức năng.

    Trả về danh sách [(ten_cum, [file,...]), ...] sắp theo cụm lớn trước.
    File không dính với ai (cụm 1 phần tử) gom hết vào cụm 'rời rạc'.
    """
    ky_uc = mach["ky_uc"]
    cac_file = list(ky_uc.get("files", {}).keys())
    if not cac_file:
        return []

    hang_xom = dung_do_thi_file(mach)
    nhan = lan_truyen_nhan(hang_xom, cac_file)

    theo_nhan = defaultdict(list)
    for f, n in nhan.items():
        theo_nhan[n].append(f)

    cum_lon, roi_rac = [], []
    for ds in theo_nhan.values():
        if len(ds) >= toi_thieu:
            cum_lon.append(sorted(ds))
        else:
            roi_rac.extend(sorted(ds))

    ket_qua = [(_dat_ten_cum(ds, hang_xom), ds) for ds in cum_lon]
    ket_qua.sort(key=lambda x: -len(x[1]))
    if roi_rac:
        ket_qua.append(("rời rạc (không gọi/không bị gọi)", sorted(roi_rac)))
    return ket_qua
