# main_kosmon.py
# ĐẠI CHU THIÊN - Đánh thức toàn bộ Tiểu Vũ Trụ OKA
#
# Cách dùng:
#     python main_kosmon.py                     -> khám bệnh nhân đã ghi danh lần trước
#     python main_kosmon.py "D:\du_an_cua_ban"  -> nhận bệnh nhân mới
#
# Không còn đường dẫn cứng của máy cũ. Chép sang máy nào cũng chạy.

import os
import sys
import time

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

# Triệu hồi các Tạng Phủ. Mỗi module tự nối dây thần kinh của mình
# ngay khi được import - không cần nối tay ở đây nữa.
import nham_mach_store          # Nhâm Mạch  - bể chứa Âm
import bang_quang_logger        # Bàng Quang - ghi bệnh án
import dom_validator            # Đởm        - chặn code hỏng
import tieu_truong_linter       # Tiểu Trường- gọt giũa
import ty_tang_parser           # Tỳ         - tiêu hóa cấu trúc
import than_tang_backup         # Thận       - cất Nguyên Khí
import tam_tang_core            # Tâm        - Chân Kinh
import dai_truong_cleaner       # Đại Trường - đào thải rác
import tam_tieu_network         # Tam Tiêu   - giao tiếp ngoại giới
import vong_chan_diagnostic     # Vọng Chẩn  - nhìn sắc diện
import thiet_chan_pulse         # Thiết Chẩn - bắt mạch
import thuong_tri_tong_hop      # Thượng Trí - tổng hợp nhận định (chạy sau Thiết Chẩn)

from phe_watchdog import khoi_dong_nhip_tho, CO_WATCHDOG
from vi_receiver import ViTang


def nhan_benh_nhan():
    """Xác định hôm nay khám ai"""
    if len(sys.argv) > 1:
        duong_dan = os.path.abspath(sys.argv[1])
        if not os.path.isdir(duong_dan):
            print(f"❌ Không tìm thấy thư mục '{duong_dan}'")
            sys.exit(1)
        return cfg.chon_benh_nhan(duong_dan)

    benh_nhan = cfg.benh_nhan_hien_tai()
    if os.path.normcase(benh_nhan) == os.path.normcase(cfg.NHA_THAY_THUOC):
        print("ℹ️  Chưa ghi danh bệnh nhân nào → Thầy Thuốc tự khám mình.")
        print(f"   Muốn khám dự án khác:  python main_kosmon.py \"đường_dẫn_dự_án\"")
    return benh_nhan


def main():
    print("\n✨ Đang đánh thức ĐẠI CHU THIÊN OKA...\n")

    benh_nhan = nhan_benh_nhan()
    print(f"🏥 Bệnh nhân: {benh_nhan}")
    if not CO_WATCHDOG:
        print("ℹ️  Thiếu thư viện 'watchdog' → Phế sẽ thở chậm (vẫn dùng được).")

    # Tỳ Tạng nhai trọn dự án một lượt để có ký ức nền
    print("\n⚙️  Tỳ Tạng đang tiêu hóa dự án lần đầu...")
    xuong_song_trung_uong.phat_khi("YEU_CAU_NHAI", benh_nhan)

    # Mở Phế - bắt đầu hô hấp
    nhip_tho = khoi_dong_nhip_tho(benh_nhan)

    # Mở Vị - nhận khẩu lệnh từ bạn
    ViTang()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        if nhip_tho:
            try:
                nhip_tho.stop()
            except Exception:
                pass
        print("\n🥀 Vũ trụ đã chìm vào giấc ngủ.")


if __name__ == "__main__":
    main()
