# kiem_chung_thuc_te.py - Chạy thử các tuyên bố trong OKA_GIOI_THIEU_CONG_DUNG.md
import os, io, sys, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DU_AN = os.path.dirname(os.path.abspath(__file__))
print(f"Kiểm chứng trên dự án: {DU_AN}\n")

def bao(ten, fn):
    print(f"\n=== {ten} ===")
    try:
        fn()
    except Exception as e:
        print(f"  ❌ LỖI: {e}")
        traceback.print_exc(limit=2)

# 1. Tỳ Tạng - tiêu hóa cấu trúc
def k1():
    import ty_tang_parser as p
    kq = p.ty_tang_trung_uong.tieu_hoa_toan_bo(DU_AN)
    print("  Kết quả:", str(kq)[:600])
bao("1. Tỳ Tạng: tiêu hóa toàn bộ dự án", k1)

# 2. Vọng Chẩn
def k2():
    import vong_chan_diagnostic as v
    kq = v.VongChan().bat_dau_kham(DU_AN)
    print("  Kết quả:", str(kq)[:600])
bao("2. Vọng Chẩn: khám dự án", k2)

# 3. Vệ Khí
def k3():
    import ve_khi_bao_ve as vk
    ds = vk.quet(DU_AN)
    print(f"  Tìm thấy {len(ds) if hasattr(ds,'__len__') else '?'} dấu hiệu:")
    print("  " + str(ds)[:800])
bao("3. Vệ Khí: soi bảo mật", k3)

# 4. Cân Bằng Âm Dương (lời gọi hàm không có định nghĩa)
def k4():
    import am_duong_can_bang as cb
    ds = cb.quet(DU_AN)
    print(f"  Tìm thấy {len(ds) if hasattr(ds,'__len__') else '?'} lời gọi nghi vấn:")
    print("  " + str(ds)[:800])
bao("4. Âm Dương Cân Bằng: soi lời gọi hàm ma", k4)

# 5. Nén ngữ cảnh - đo bằng do_cong_luc (quy trình chuẩn của tool)
def k5():
    import oka_config as cfg
    import tam_tang_core as tc
    import ty_tang_parser as tp
    cfg.chon_benh_nhan(DU_AN)                       # ghi danh OKA làm bệnh nhân
    ky_uc = tp.ty_tang_trung_uong.tieu_hoa_toan_bo(DU_AN)
    print(f"  Tỳ Tạng đã nhai: {len(ky_uc['files'])} bộ xương trong ký ức")
    chan_kinh = tc.tam_tang_trung_uong.xuat_chan_kinh_cho_ai(DU_AN)
    so_token = tc.uoc_luong_token(chan_kinh)
    print(f"  Chân Kinh: {len(chan_kinh):,} ký tự = {so_token:,} token")
    kq = tc.tam_tang_trung_uong.do_cong_luc(DU_AN, chan_kinh)
    print(f"  do_cong_luc trả về: {kq}")
bao("5. Nén ngữ cảnh - đo bằng do_cong_luc sau khi nhai", k5)

# 6. Xoắn Ốc Ký Ức
def k6():
    import xoan_oc_ky_uc as xo
    van_ban, tk = xo.dung_tu_du_an(DU_AN)
    if not van_ban:
        print("  (Không có lịch sử hội thoại lưu cho dự án này - báo trống như tài liệu nói, không phải lỗi)")
    else:
        print(f"  {tk['so_su_kien']:,} lượt, {tk['ky_tu_goc']:,} → {tk['ky_tu_ky_uc']:,} ký tự "
              f"(giảm {(1-tk['ky_tu_ky_uc']/max(1,tk['ky_tu_goc']))*100:.1f}%)")
bao("6. Xoắn Ốc Ký Ức: nén lịch sử hội thoại", k6)

# 7. Phản Vũ - vòng phụ thuộc (nằm trong vong_chan_diagnostic?)
def k7():
    import tam_tieu_network as tn
    print("  Hàm có:", [x for x in dir(tn) if not x.startswith('_')])
bao("7. Tam Tiêu network - xem API vòng phụ thuộc", k7)

print("\n=== HẾT KIỂM CHỨNG ===")
