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
from can_tang_goc import can_tang_trung_uong
import phan_vu_vong
import ty_ngo_luu_chu


class ThuongTri:
    def __init__(self):
        # Đăng ký nghe CÙNG sự kiện với Thiết Chẩn ('mach'). Thứ tự chạy phụ
        # thuộc thứ tự import trong main_kosmon.py - module này phải được
        # import SAU thiet_chan_pulse để Thiết Chẩn in report trước, Thượng
        # Trí tổng hợp sau (đúng thứ tự Hạ Trí báo cáo rồi Thượng Trí kết luận).
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_BAT_MACH", self.tong_hop)

    def _dem_ham_trong_file(self, mach, khoa):
        """Đếm đúng số 'tên' mà file này định nghĩa - PHẢI khớp với cách
        dung_mach_do() (thiet_chan_pulse.py) xây noi_sinh, vì đó chính là
        nguồn của khi_chet. Bug từng gặp: quên cộng số CLASS (chỉ cộng
        methods bên trong), khiến mẫu số thiếu -> tỷ lệ khí chết có thể
        vượt quá 100% (23/22 hàm) một cách vô lý.
        """
        tinh_hoa = mach["ky_uc"].get("files", {}).get(khoa, {})
        classes = tinh_hoa.get("classes", {})
        so = len(tinh_hoa.get("ham", {})) + len(classes)  # +len(classes): chính class cũng là 1 "tên" trong noi_sinh
        for than in classes.values():
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

        # Mỗi nhận định kèm ĐỘ TIN CẬY, để người/AI đọc biết chỗ nào tin được
        # ngay và chỗ nào phải tự kiểm lại:
        #   CHAC   = đọc thẳng từ cấu trúc code (đếm được, không cãi được)
        #   DOAN   = dựa trên quy tắc phỏng đoán, HOÀN TOÀN có thể sai
        # Đây là điểm mà công cụ phân tích tĩnh hay giấu: gộp chung mọi kết
        # luận thành một giọng chắc nịch, khiến người đọc tin cả những chỗ
        # thực chất chỉ là đoán.
        CHAC, DOAN = "CHẮC CHẮN", "SUY ĐOÁN"
        nhan_dinh = []          # [(do_tin_cay, van_ban), ...]

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
                # Việc TRÙNG TÊN là chắc chắn (đọc thẳng từ AST). Nhưng việc
                # xếp file nào là "dị vật" lại dựa trên quy tắc đoán theo tên
                # thư mục -> cả nhận định phải hạ xuống mức SUY ĐOÁN.
                nhan_dinh.append((DOAN,
                    f"⚠️ '{ten}' bị định nghĩa TRÙNG TÊN ở cả code chính chủ "
                    f"({', '.join(sorted(o_chinh_chu))}) lẫn dị vật "
                    f"({', '.join(sorted(o_di_vat))}). Lỡ import nhầm file dị "
                    f"vật là mọi sửa lỗi trong bản chính chủ coi như vô nghĩa "
                    f"mà không ai biết. (Việc trùng tên là chắc chắn; việc xếp "
                    f"loại 'dị vật' chỉ là phỏng đoán theo tên/vị trí thư mục.)"
                ))

        # --- B: Huyệt hiểm nằm trong file phình to - rủi ro kép ---
        for ten, so in mach["huyet_hiem"]:
            if so <= 0 or ten in quy_uoc_pho_bien or ten.startswith('_'):
                continue
            o_phinh = sorted({k for k in mach["noi_sinh"].get(ten, []) if k in phinh_ten})
            if o_phinh:
                # Số nơi gọi và số dòng đều ĐẾM ĐƯỢC từ code - không phải đoán.
                nhan_dinh.append((CHAC,
                    f"🔴 '{ten}' vừa là huyệt hiểm ({so} nơi gọi) vừa nằm trong "
                    f"file phình to ({', '.join(o_phinh)}) - sửa sai ảnh hưởng "
                    f"nhiều nơi, mà file quá dài nên khó review kỹ."
                ))

        # --- C: Khí chết dồn vào một file - có thể cả file là rác ---
        khi_chet_theo_file = {}
        for ten in mach["khi_chet"]:
            for khoa in mach["noi_sinh"].get(ten, []):
                khi_chet_theo_file.setdefault(khoa, []).append(ten)
        for khoa, ds in khi_chet_theo_file.items():
            tong_ham = self._dem_ham_trong_file(mach, khoa)
            if tong_ham > 0 and len(ds) >= 3 and len(ds) / tong_ham >= 0.7:
                # "Không ai gọi" chỉ đúng trong PHẠM VI QUÉT TĨNH. Hàm có thể
                # được gọi động (getattr, eval), qua route web, qua CLI, hoặc
                # từ dự án khác import sang - phân tích tĩnh không thấy được.
                nhan_dinh.append((DOAN,
                    f"💀 File '{khoa}' có {len(ds)}/{tong_ham} hàm là khí chết "
                    f"(~{len(ds) / tong_ham:.0%}) - nhiều khả năng cả file là "
                    f"rác còn sót, nên cân nhắc xóa hẳn thay vì dọn từng hàm. "
                    f"(Cẩn trọng: hàm gọi động/qua route/entry point sẽ bị "
                    f"phân tích tĩnh tưởng nhầm là chết.)"
                ))

        # --- E: Phản Vũ - vòng phụ thuộc luẩn quẩn ---
        # CHẮC CHẮN: dựng từ câu lệnh import thật, không suy diễn.
        canh_phu_thuoc = {}
        try:
            canh_phu_thuoc = phan_vu_vong.dung_do_thi_co_huong(mach)
            for van in phan_vu_vong.ke_lai(phan_vu_vong.soi_phan_vu(mach)):
                nhan_dinh.append((CHAC, van))
        except Exception:
            pass

        # --- F: Tý Ngọ Lưu Chú - liên kết ẩn theo thời gian ---
        # SUY ĐOÁN: suy luận thống kê từ lịch sử sửa, không phải bằng chứng.
        try:
            for van in ty_ngo_luu_chu.ke_lai(
                ty_ngo_luu_chu.soi_lien_ket_an(benh_nhan, mach, canh_phu_thuoc)
            ):
                nhan_dinh.append((DOAN, van))
        except Exception:
            pass

        # --- D2: Can Tạng - file tái phát (Anthony William: vá triệu chứng
        # mãi không chạm gốc thì bệnh cứ tái đi tái lại). Chỉ đáng nói khi
        # file đó CŨNG là huyệt hiểm hoặc phình to - tái phát ở một file nhỏ,
        # không ai gọi thì không đáng bận tâm bằng.
        goc_so_lieu = can_tang_trung_uong._thong_ke(benh_nhan)
        if goc_so_lieu:
            huyet_hiem_ten = {ten for ten, so in mach["huyet_hiem"] if so > 0}
            for ten_file, gan, tong in goc_so_lieu["qua_tai"]:
                # noi_sinh dùng đường dẫn tương đối (vd 'engine\\rpc.py'), còn
                # Can Tạng chỉ có basename - so khớp theo đuôi đường dẫn.
                lien_quan_huyet_hiem = any(
                    ten in huyet_hiem_ten and any(k.endswith(ten_file) for k in ds)
                    for ten, ds in mach["noi_sinh"].items()
                )
                lien_quan_phinh = any(k.endswith(ten_file) for k in phinh_ten)
                if lien_quan_huyet_hiem or lien_quan_phinh:
                    # Số lần sửa là dữ liệu thật (đếm từ kho Nguyên Khí), nhưng
                    # kết luận "đang vá triệu chứng" là diễn giải của con người.
                    nhan_dinh.append((DOAN,
                        f"🫘 '{ten_file}' vừa bị sửa cấu trúc {gan} lần trong "
                        f"{cfg.KHUNG_GIO_QUA_TAI}h gần đây, VỪA là huyệt hiểm/file "
                        f"phình to - dấu hiệu đang vá triệu chứng ở một chỗ vốn đã "
                        f"rủi ro cao, chưa chạm gốc. (Số lần sửa là thật; cách "
                        f"diễn giải là phỏng đoán - có thể bạn đang cố ý làm lớn "
                        f"một tính năng ở đó.)"
                    ))

        # --- D: Tỷ trọng dị vật quá cao ---
        tong = len(nguyen_khi) + len(di_vat)
        if tong > 0 and len(di_vat) / tong > 0.5:
            nhan_dinh.append((DOAN,
                f"📦 Dị vật chiếm {len(di_vat)}/{tong} file "
                f"(~{len(di_vat) / tong:.0%}) trong dự án - nên dọn rác trước "
                f"khi làm thêm tính năng mới. (Nhãn 'dị vật' dựa trên tên và vị "
                f"trí thư mục, script tiện ích thật cũng có thể bị xếp nhầm.)"
            ))

        if not nhan_dinh:
            nhan_dinh.append((CHAC, "🟢 Không phát hiện tổ hợp rủi ro nào đáng báo động lúc này."))

        # Xếp CHẮC CHẮN lên trước - đọc từ trên xuống là đi từ chắc tới đoán
        nhan_dinh.sort(key=lambda x: 0 if x[0] == CHAC else 1)
        ket_luan = "\n".join(f"   [{do:^9}] {van}" for do, van in nhan_dinh)

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
