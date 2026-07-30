# phan_vu_vong.py
# PHẢN VŨ (反侮) - dò vòng phụ thuộc luẩn quẩn
#
# Y lý Ngũ Hành có ba loại quan hệ:
#   TƯƠNG SINH - Mộc sinh Hỏa: cái này nuôi cái kia. Lành.
#   TƯƠNG KHẮC - Thủy khắc Hỏa: cái này kiềm chế cái kia. Cũng LÀNH,
#                vì có kiềm chế thì hệ mới không thái quá.
#   PHẢN VŨ    - kẻ đang bị khắc quay lại lấn kẻ khắc mình. BỆNH.
#                Trật tự đảo lộn, thành vòng luẩn quẩn không lối ra.
#
# Áp vào code: A gọi B là bình thường (tương sinh). Nhưng A→B→C→A là
# PHẢN VŨ - không tìm được đâu là gốc, đâu là ngọn. Hậu quả thật:
#   - Lỗi import vòng khó hiểu (Python: partially initialized module)
#   - Không test riêng lẻ được module nào trong vòng
#   - AI sửa một mắt xích là gãy cả dây chuyền
#
# Thiết Chẩn hiện chỉ đếm "ai gọi ai bao nhiêu lần" (vô hướng), không
# nhìn ra CHIỀU và CHU TRÌNH. Module này dựng đồ thị CÓ HƯỚNG rồi dùng
# thuật toán Tarjan tìm "thành phần liên thông mạnh" - mỗi thành phần
# có từ 2 đỉnh trở lên chính là một vòng luẩn quẩn.

import os
from collections import defaultdict


def _chuan_hoa(khoa):
    """'engine\\rpc.py' -> 'engine/rpc' (bỏ đuôi, thống nhất dấu gạch)."""
    k = khoa.replace("\\", "/")
    for duoi in (".py", ".jsx", ".tsx", ".ts", ".js", ".mjs", ".cjs"):
        if k.endswith(duoi):
            return k[: -len(duoi)]
    return k


def dung_do_thi_co_huong(mach):
    """A → B nghĩa là: file A THỰC SỰ import file B.

    Vì sao KHÔNG dùng "A gọi hàm định nghĩa trong B": tên hàm bị trùng ở
    nhiều file là chuyện thường (riêng '__init__' có mặt ở 15 file trong
    OKA), nên cứ file nào tạo object là bị nối cạnh tới cả 15 file đó ->
    sinh ra vòng luẩn quẩn HOÀN TOÀN GIẢ. Đã kiểm chứng: bản đầu báo
    phe_watchdog.py phụ thuộc vi_receiver.py, trong khi phe_watchdog
    không hề nhắc tới vi_receiver một lần nào.

    Câu lệnh import là bằng chứng KHÔNG THỂ CHỐI CÃI về phụ thuộc, nên
    dùng nó làm nguồn sự thật.
    """
    files = mach["ky_uc"].get("files", {})

    # Bảng tra: dạng chuẩn hóa -> khóa file thật
    tra_cuu = {}
    dem_ten_ngan = defaultdict(int)
    for khoa in files:
        chuan = _chuan_hoa(khoa)
        tra_cuu[chuan] = khoa
        dem_ten_ngan[chuan.rsplit("/", 1)[-1]] += 1

    # Chỉ cho tra bằng tên ngắn khi tên đó DUY NHẤT trong dự án. Có hai file
    # cùng tên ở hai thư mục mà vẫn tra thì lại nối cạnh sai - đúng cái bẫy
    # vừa mắc ở bản trước.
    for khoa in files:
        chuan = _chuan_hoa(khoa)
        ngan = chuan.rsplit("/", 1)[-1]
        if dem_ten_ngan[ngan] == 1:
            tra_cuu.setdefault(ngan, khoa)

    canh = defaultdict(set)
    for khoa, tinh_hoa in files.items():
        thu_muc = os.path.dirname(khoa.replace("\\", "/"))
        for mo_dun in tinh_hoa.get("import", []):
            dich = _giai_ma_import(mo_dun, thu_muc, tra_cuu)
            if dich and dich != khoa:
                canh[khoa].add(dich)
    return canh


def _giai_ma_import(mo_dun, thu_muc_hien_tai, tra_cuu):
    """Từ tên module trong câu import -> khóa file trong ký ức (hoặc None
    nếu đó là thư viện ngoài, không thuộc dự án)."""
    if not mo_dun:
        return None

    # --- Kiểu JS: './foo', '../bar/baz' (luôn có dấu / sau dấu chấm) ---
    if mo_dun.startswith("./") or mo_dun.startswith("../"):
        duong = os.path.normpath(
            os.path.join(thu_muc_hien_tai, mo_dun)
        ).replace("\\", "/")
        return tra_cuu.get(duong) or tra_cuu.get(duong + "/index")

    # --- Kiểu Python tương đối: '.foo', '..pkg.foo' ---
    # Một dấu chấm = cùng gói; mỗi dấu chấm thêm là lùi lên một cấp.
    if mo_dun.startswith("."):
        so_cham = len(mo_dun) - len(mo_dun.lstrip("."))
        phan_con = mo_dun[so_cham:].replace(".", "/")
        goc = thu_muc_hien_tai
        for _ in range(so_cham - 1):
            goc = os.path.dirname(goc)
        duong = f"{goc}/{phan_con}" if goc else phan_con
        duong = os.path.normpath(duong).replace("\\", "/")
        return tra_cuu.get(duong) or tra_cuu.get(duong + "/__init__")

    # --- Kiểu Python tuyệt đối: 'engine.rpc', 'oka_config' ---
    duong = mo_dun.replace(".", "/")
    return tra_cuu.get(duong) or tra_cuu.get(duong + "/__init__")


def tim_vong(canh, cac_dinh):
    """Tarjan - tìm thành phần liên thông mạnh (SCC).

    Viết theo lối LẶP chứ không đệ quy: dự án lớn có thể sâu hàng nghìn
    tầng, đệ quy sẽ vỡ ngăn xếp Python (mặc định chỉ ~1000 tầng).

    Trả về: danh sách các vòng, mỗi vòng là list file (đã sắp xếp).
    """
    chi_so = {}         # đỉnh -> thứ tự khám phá
    thap_nhat = {}      # đỉnh -> chỉ số nhỏ nhất chạm tới được
    tren_ngan_xep = set()
    ngan_xep = []
    dem = [0]
    cac_vong = []

    for goc in sorted(cac_dinh):
        if goc in chi_so:
            continue

        # Mỗi khung: (đỉnh, iterator các đỉnh kề chưa duyệt)
        khung = [(goc, iter(sorted(canh.get(goc, ()))))]
        chi_so[goc] = thap_nhat[goc] = dem[0]
        dem[0] += 1
        ngan_xep.append(goc)
        tren_ngan_xep.add(goc)

        while khung:
            dinh, lang_gieng = khung[-1]
            da_di_tiep = False

            for ke in lang_gieng:
                if ke not in chi_so:
                    chi_so[ke] = thap_nhat[ke] = dem[0]
                    dem[0] += 1
                    ngan_xep.append(ke)
                    tren_ngan_xep.add(ke)
                    khung.append((ke, iter(sorted(canh.get(ke, ())))))
                    da_di_tiep = True
                    break
                if ke in tren_ngan_xep:
                    thap_nhat[dinh] = min(thap_nhat[dinh], chi_so[ke])

            if da_di_tiep:
                continue

            khung.pop()
            if khung:
                cha = khung[-1][0]
                thap_nhat[cha] = min(thap_nhat[cha], thap_nhat[dinh])

            # Đỉnh này là gốc của một SCC
            if thap_nhat[dinh] == chi_so[dinh]:
                thanh_phan = []
                while True:
                    d = ngan_xep.pop()
                    tren_ngan_xep.discard(d)
                    thanh_phan.append(d)
                    if d == dinh:
                        break
                if len(thanh_phan) > 1:
                    cac_vong.append(sorted(thanh_phan))

    cac_vong.sort(key=lambda v: -len(v))
    return cac_vong


def _duong_di_trong_vong(vong, canh):
    """Dựng một đường đi minh họa A→B→C→A cho dễ hiểu."""
    trong_vong = set(vong)
    bat_dau = vong[0]
    duong = [bat_dau]
    hien_tai = bat_dau
    da_qua = {bat_dau}

    while True:
        ke_tiep = None
        for ke in sorted(canh.get(hien_tai, ())):
            if ke in trong_vong and ke not in da_qua:
                ke_tiep = ke
                break
        if ke_tiep is None:
            break
        duong.append(ke_tiep)
        da_qua.add(ke_tiep)
        hien_tai = ke_tiep

    duong.append(bat_dau)   # khép vòng
    return duong


def soi_phan_vu(mach):
    """Trả về danh sách [(vong, duong_di_minh_hoa), ...]"""
    canh = dung_do_thi_co_huong(mach)
    cac_dinh = set(mach["ky_uc"].get("files", {}).keys())
    cac_vong = tim_vong(canh, cac_dinh)
    return [(v, _duong_di_trong_vong(v, canh)) for v in cac_vong]


def ke_lai(ket_qua, gioi_han=5):
    """Diễn giải thành câu chữ cho người đọc."""
    if not ket_qua:
        return []
    dong = []
    for vong, duong in ket_qua[:gioi_han]:
        mui_ten = " → ".join(os.path.basename(f) for f in duong)
        dong.append(
            f"🌀 PHẢN VŨ: {len(vong)} file kẹt trong vòng phụ thuộc luẩn quẩn: "
            f"{mui_ten}. Không có file nào là gốc - sửa một mắt xích là động "
            f"cả vòng, và Python có thể báo lỗi import vòng khó hiểu."
        )
    if len(ket_qua) > gioi_han:
        dong.append(f"🌀 (còn {len(ket_qua) - gioi_han} vòng luẩn quẩn nữa)")
    return dong
