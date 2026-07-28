# dom_validator.py
# ĐỞM (Mật) - Chủ sự quyết đoán: duyệt hay từ chối đoạn code vừa lưu
#
# Sửa: bản đầu dùng py_compile, mà py_compile ĐẺ ra thư mục __pycache__
# ngay trong nhà bệnh nhân - vừa khám vừa xả rác. Nay biên dịch trong bộ nhớ,
# không để lại dấu vết nào trên ổ cứng người ta.

import os

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong


class DomPhu:
    def __init__(self):
        # Đởm đứng gác ngay sau khi Phế hít file vào
        xuong_song_trung_uong.dang_ky_nhan_khi("FILE_DA_LUU", self.phan_xet_code)

    def phan_xet_code(self, duong_dan_file):
        if not duong_dan_file or not os.path.isfile(duong_dan_file):
            return

        ten_file = os.path.basename(duong_dan_file)
        try:
            with open(duong_dan_file, 'r', encoding='utf-8') as f:
                noi_dung = f.read()
            compile(noi_dung, duong_dan_file, 'exec')

        except SyntaxError as e:
            xuong_song_trung_uong.phat_khi(
                "GHI_LOG",
                f"🚨 ĐỞM TỪ CHỐI: {ten_file} dòng {e.lineno} - {e.msg}. Chặn luồng!"
            )
            xuong_song_trung_uong.phat_khi("CODE_HONG", {
                "file": duong_dan_file, "dong": e.lineno, "loi": e.msg,
            })
            return

        except (OSError, ValueError) as e:
            xuong_song_trung_uong.phat_khi("GHI_LOG", f"ĐỞM: Không đọc nổi {ten_file} → {e}")
            return

        # Code sạch cú pháp thì cho đi tiếp
        xuong_song_trung_uong.phat_khi("CODE_SACH_CUM_1", duong_dan_file)


dom_phu_trung_uong = DomPhu()
