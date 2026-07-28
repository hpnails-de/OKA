# tieu_truong_linter.py
# TIỂU TRƯỜNG - Phân thanh giáng trọc: tách cái trong khỏi cái đục
#
# CẢNH BÁO ĐÃ ĐƯỢC XỬ LÝ: bản đầu tự ghi đè file source của bệnh nhân
# mỗi lần lưu. Thầy Thuốc mà tự tay cầm dao sửa người bệnh khi chưa được phép
# là chuyện nguy hiểm - nhất là khi bệnh nhân đang mở file đó trong editor.
# Nay mặc định TẮT (xem cfg.TU_DONG_GOT_GIUA), và chỉ ghi khi thực sự có gì để gọt.

import os

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong


class TieuTruong:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("CODE_SACH_CUM_1", self.got_giua_code)

    def got_giua_code(self, duong_dan_file):
        if not duong_dan_file or not os.path.isfile(duong_dan_file):
            return

        if cfg.TU_DONG_GOT_GIUA:
            self._got(duong_dan_file)

        # Dù có gọt hay không, code vẫn đi tiếp sang Tỳ và Thận
        xuong_song_trung_uong.phat_khi("CODE_HOAN_HAO", duong_dan_file)

    def _got(self, duong_dan_file):
        try:
            with open(duong_dan_file, 'r', encoding='utf-8') as f:
                cac_dong = f.readlines()
        except OSError:
            return

        cac_dong_sach = [d.rstrip() + '\n' for d in cac_dong]

        # Không có gì đổi thì tuyệt đối không chạm vào file.
        # Ghi lại y nguyên chỉ tổ đánh thức Phế một vòng vô ích.
        if cac_dong_sach == cac_dong:
            return

        try:
            with open(duong_dan_file, 'w', encoding='utf-8') as f:
                f.writelines(cac_dong_sach)
        except OSError as e:
            xuong_song_trung_uong.phat_khi("GHI_LOG", f"TIỂU TRƯỜNG: Không gọt được → {e}")
            return

        xuong_song_trung_uong.phat_khi(
            "GHI_LOG",
            f"TIỂU TRƯỜNG: Đã gọt khoảng trắng thừa trong {os.path.basename(duong_dan_file)}"
        )


tieu_truong_trung_uong = TieuTruong()
