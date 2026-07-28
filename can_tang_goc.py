# can_tang_goc.py
# CAN (Lá Gan) - "Can tàng Huyết, chủ mưu lự" - một trong Ngũ Tạng có trong
# blueprint gốc của OKA (xem README) nhưng CHƯA TỪNG được viết cho tới nay.
#
# Cảm hứng: sách của Anthony William (Medical Medium) - lưu ý đây là quan
# điểm CÁ NHÂN tác giả tự nhận được "mách bảo", KHÔNG phải kiến thức y khoa
# đã kiểm chứng, dùng ở đây thuần túy làm ẩn dụ kiến trúc, giống cách Oahspe
# từng được dùng cho tool đào Bitcoin. Cốt lõi mượn: "gan quá tải là gốc của
# phần lớn bệnh mãn tính - chữa mãi triệu chứng mà không chạm gốc thì bệnh
# cứ tái đi tái lại."
#
# Áp vào code: một file bị SỬA CẤU TRÚC (Thận Tạng thật sự cất Nguyên Khí,
# không phải gõ nhầm dấu cách) liên tiếp nhiều lần trong thời gian ngắn không
# phải dấu hiệu "đang khỏe dần lên" - đó là dấu hiệu đang vá triệu chứng mà
# chưa ai chạm tới gốc. Can Tạng không đọc code, không phân tích cấu trúc
# (việc đó của Vọng Chẩn/Thiết Chẩn) - nó chỉ soi lại LỊCH SỬ mà Thận Tạng
# đã cất, tìm file nào "tái phát" nhiều nhất.

import os
from datetime import datetime, timedelta

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong


class CanTang:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_KHAM_GOC", self.kham_qua_tai)

    def _doc_gio_backup(self, ten_ban_sao):
        """Bản sao dạng '{ten_file}_{YYYYMMDD_HHMMSS}.bak'.

        ten_file có thể tự chứa dấu '_', nên tách 2 mảnh CUỐI làm mốc giờ
        thay vì tách theo dấu '_' đầu tiên.
        """
        if not ten_ban_sao.endswith(".bak"):
            return None, None
        goc = ten_ban_sao[: -len(".bak")]
        phan = goc.rsplit("_", 2)
        if len(phan) != 3:
            return None, None
        ten_file, ngay, gio = phan
        try:
            moc = datetime.strptime(f"{ngay}_{gio}", "%Y%m%d_%H%M%S")
        except ValueError:
            return None, None
        return ten_file, moc

    # Thận Tạng đặt tên bản sao chỉ theo BASENAME (không giữ đường dẫn thư
    # mục), nên nếu dự án có nhiều file cùng tên ở khác thư mục (rất thường
    # gặp với __init__.py), lịch sử của chúng sẽ bị TRỘN LẪN vào chung một
    # chỗ - Can Tạng sẽ đếm sai (tưởng 1 file sửa nhiều lần, thật ra là nhiều
    # file khác nhau). Sửa tận gốc Thận Tạng rủi ro cao (module cứu hộ quan
    # trọng nhất hệ thống), nên ở đây chỉ LOẠI TRỪ những tên biết chắc là mơ
    # hồ, thay vì đổi cách lưu trữ.
    TEN_MO_HO = {"__init__.py"}

    def _thong_ke(self, benh_nhan):
        """Tính thuần túy, không in - để Thượng Trí gọi lại mà không in
        report một lần nữa."""
        kho = cfg.kho_nguyen_khi(benh_nhan)
        if not os.path.isdir(kho):
            return None

        theo_file = {}
        for ten in os.listdir(kho):
            ten_file, moc = self._doc_gio_backup(ten)
            if ten_file is None or ten_file in self.TEN_MO_HO:
                continue
            theo_file.setdefault(ten_file, []).append(moc)

        nguong_gio = datetime.now() - timedelta(hours=cfg.KHUNG_GIO_QUA_TAI)
        qua_tai = []
        for ten_file, ds_gio in theo_file.items():
            gan_day = [g for g in ds_gio if g >= nguong_gio]
            if len(gan_day) >= cfg.NGUONG_TAI_PHAT:
                qua_tai.append((ten_file, len(gan_day), len(ds_gio)))

        qua_tai.sort(key=lambda x: -x[1])
        return {"benh_nhan": benh_nhan, "theo_file": theo_file, "qua_tai": qua_tai}

    def kham_qua_tai(self, benh_nhan=None):
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        so_lieu = self._thong_ke(benh_nhan)

        print("\n" + "🫘 " * 5)
        print(f"🫘 [CAN TẠNG]: SOI GỐC QUÁ TẢI - {os.path.basename(benh_nhan)}")
        print("🫘 " * 5)

        if so_lieu is None:
            print("\n⚠️ Chưa có lịch sử Nguyên Khí nào để soi. "
                  "Gõ 'nhai' vài lần khi có sửa đổi thật để tích lũy lịch sử trước.")
            print("-" * 60 + "\n")
            return None

        qua_tai = so_lieu["qua_tai"]
        if not qua_tai:
            print(f"\n🟢 Không có file nào đổi cấu trúc quá {cfg.NGUONG_TAI_PHAT} lần "
                  f"trong {cfg.KHUNG_GIO_QUA_TAI} giờ gần đây.")
        else:
            print(f"\n🔴 TÁI PHÁT (nghi vá triệu chứng, chưa chạm gốc):")
            for ten_file, gan, tong in qua_tai:
                print(f"   {ten_file:<30} ← {gan} lần trong {cfg.KHUNG_GIO_QUA_TAI}h "
                      f"gần đây (tổng {tong} lần từng cất)")
            print(f"\n💡 File bị sửa cấu trúc dồn dập không phải đang khỏe lên -")
            print(f"    trước khi sửa tiếp, hãy tự hỏi: lỗi thật nằm ở ĐÂY, hay")
            print(f"    đây chỉ là nơi triệu chứng lộ ra?")

        print("-" * 60 + "\n")
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG",
            f"CAN TẠNG: Đã soi {len(so_lieu['theo_file'])} file, "
            f"{len(qua_tai)} nghi tái phát."
        )
        return qua_tai


can_tang_trung_uong = CanTang()
