# tam_tieu_network.py
# TAM TIÊU - Đường ống dẫn khí vô hình, giao tiếp ngoại giới (API / Network Layer)
#
# Sửa: bản đầu gọi thẳng "pip", nhưng máy mới có thể không có pip trong PATH.
# Nay gọi qua chính trình Python đang chạy - chắc chắn đúng môi trường.

import sys
import subprocess

from doc_mach_bus import xuong_song_trung_uong

# Những thần dược OKA cần để phát huy trọn công lực
THAN_DUOC = {
    "watchdog": "Phế thở sâu (bắt file đổi tức thì thay vì quét chậm)",
    "customtkinter": "Nhãn Tạng (giao diện đồ họa)",
}


class TamTieu:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_CAI_THU_VIEN", self.uong_nuoc_nguyen_khi)

    def kiem_ke(self):
        """Xem còn thiếu thần dược nào"""
        thieu = {}
        for ten, cong_dung in THAN_DUOC.items():
            try:
                __import__(ten)
            except ImportError:
                thieu[ten] = cong_dung
        return thieu

    def uong_nuoc_nguyen_khi(self, ten_thu_vien):
        if not ten_thu_vien:
            return False

        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"TAM TIÊU: Đang đi thỉnh kinh (cài {ten_thu_vien})..."
        )
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", ten_thu_vien])
            xuong_song_trung_uong.phat_khi("GHI_LOG", f"✅ TAM TIÊU: Đã nạp {ten_thu_vien}!")
            return True
        except (subprocess.CalledProcessError, OSError) as e:
            xuong_song_trung_uong.phat_khi(
                "GHI_LOG", f"❌ TAM TIÊU: Khí tức hỗn loạn, không cài được {ten_thu_vien} → {e}"
            )
            return False


tam_tieu_trung_uong = TamTieu()
