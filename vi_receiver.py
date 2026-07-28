# vi_receiver.py
# VỊ (Dạ dày) - Nơi tiếp nhận khẩu lệnh từ người dùng
#
# Vị không tự phân tích. Nó chỉ nhận thức ăn (lệnh) rồi đẩy xuống
# cho Tỳ, Tâm, Thiết Chẩn... qua Đốc Mạch.

import os
import threading

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

BANG_LENH = """
🥣 [VỊ]: KHẨU LỆNH
   nhai            - Tỳ Tạng tiêu hóa toàn bộ dự án (làm trước tiên)
   kham            - Vọng Chẩn: nhìn sắc diện dự án
   mach            - Thiết Chẩn: bắt mạch, tìm huyệt hiểm & khí chết
   mach <tên hàm>  - Sửa hàm này thì hỏng những đâu?
   kinh [từ khóa]  - Xuất Chân Kinh cho AI (có từ khóa thì chỉ lấy phần liên quan)
   benhnhan        - Xem / đổi bệnh nhân đang khám
   hoisinh <file>  - Thận Tạng phục hồi file từ bản Nguyên Khí
   don             - Đại Trường đào thải rác
   lenh            - Xem lại bảng lệnh này
   thoat           - Đóng Tiểu Vũ Trụ
"""


class ViTang:
    def __init__(self, tu_dong_chay=True):
        self.luong_lang_nghe = threading.Thread(target=self.cho_doi_thuc_an, daemon=True)
        if tu_dong_chay:
            self.luong_lang_nghe.start()

    def cho_doi_thuc_an(self):
        print(f"\n🌿 [VỊ]: Đang bám rễ tại bệnh nhân: {cfg.benh_nhan_hien_tai()}")
        print(BANG_LENH)

        while True:
            try:
                raw = input("\n👉 Nhập lệnh: ").strip()
            except (EOFError, KeyboardInterrupt):
                break

            if not raw:
                continue

            phan = raw.split(maxsplit=1)
            lenh = phan[0].lower()
            tham_so = phan[1].strip() if len(phan) > 1 else ""

            try:
                self.tieu_thu(lenh, tham_so)
            except Exception as e:
                print(f"⚠️ [VỊ]: Nuốt không trôi lệnh này → {e}")

    def tieu_thu(self, lenh, tham_so):
        if lenh == 'nhai':
            xuong_song_trung_uong.phat_khi("YEU_CAU_NHAI", cfg.benh_nhan_hien_tai())

        elif lenh == 'kham':
            dia_chi = tham_so or cfg.benh_nhan_hien_tai()
            if os.path.isdir(dia_chi):
                xuong_song_trung_uong.phat_khi("YEU_CAU_KHAM_BENH", dia_chi)
            else:
                print(f"❌ [VỊ]: Không tìm thấy '{dia_chi}'")

        elif lenh == 'mach':
            if tham_so:
                xuong_song_trung_uong.phat_khi("YEU_CAU_DO_ANH_HUONG", tham_so)
            else:
                xuong_song_trung_uong.phat_khi("YEU_CAU_BAT_MACH", cfg.benh_nhan_hien_tai())

        elif lenh == 'kinh':
            xuong_song_trung_uong.phat_khi("YEU_CAU_CHAN_KINH", {"loc": tham_so or None})

        elif lenh == 'benhnhan':
            self._doi_benh_nhan(tham_so)

        elif lenh == 'hoisinh':
            if not tham_so:
                print("❓ Cú pháp: hoisinh <tên file>")
            else:
                xuong_song_trung_uong.phat_khi("YEU_CAU_PHUC_HOI", tham_so)

        elif lenh == 'don':
            xuong_song_trung_uong.phat_khi("YEU_CAU_DON_RAC", cfg.benh_nhan_hien_tai())

        elif lenh == 'lenh':
            print(BANG_LENH)

        elif lenh in ('thoat', 'exit', 'quit'):
            print("🥀 Đang đóng Tiểu Vũ Trụ...")
            os._exit(0)

        else:
            print(f"❓ [VỊ]: Không rõ lệnh '{lenh}'. Gõ 'lenh' để xem bảng lệnh.")

    def _doi_benh_nhan(self, duong_dan):
        if not duong_dan:
            print(f"\n🏥 Đang khám: {cfg.benh_nhan_hien_tai()}")
            ds = cfg.danh_sach_benh_nhan()
            if ds:
                print("📋 Danh sách bệnh nhân đã ghi danh:")
                for bn in ds:
                    con_song = "  " if os.path.isdir(bn) else " ❌(mất tích)"
                    print(f"   •{con_song} {bn}")
            print("\n   Đổi bằng: benhnhan <đường dẫn dự án>")
            return

        if not os.path.isdir(duong_dan):
            print(f"❌ [VỊ]: Không tìm thấy thư mục '{duong_dan}'")
            return

        cfg.chon_benh_nhan(duong_dan)
        print(f"✅ [VỊ]: Đã chuyển sang khám: {duong_dan}")
        print("   → Gõ 'nhai' để Tỳ Tạng tiêu hóa bệnh nhân mới.")
