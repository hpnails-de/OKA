# than_tang_backup.py
# THẬN TẠNG - Thận tàng Tinh, gốc của tiên thiên (Backup & Rollback)
#
# Sửa 3 chỗ so với bản đầu:
#   1. Trước đây đăng ký sự kiện "CODE_AN_TOAN" mà chẳng ai phát ra bao giờ,
#      nên phải nối tay thủ công ở main/gui. Nay nghe đúng "CAU_TRUC_DA_DOI".
#   2. Kho Nguyên Khí tách riêng theo từng bệnh nhân.
#   3. Hàm phục hồi (rollback) trước đây chỉ có 'pass' - nay làm thật.

import os
import shutil
from datetime import datetime

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong


class ThanTang:
    def __init__(self):
        # Chỉ cất Nguyên Khí khi CẤU TRÚC thực sự đổi.
        # Gõ thêm một dấu cách không đáng để sinh một bản sao mới.
        xuong_song_trung_uong.dang_ky_nhan_khi("CAU_TRUC_DA_DOI", self.luu_nguyen_khi)
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_PHUC_HOI", self.phuc_hoi_nguyen_khi)

    def luu_nguyen_khi(self, tin_hieu):
        """Cất một bản sao khỏe mạnh của file vào kho của đúng bệnh nhân"""
        if isinstance(tin_hieu, dict):
            duong_dan_file = tin_hieu.get("file")
            benh_nhan = tin_hieu.get("benh_nhan")
        else:
            duong_dan_file, benh_nhan = tin_hieu, None

        if not duong_dan_file or not os.path.isfile(duong_dan_file):
            return

        benh_nhan = benh_nhan or cfg.tim_benh_nhan_cua(duong_dan_file)
        kho = cfg.kho_nguyen_khi(benh_nhan)

        ten_file = os.path.basename(duong_dan_file)
        thoi_gian = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            shutil.copy2(duong_dan_file, os.path.join(kho, f"{ten_file}_{thoi_gian}.bak"))
        except OSError as e:
            xuong_song_trung_uong.phat_khi("GHI_LOG", f"THẬN TẠNG: Không cất được {ten_file} → {e}")
            return

        self._tia_bot(kho, ten_file)
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"THẬN TẠNG: Đã cất Nguyên Khí cho {ten_file} lúc {thoi_gian}"
        )

    def _tia_bot(self, kho, ten_file):
        """Quên có chọn lọc: chỉ giữ N bản gần nhất, tránh kho phình vô hạn"""
        ban_sao = sorted(
            (f for f in os.listdir(kho) if f.startswith(ten_file + "_")),
            reverse=True
        )
        for cu in ban_sao[cfg.SO_BAN_NGUYEN_KHI_GIU:]:
            try:
                os.remove(os.path.join(kho, cu))
            except OSError:
                pass

    # ---------------- Phục hồi ----------------

    def liet_ke_ban_sao(self, ten_file, benh_nhan=None):
        """Các bản Nguyên Khí đang giữ cho một file"""
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        kho = cfg.kho_nguyen_khi(benh_nhan)
        if not os.path.isdir(kho):
            return []
        return sorted(
            (f for f in os.listdir(kho) if f.startswith(ten_file + "_")),
            reverse=True
        )

    def phuc_hoi_nguyen_khi(self, yeu_cau):
        """Tái sinh file từ bản sao khỏe mạnh.

        yeu_cau: tên file, hoặc dict {'ten_file':..., 'ban_sao':..., 'benh_nhan':...}
        Không chỉ định bản sao thì lấy bản mới nhất.
        """
        if isinstance(yeu_cau, dict):
            ten_file = yeu_cau.get("ten_file")
            ban_chon = yeu_cau.get("ban_sao")
            benh_nhan = yeu_cau.get("benh_nhan")
        else:
            ten_file, ban_chon, benh_nhan = yeu_cau, None, None

        if not ten_file:
            return False

        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        ds = self.liet_ke_ban_sao(ten_file, benh_nhan)
        if not ds:
            print(f"❌ [THẬN TẠNG]: Không còn Nguyên Khí nào của '{ten_file}'.")
            return False

        ban_sao = ban_chon if ban_chon in ds else ds[0]
        nguon = os.path.join(cfg.kho_nguyen_khi(benh_nhan), ban_sao)

        # Tìm lại chỗ file từng nằm trong dự án
        dich = None
        for root, dirs, files in os.walk(benh_nhan):
            dirs[:] = [d for d in dirs if d not in cfg.TA_KHI_DIRS]
            if ten_file in files:
                dich = os.path.join(root, ten_file)
                break
        if dich is None:
            dich = os.path.join(benh_nhan, ten_file)

        # Cất bản hiện tại trước khi đè - phòng khi phục hồi nhầm
        if os.path.isfile(dich):
            self.luu_nguyen_khi({"file": dich, "benh_nhan": benh_nhan})

        shutil.copy2(nguon, dich)
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"THẬN TẠNG: Đã tái sinh {ten_file} từ {ban_sao}"
        )
        print(f"🌱 [THẬN TẠNG]: Đã phục hồi '{ten_file}' ← {ban_sao}")
        return True


than_tang = ThanTang()
