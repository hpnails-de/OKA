# thiet_chan_pulse.py
# THIẾT CHẨN (切診) - Phép bắt mạch, phép thứ tư trong Tứ Chẩn
#
# Vọng Chẩn chỉ nhìn được sắc diện bên ngoài: file dài bao nhiêu dòng, tên gì.
# Muốn biết "sửa chỗ này có hỏng chỗ kia không" thì phải BẮT MẠCH -
# phải biết khí huyết chạy đường nào, hàm nào nuôi hàm nào.
#
# Điểm hay: Thiết Chẩn KHÔNG đọc lại file. Nó bắt mạch ngay trên ký ức
# mà Tỳ Tạng đã tiêu hóa sẵn - đúng tinh thần "nhớ nhiều mà tốn ít".

import os

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong
from ty_tang_parser import ty_tang_trung_uong


class ThietChan:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_BAT_MACH", self.bat_mach)
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_DO_ANH_HUONG", self.do_anh_huong)

    # ---------------- Dựng đồ thị khí huyết ----------------

    def dung_mach_do(self, benh_nhan=None):
        """Từ ký ức của Tỳ Tạng, dựng bản đồ: ai định nghĩa gì, ai gọi ai"""
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        ky_uc = ty_tang_trung_uong.tai_ky_uc(benh_nhan)

        noi_sinh = {}    # tên hàm/class -> [file định nghĩa nó]
        nguoi_goi = {}   # tên hàm -> [file gọi nó]

        for khoa, tinh_hoa in ky_uc.get("files", {}).items():
            for ten_ham in tinh_hoa.get("ham", {}):
                noi_sinh.setdefault(ten_ham, []).append(khoa)
            for ten_cls, than in tinh_hoa.get("classes", {}).items():
                noi_sinh.setdefault(ten_cls, []).append(khoa)
                for ten_m in than.get("methods", {}):
                    noi_sinh.setdefault(ten_m, []).append(khoa)

        nguoi_nhac = {}  # tên -> [file có nhắc tới, dù chưa gọi thẳng]

        for khoa, tinh_hoa in ky_uc.get("files", {}).items():
            for ten_goi in tinh_hoa.get("goi", []):
                if ten_goi in noi_sinh:
                    nguoi_goi.setdefault(ten_goi, []).append(khoa)
            # Callback đưa đi gửi (VD: dang_ky_nhan_khi(..., self.ghi_log))
            # cũng là đang được dùng, tuy chưa gọi ngay
            for ten in tinh_hoa.get("tham_chieu", []):
                if ten in noi_sinh:
                    nguoi_nhac.setdefault(ten, []).append(khoa)

        return {"benh_nhan": benh_nhan, "noi_sinh": noi_sinh,
                "nguoi_goi": nguoi_goi, "nguoi_nhac": nguoi_nhac, "ky_uc": ky_uc}

    # ---------------- Trả lời câu hỏi đắt giá nhất ----------------

    def do_anh_huong(self, yeu_cau):
        """Sửa hàm này thì đụng tới những đâu?

        yeu_cau: tên hàm (chuỗi), hoặc dict {'ten': ..., 'benh_nhan': ...}
        """
        if isinstance(yeu_cau, dict):
            ten = yeu_cau.get("ten")
            benh_nhan = yeu_cau.get("benh_nhan")
        else:
            ten, benh_nhan = yeu_cau, None

        if not ten:
            return None

        mach = self.dung_mach_do(benh_nhan)
        sinh_tai = mach["noi_sinh"].get(ten, [])
        bi_goi_tai = mach["nguoi_goi"].get(ten, [])
        bi_nhac_tai = [f for f in mach["nguoi_nhac"].get(ten, []) if f not in bi_goi_tai]

        print("\n" + "=" * 60)
        print(f"🫀 [THIẾT CHẨN]: BẮT MẠCH CHO '{ten}'")
        print("=" * 60)

        if not sinh_tai:
            print(f"❓ Không tìm thấy '{ten}' trong ký ức dự án.")
            print("   → Nếu AI vừa gọi tên này, rất có thể nó đang ẢO GIÁC.")
        else:
            print(f"📍 Được định nghĩa tại: {', '.join(sinh_tai)}")
            if bi_goi_tai:
                print(f"\n⚠️  CẢNH BÁO: có {len(set(bi_goi_tai))} nơi GỌI THẲNG hàm này.")
                print("   Sửa nó là động vào từng chỗ dưới đây:")
                for f in sorted(set(bi_goi_tai)):
                    print(f"      • {f}")
            if bi_nhac_tai:
                print(f"\n🔗 Ngoài ra {len(set(bi_nhac_tai))} nơi NHẮC TÊN (callback, truyền đi):")
                for f in sorted(set(bi_nhac_tai)):
                    print(f"      • {f}")
            if not bi_goi_tai and not bi_nhac_tai:
                print("\n🟢 Không nơi nào dùng tới. Sửa hay xóa đều an toàn.")
                print("   (Hoặc đây là code chết - Đại Trường nên để mắt.)")

        print("=" * 60 + "\n")
        return {
            "ten": ten,
            "sinh_tai": sinh_tai,
            "bi_goi_tai": sorted(set(bi_goi_tai)),
            "bi_nhac_tai": sorted(set(bi_nhac_tai)),
        }

    # ---------------- Bắt mạch tổng quát ----------------

    def bat_mach(self, benh_nhan=None):
        """Xem toàn bộ khí huyết dự án: chỗ nào là huyệt hiểm, chỗ nào khí chết"""
        mach = self.dung_mach_do(benh_nhan)
        ky_uc = mach["ky_uc"]
        files = ky_uc.get("files", {})

        if not files:
            print("⚠️ [THIẾT CHẨN]: Ký ức trống. Hãy chạy 'nhai' để Tỳ Tạng tiêu hóa dự án trước.")
            return None

        # Huyệt hiểm: hàm được nhiều nơi gọi -> đụng vào là chấn động toàn thân
        huyet_hiem = sorted(
            ((ten, len(set(ds))) for ten, ds in mach["nguoi_goi"].items()),
            key=lambda x: -x[1]
        )[:10]

        # Khí chết: định nghĩa rồi bỏ đó - không ai gọi VÀ cũng không ai nhắc tên.
        # Phải xét cả "nhắc tên", vì callback gắn vào Đốc Mạch không hề bị gọi thẳng.
        rieng_tu = lambda t: t.startswith('_') or t in {
            'main', '__init__', 'setup_ui', 'run'
        }
        khi_chet = sorted(
            ten for ten in mach["noi_sinh"]
            if ten not in mach["nguoi_goi"]
            and ten not in mach["nguoi_nhac"]
            and not rieng_tu(ten)
        )

        print("\n" + "✨ " * 5)
        print(f"🫀 [THIẾT CHẨN]: BẮT MẠCH DỰ ÁN {os.path.basename(mach['benh_nhan'])}")
        print("✨ " * 5)
        print(f"\n📊 Ký ức đang giữ {len(files)} file, "
              f"{len(mach['noi_sinh'])} tên hàm/class.")

        if huyet_hiem and huyet_hiem[0][1] > 0:
            print("\n🔴 HUYỆT HIỂM (sửa vào là chấn động nhiều nơi):")
            for ten, so in huyet_hiem:
                if so > 0:
                    print(f"   {ten:<28} ← {so} nơi đang gọi")

        if khi_chet:
            print(f"\n💀 KHÍ CHẾT ({len(khi_chet)} hàm không ai gọi tới):")
            for ten in khi_chet[:15]:
                print(f"   • {ten}")
            if len(khi_chet) > 15:
                print(f"   ... và {len(khi_chet) - 15} chỗ nữa.")

        # File phình to: Vọng Chẩn nhìn thấy, Thiết Chẩn xác nhận bằng số liệu
        phinh = [(k, v.get("dong", 0)) for k, v in files.items()
                 if v.get("dong", 0) > cfg.NGUONG_PHINH_TO]
        if phinh:
            print(f"\n🔴 TẠNG PHỦ PHÌNH TO (quá {cfg.NGUONG_PHINH_TO} dòng):")
            for k, d in sorted(phinh, key=lambda x: -x[1]):
                print(f"   {k:<40} {d:>5} dòng")

        print("-" * 60 + "\n")
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"THIẾT CHẨN: Đã bắt mạch {len(files)} file."
        )
        return mach

    # ---------------- Chống ảo giác ----------------

    def kiem_tra_ao_giac(self, danh_sach_ten, benh_nhan=None):
        """AI vừa nhắc tới các tên này - có thật không hay nó bịa?"""
        mach = self.dung_mach_do(benh_nhan)
        co_that, bia_dat = [], []
        for ten in danh_sach_ten:
            (co_that if ten in mach["noi_sinh"] else bia_dat).append(ten)
        return {"co_that": co_that, "bia_dat": bia_dat}


thiet_chan_trung_uong = ThietChan()
