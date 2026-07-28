# nham_mach_store.py
# NHÂM MẠCH - Bể chứa Âm (Global State / Redux Store)
#
# Nguyên tắc: Nhâm Mạch giữ CHỈ MỤC, không giữ bản sao.
# Hippocampus trong não người cũng vậy - nó không chứa ký ức, nó chỉ đánh dấu
# ký ức nằm ở đâu rồi trỏ về đó. Sao chép thành hai bản là tự chuốc lệch pha.

import threading


class NhamMach:
    def __init__(self):
        self._trang_thai = {
            "benh_nhan_hien_tai": None,
            "chi_muc_ky_uc": {},      # con trỏ tới ký ức của Tỳ Tạng, không phải bản sao
            "nhip_tho": None,
        }
        self._khoa = threading.Lock()

    def cap_nhat(self, chia_khoa, gia_tri):
        """Bơm thêm dưỡng chất vào dòng máu"""
        with self._khoa:
            self._trang_thai[chia_khoa] = gia_tri

    def lay_khi_huyet(self, chia_khoa, mac_dinh=None):
        """Các tạng phủ rút máu từ đây để dùng"""
        with self._khoa:
            return self._trang_thai.get(chia_khoa, mac_dinh)

    def lay_toan_bo(self):
        with self._khoa:
            return dict(self._trang_thai)


# Tạo ra Bể chứa huyết mạch duy nhất
nham_mach_trung_uong = NhamMach()
