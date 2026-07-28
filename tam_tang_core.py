# tam_tang_core.py
# TÂM TẠNG - Tâm tàng Thần, bậc quân vương: giữ Bối Cảnh và xuất Chân Kinh
#
# Trước đây Tâm Tạng lắng nghe sự kiện "CODE_DA_TIEU_HOA" nhưng Tỳ Tạng
# chưa bao giờ phát tín hiệu ấy - dây thần kinh bị đứt, nên Chân Kinh luôn rỗng.
# Nay dây đã nối, và Tâm đọc thẳng ký ức của Tỳ theo từng bệnh nhân.

import os

import oka_config as cfg
from nham_mach_store import nham_mach_trung_uong
from doc_mach_bus import xuong_song_trung_uong
from ty_tang_parser import ty_tang_trung_uong


# Đếm token THẬT nếu máy có tiktoken; không có thì lùi về ước lượng thô.
# Đã đo trên dự án thật: ước lượng len//4 lệch khoảng 13-15% so với số thật,
# NHƯNG tỷ lệ tiết kiệm gần như không đổi (96.4% ước tính vs 96.3% thật) vì
# sai số ở tử và mẫu triệt tiêu nhau. Vẫn nên dùng số thật khi có, để con số
# tuyệt đối in ra không sai lệch.
try:
    import tiktoken
    _BO_MA_HOA = tiktoken.get_encoding("cl100k_base")
except Exception:
    _BO_MA_HOA = None


def uoc_luong_token(van_ban):
    """Số token. Chính xác nếu có tiktoken, không thì ~4 ký tự một token."""
    if _BO_MA_HOA is not None:
        try:
            return max(1, len(_BO_MA_HOA.encode(van_ban)))
        except Exception:
            pass
    return max(1, len(van_ban) // 4)


class TamTang:
    def __init__(self):
        # Tỳ tiêu hóa xong thì Tâm ghi nhận bối cảnh mới
        xuong_song_trung_uong.dang_ky_nhan_khi("CODE_DA_TIEU_HOA", self.cap_nhat_tri_nho)
        # Vị Tạng (hoặc GUI) xin Chân Kinh
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_CHAN_KINH", self.giang_giai_chan_kinh)

    def cap_nhat_tri_nho(self, benh_nhan=None):
        """Nhâm Mạch chỉ giữ CON TRỎ tới ký ức, không sao chép lại ký ức.

        Đây là lối đi của Hippocampus: nó không chứa ký ức, nó chỉ đánh chỉ mục
        rồi trỏ về nơi ký ức thực sự nằm. Sao chép hai bản là tự chuốc lệch pha.
        """
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        ky_uc = ty_tang_trung_uong.tai_ky_uc(benh_nhan)

        nham_mach_trung_uong.cap_nhat("benh_nhan_hien_tai", benh_nhan)
        nham_mach_trung_uong.cap_nhat("chi_muc_ky_uc", {
            "duong_dan": cfg.duong_dan_ky_uc(benh_nhan),
            "so_file": len(ky_uc.get("files", {})),
            "cap_nhat": ky_uc.get("cap_nhat"),
        })

    # ---------------- Chân Kinh ----------------

    def xuat_chan_kinh_cho_ai(self, benh_nhan=None, loc=None, kem_chu_ky=True):
        """Biến ký ức thành Prompt súc tích để AI hết 'ngáo' bối cảnh.

        loc: chỉ lấy các file có chứa từ khóa này (retrieval theo cue,
             thay vì dội cả dự án vào mặt AI).
        """
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        ky_uc = ty_tang_trung_uong.tai_ky_uc(benh_nhan)
        files = ky_uc.get("files", {})

        if not files:
            return ("⚠️ Ký ức đang trống rỗng.\n"
                    "→ Hãy gõ lệnh 'nhai' để Tỳ Tạng tiêu hóa dự án trước.")

        if loc:
            khoa_lay = {k: v for k, v in files.items() if loc.lower() in k.lower()}
            if not khoa_lay:
                return f"⚠️ Không có file nào khớp với '{loc}' trong ký ức."
        else:
            khoa_lay = files

        dong = [
            "### 📜 BỐI CẢNH DỰ ÁN (Master Context) ###",
            f"Dự án: {os.path.basename(benh_nhan)}",
            "Đây là toàn bộ class/hàm ĐANG TỒN TẠI. Chỉ được dùng những tên có trong đây;",
            "nếu cần thứ chưa có, phải nói rõ là tạo mới.",
            "",
        ]

        # Thượng Trí đã tổng hợp nhận định (nếu đã chạy 'mach' cho đúng bệnh
        # nhân này) - gắn lên đầu để AI đọc cảnh báo trước khi đụng vào code,
        # không chỉ người ngồi xem terminal mới thấy.
        ket_luan = nham_mach_trung_uong.lay_khi_huyet("ket_luan_thuong_tri")
        if ket_luan and ket_luan.get("benh_nhan") == benh_nhan:
            dong = [
                "### 🧠 NHẬN ĐỊNH THƯỢNG TRÍ (đọc trước khi sửa code) ###",
                ket_luan["van_ban"],
                "",
            ] + dong

        for khoa in sorted(khoa_lay):
            tinh_hoa = khoa_lay[khoa]
            dong.append(f"📂 {khoa}  ({tinh_hoa.get('dong', '?')} dòng)")

            for ten_cls, than in tinh_hoa.get("classes", {}).items():
                ke_thua = than.get("ke_thua") or []
                dau = f"({', '.join(ke_thua)})" if ke_thua else ""
                dong.append(f"   ▸ class {ten_cls}{dau}")
                for ten_m, ky in than.get("methods", {}).items():
                    dong.append(f"       - {ten_m}{ky if kem_chu_ky else '()'}")

            for ten_h, ky in tinh_hoa.get("ham", {}).items():
                dong.append(f"   ▸ def {ten_h}{ky if kem_chu_ky else '()'}")

            dong.append("")

        dong.append("[NHIỆM VỤ]: Bám sát cấu trúc trên khi thực hiện yêu cầu tiếp theo.")
        return "\n".join(dong)

    def giang_giai_chan_kinh(self, du_lieu=None):
        """In Chân Kinh ra Terminal kèm số liệu tiết kiệm token"""
        benh_nhan, loc = None, None
        if isinstance(du_lieu, dict):
            benh_nhan, loc = du_lieu.get("benh_nhan"), du_lieu.get("loc")
        elif isinstance(du_lieu, str) and du_lieu:
            loc = du_lieu

        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        chan_kinh = self.xuat_chan_kinh_cho_ai(benh_nhan, loc=loc)

        print("\n" + "=" * 60)
        print("✨ [TÂM TẠNG]: CHÂN KINH BỐI CẢNH DỰ ÁN")
        print("=" * 60)
        print(chan_kinh)
        print("=" * 60)
        print(self.do_cong_luc(benh_nhan, chan_kinh, loc=loc))
        print("💡 Copy đoạn trên dán cho AI trước khi nhờ nó sửa code.")
        print("=" * 60 + "\n")

        xuong_song_trung_uong.phat_khi("GHI_LOG", "TÂM TẠNG: Đã xuất Chân Kinh.")
        return chan_kinh

    def do_cong_luc(self, benh_nhan, chan_kinh, loc=None):
        """Đo mức nén - biến niềm tin thành số.

        Phải so đúng phạm vi: lọc lấy 1 file thì so với source của đúng file đó.
        Đem Chân Kinh của một file so với source cả dự án là tự khen dối lòng.
        """
        ky_uc = ty_tang_trung_uong.tai_ky_uc(benh_nhan)
        files = ky_uc.get("files", {})
        if loc:
            files = {k: v for k, v in files.items() if loc.lower() in k.lower()}

        tong_dong = sum(v.get("dong", 0) for v in files.values())
        if tong_dong <= 0:
            return ""

        # ĐỌC THẲNG file thật để đếm cho đúng. Bản cũ đoán "mỗi dòng ~10
        # token" - đo lại bằng tiktoken trên dự án thật thì con số đoán này
        # thấp hơn thực tế ~17% (149.150 đoán vs 179.145 thật), tức là đang
        # tự khai KHIÊM TỐN hơn thực lực. Vẫn nên sửa: một công cụ đo mức nén
        # mà chính phép đo lại ước lượng thì mất tin cậy.
        token_tho = 0
        doc_duoc_het = True
        for khoa in files:
            duong_dan = os.path.join(benh_nhan, khoa)
            try:
                with open(duong_dan, "r", encoding="utf-8", errors="replace") as f:
                    token_tho += uoc_luong_token(f.read())
            except OSError:
                doc_duoc_het = False
                break

        if not doc_duoc_het or token_tho <= 0:
            token_tho = tong_dong * 10   # đường lui khi file đã bị xóa/đổi chỗ

        token_kinh = uoc_luong_token(chan_kinh)
        # Chia số nguyên làm tròn xuống, nên khi Chân Kinh nhỏ hơn 1% source
        # thì "100 - 0" ra đúng 100% - hiện "Tiết kiệm 100%" là nói dối trắng
        # trợn (nghĩa là không tốn token nào). Dùng số thực và cắt trần 99.9%.
        ti_le = 100.0 - (token_kinh * 100.0 / token_tho)
        ti_le_chu = f"{min(ti_le, 99.9):.1f}"

        do_chinh_xac = "đo thật" if _BO_MA_HOA is not None else "ước lượng"
        pham_vi = f"{len(files)} file" + (f" khớp '{loc}'" if loc else "")
        return (f"📊 [{pham_vi}]  Ném cả source: ~{token_tho:,} token  |  "
                f"Chân Kinh: ~{token_kinh:,} token  |  "
                f"Tiết kiệm ~{ti_le_chu}%  ({do_chinh_xac})")


# Khởi tạo thực thể Tâm Tạng duy nhất
tam_tang_trung_uong = TamTang()
