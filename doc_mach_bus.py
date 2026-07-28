# doc_mach_bus.py
# ĐỐC MẠCH - Tuyến truyền tin của Tiểu Vũ Trụ OKA
#
# Nâng cấp theo Ngũ Hành: ngoài quan hệ SINH (A xong thì kích hoạt B),
# nay có thêm quan hệ KHẮC (A quá tải thì hãm nhịp B) để hệ thống tự cân bằng,
# thay vì chạy một chiều đến kiệt sức.

import time
import threading

import oka_config  # noqa: F401  - nạp trước để khai khiếu UTF-8 cho màn hình


class DocMach:
    def __init__(self):
        # Bể chứa các đường kinh lạc (Sinh: sự kiện -> danh sách hàm nhận)
        self._kinh_lac = {}
        # Bảng Khắc: tạng nào đang bị hãm, hãm đến bao giờ
        self._dang_bi_khac = {}
        self._khoa = threading.Lock()
        self.im_lang = False  # True: không in ra terminal khi đăng ký

    # ---------- SINH: nuôi dưỡng, kích hoạt tiếp ----------

    def dang_ky_nhan_khi(self, ten_su_kien, chuc_nang_nhan):
        """(Subscribe) Một Tạng/Phủ đăng ký lắng nghe một luồng Khí"""
        with self._khoa:
            nguoi_nhan = self._kinh_lac.setdefault(ten_su_kien, [])
            # Tránh nối trùng một dây thần kinh hai lần
            if chuc_nang_nhan in nguoi_nhan:
                return
            nguoi_nhan.append(chuc_nang_nhan)
        if not self.im_lang:
            print(f"🔗 [ĐỐC MẠCH]: Đã kết nối thần kinh cho sự kiện '{ten_su_kien}'")

    def phat_khi(self, ten_su_kien, du_lieu=None):
        """(Publish) Phát tín hiệu đi toàn thân.

        Mỗi người nhận được bọc riêng: một Tạng ngã bệnh thì các Tạng còn lại
        vẫn nhận được khí, không đứt cả chuỗi như trước.
        """
        if self._bi_khac(ten_su_kien):
            return

        with self._khoa:
            nguoi_nhan = list(self._kinh_lac.get(ten_su_kien, []))

        for chuc_nang in nguoi_nhan:
            try:
                chuc_nang(du_lieu)
            except Exception as e:
                ten = getattr(chuc_nang, '__qualname__', repr(chuc_nang))
                print(f"⚠️ [ĐỐC MẠCH]: Kinh lạc '{ten_su_kien}' tắc tại {ten} → {e}")

    # ---------- KHẮC: kiềm chế, giữ cho không thái quá ----------

    def khac(self, ten_su_kien, trong_giay):
        """Hãm một luồng khí lại trong ít lâu (VD: Tâm khắc Phế khi thở gấp)"""
        with self._khoa:
            self._dang_bi_khac[ten_su_kien] = time.time() + trong_giay

    def _bi_khac(self, ten_su_kien):
        with self._khoa:
            han = self._dang_bi_khac.get(ten_su_kien)
            if han is None:
                return False
            if time.time() >= han:
                del self._dang_bi_khac[ten_su_kien]
                return False
            return True


# Tạo ra một 'Xương sống' duy nhất cho toàn bộ cơ thể dùng chung
xuong_song_trung_uong = DocMach()
