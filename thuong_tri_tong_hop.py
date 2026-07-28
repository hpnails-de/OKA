# thuong_tri_tong_hop.py
# THƯỢNG TRÍ (Abstract Mind) - đứng TRÊN Ngũ Tạng/Lục Phủ, không phải một
# tạng phủ vật lý. Đúng vị trí phân tầng trong huyền bí học: Thân xác (Ngũ
# Tạng/Lục Phủ) -> Trí (module này).
#
# Hạ Trí (Vọng Chẩn, Thiết Chẩn, Tỳ Tạng) chỉ xử lý CỤ THỂ, RỜI RẠC: đếm
# dòng, đếm số nơi gọi, so khớp tên theo mẫu. Mỗi module chỉ thấy MỘT MẢNH
# của bức tranh - không module nào tự biết "đây là landmine nguy hiểm",
# chúng chỉ báo con số thô.
#
# Thượng Trí không đọc lại file, không tính gì mới. Nó gọi lại đúng những
# hàm Hạ Trí ĐÃ tính (dùng bản _tinh_mach/_phan_tich không in gì, để khỏi
# in lặp report), GHÉP nhiều tín hiệu rời rạc lại, và rút ra kết luận bằng
# ngôn ngữ tự nhiên - việc tổng hợp mà không tầng Hạ Trí nào tự làm được.

import os

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong
from nham_mach_store import nham_mach_trung_uong
from thiet_chan_pulse import thiet_chan_trung_uong
from vong_chan_diagnostic import vong_chan_trung_uong


class ThuongTri:
    def __init__(self):
        # Đăng ký nghe CÙNG sự kiện với Thiết Chẩn ('mach'). Thứ tự chạy phụ
        # thuộc thứ tự import trong main_kosmon.py - module này phải được
        # import SAU thiet_chan_pulse để Thiết Chẩn in report trước, Thượng
        # Trí tổng hợp sau (đúng thứ tự Hạ Trí báo cáo rồi Thượng Trí kết luận).
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_BAT_MACH", self.tong_hop)

    def _dem_ham_trong_file(self, mach, khoa):
        tinh_hoa = mach["ky_uc"].get("files", {}).get(khoa, {})
        so = len(tinh_hoa.get("ham", {}))
        for than in tinh_hoa.get("classes", {}).values():
            so += len(than.get("methods", {}))
        return so

    def tong_hop(self, benh_nhan=None):
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()

        mach = thiet_chan_trung_uong._tinh_mach(benh_nhan)
        if mach is None:
            return None
        nguyen_khi, di_vat = vong_chan_trung_uong._phan_tich(benh_nhan)

        nguyen_khi_ten = {rel for rel, _, _ in nguyen_khi}
        di_vat_ten = {rel for rel, _, _ in di_vat}
        phinh_ten = {k for k, _ in mach["phinh"]}

        nhan_dinh = []

        # Tên quy ước OOP phổ biến (class nào cũng có __init__/run/stop...) -
        # trùng tên ở đây là chuyện thường, không phải dấu hiệu landmine.
        # Chỉ những tên ĐẶC THÙ (rpc_call, HistoryThread, save_block...) trùng
        # nhau mới đáng ngờ thật.
        quy_uoc_pho_bien = {
            '__init__', 'run', 'stop', 'start', 'main', 'setup_ui',
            'update', 'close', 'connect',
        }

        # --- A: Trùng tên nguy hiểm giữa code chính chủ và dị vật ---
        for ten, khoa_list in mach["noi_sinh"].items():
            if ten in quy_uoc_pho_bien or ten.startswith('_'):
                continue
            khoa_set = set(khoa_list)
            if len(khoa_set) < 2:
                continue
            o_di_vat = khoa_set & di_vat_ten
            o_chinh_chu = khoa_set & nguyen_khi_ten
            if o_di_vat and o_chinh_chu:
                nhan_dinh.append(
                    f"⚠️ '{ten}' bị định nghĩa TRÙNG TÊN ở cả code chính chủ "
                    f"({', '.join(sorted(o_chinh_chu))}) lẫn dị vật "
                    f"({', '.join(sorted(o_di_vat))}). Lỡ import nhầm file dị "
                    f"vật là mọi sửa lỗi trong bản chính chủ coi như vô nghĩa "
                    f"mà không ai biết."
                )

        # --- B: Huyệt hiểm nằm trong file phình to - rủi ro kép ---
        for ten, so in mach["huyet_hiem"]:
            if so <= 0 or ten in quy_uoc_pho_bien or ten.startswith('_'):
                continue
            o_phinh = sorted({k for k in mach["noi_sinh"].get(ten, []) if k in phinh_ten})
            if o_phinh:
                nhan_dinh.append(
                    f"🔴 '{ten}' vừa là huyệt hiểm ({so} nơi gọi) vừa nằm trong "
                    f"file phình to ({', '.join(o_phinh)}) - sửa sai ảnh hưởng "
                    f"nhiều nơi, mà file quá dài nên khó review kỹ."
                )

        # --- C: Khí chết dồn vào một file - có thể cả file là rác ---
        khi_chet_theo_file = {}
        for ten in mach["khi_chet"]:
            for khoa in mach["noi_sinh"].get(ten, []):
                khi_chet_theo_file.setdefault(khoa, []).append(ten)
        for khoa, ds in khi_chet_theo_file.items():
            tong_ham = self._dem_ham_trong_file(mach, khoa)
            if tong_ham > 0 and len(ds) >= 3 and len(ds) / tong_ham >= 0.7:
                nhan_dinh.append(
                    f"💀 File '{khoa}' có {len(ds)}/{tong_ham} hàm là khí chết "
                    f"(~{len(ds) / tong_ham:.0%}) - nhiều khả năng cả file là "
                    f"rác còn sót, nên cân nhắc xóa hẳn thay vì dọn từng hàm."
                )

        # --- D: Tỷ trọng dị vật quá cao ---
        tong = len(nguyen_khi) + len(di_vat)
        if tong > 0 and len(di_vat) / tong > 0.5:
            nhan_dinh.append(
                f"📦 Dị vật chiếm {len(di_vat)}/{tong} file "
                f"(~{len(di_vat) / tong:.0%}) trong dự án - nên dọn rác trước "
                f"khi làm thêm tính năng mới."
            )

        if not nhan_dinh:
            nhan_dinh.append("🟢 Không phát hiện tổ hợp rủi ro nào đáng báo động lúc này.")

        ket_luan = "\n".join(f"   {d}" for d in nhan_dinh)

        print("\n" + "🧠 " * 5)
        print(f"🧠 [THƯỢNG TRÍ]: TỔNG HỢP NHẬN ĐỊNH - {os.path.basename(benh_nhan)}")
        print("🧠 " * 5)
        print(ket_luan)
        print("-" * 60 + "\n")

        # Nhâm Mạch chỉ giữ CON TRỎ tới kết luận mới nhất - Tâm Tạng đọc lại
        # từ đây khi xuất Chân Kinh, không cần Thượng Trí tự ghép vào chuỗi
        # của Tâm Tạng (tách trách nhiệm rõ ràng, đúng tinh thần Nhâm Mạch).
        nham_mach_trung_uong.cap_nhat("ket_luan_thuong_tri", {
            "benh_nhan": benh_nhan,
            "van_ban": ket_luan,
        })

        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"THƯỢNG TRÍ: Đã tổng hợp {len(nhan_dinh)} nhận định."
        )
        return nhan_dinh


thuong_tri_trung_uong = ThuongTri()
