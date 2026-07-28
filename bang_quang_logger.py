# bang_quang_logger.py
# BÀNG QUANG - Bài tiết cặn bã và ghi chép bệnh án (System Logger)
#
# Sửa: bản đầu ghi vào os.getcwd(), nên khởi động từ thư mục khác là log
# rơi vãi khắp nơi. Nay luôn ghi vào đúng nhà Thầy Thuốc.

import os

from datetime import datetime

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

GIOI_HAN_BYTE = 1_000_000   # ~1MB thì cuộn sổ, tránh phình vô hạn


class BangQuang:
    def __init__(self):
        self.file_log = cfg.NHAT_KY_THAY_THUOC
        self.in_ra_man_hinh = True
        xuong_song_trung_uong.dang_ky_nhan_khi("GHI_LOG", self.bai_tiet_log)

    def bai_tiet_log(self, thong_diep):
        if thong_diep is None:
            return

        thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dong_log = f"[{thoi_gian}] {thong_diep}"

        try:
            self._cuon_so()
            with open(self.file_log, "a", encoding="utf-8") as f:
                f.write(dong_log + "\n")
        except OSError:
            pass

        if self.in_ra_man_hinh:
            print(f"💧 {dong_log}")

    def _cuon_so(self):
        """Quên có chọn lọc: sổ đầy thì cuộn lại một bản, không giữ mãi"""
        try:
            if os.path.getsize(self.file_log) < GIOI_HAN_BYTE:
                return
        except OSError:
            return

        cu = self.file_log + ".1"
        try:
            if os.path.exists(cu):
                os.remove(cu)
            os.rename(self.file_log, cu)
        except OSError:
            pass


bang_quang = BangQuang()
