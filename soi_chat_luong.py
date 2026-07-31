# soi_chat_luong.py
# Gộp 3 hiện tượng cùng nhóm "chất lượng cấu trúc" (không phải bug, không
# phải bảo mật) vào một lệnh/một bước GUI duy nhất, đỡ dài dòng cho người
# dùng phổ thông:
#   Trùng Ảnh (trung_anh.py) - logic bị viết lại ở nhiều nơi
#   Vỏ Rỗng   (vo_rong.py)   - lớp bọc (wrapper) không cần thiết dồn 1 file
#   Giả Khỏi  (gia_khoi.py)  - bài test bị làm yếu thay vì sửa lỗi thật
#
# Thượng Trí gọi thẳng quet()/ke_lai() của từng module (không qua đây) để
# gắn nhãn CHẮC CHẮN/SUY ĐOÁN đúng ngữ cảnh tổng hợp - module này chỉ phục
# vụ lệnh CLI 'chatluong' và bước GUI đứng riêng, in report thô.

import os

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong
import trung_anh
import vo_rong
import gia_khoi


class SoiChatLuong:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_SOI_CHAT_LUONG", self.soi_va_bao_cao)

    def soi_va_bao_cao(self, benh_nhan=None):
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()

        print("\n" + "🪞 " * 5)
        print(f"🪞 [CHẤT LƯỢNG CẤU TRÚC]: {os.path.basename(benh_nhan)}")
        print("🪞 " * 5)

        co_gi = False
        for van in trung_anh.ke_lai(trung_anh.quet(benh_nhan)):
            print("\n" + van)
            co_gi = True
        for van in vo_rong.ke_lai(vo_rong.quet(benh_nhan)):
            print("\n" + van)
            co_gi = True
        for van in gia_khoi.ke_lai(gia_khoi.quet(benh_nhan)):
            print("\n" + van)
            co_gi = True

        if not co_gi:
            print("\n🟢 Không thấy trùng lặp, vỏ rỗng, hay test bị làm yếu.")

        print("\n" + "-" * 60 + "\n")
        xuong_song_trung_uong.phat_khi("GHI_LOG", "CHẤT LƯỢNG CẤU TRÚC: đã soi xong.")


soi_chat_luong_trung_uong = SoiChatLuong()
