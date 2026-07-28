# dai_truong_cleaner.py
# ĐẠI TRƯỜNG - Đào thải cặn bã (Garbage Collector)
#
# Sửa: bản đầu dọn os.getcwd() - tức nhà của chính Thầy Thuốc, hoặc tệ hơn là
# thư mục bạn tình cờ đứng lúc khởi động. Rác thì nằm ở nhà bệnh nhân.

import os
import shutil

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

RAC_THU_MUC = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
RAC_DUOI_FILE = (".pyc", ".pyo", ".tmp", ".temp", ".bak~")


class DaiTruong:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_DON_RAC", self.dao_thai)

    def dao_thai(self, duong_dan_du_an=None):
        benh_nhan = duong_dan_du_an or cfg.benh_nhan_hien_tai()
        if not os.path.isdir(benh_nhan):
            return

        so_thu_muc = so_file = 0

        for root, dirs, files in os.walk(benh_nhan, topdown=True):
            # Không đụng vào kho Nguyên Khí - đó là thuốc, không phải rác
            dirs[:] = [d for d in dirs if d not in {"KHO_NGUYEN_KHI", "HO_SO_BENH_AN", ".git"}]

            for d in list(dirs):
                if d in RAC_THU_MUC:
                    try:
                        shutil.rmtree(os.path.join(root, d))
                        so_thu_muc += 1
                        dirs.remove(d)
                    except OSError:
                        pass

            for f in files:
                if f.endswith(RAC_DUOI_FILE):
                    try:
                        os.remove(os.path.join(root, f))
                        so_file += 1
                    except OSError:
                        pass

        xuong_song_trung_uong.phat_khi(
            "GHI_LOG",
            f"💩 ĐẠI TRƯỜNG: Đào thải {so_thu_muc} búi rác và {so_file} file cặn "
            f"khỏi {os.path.basename(benh_nhan)}."
        )


dai_truong_trung_uong = DaiTruong()
