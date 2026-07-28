# gui_nhan_tang.py
# NHÃN TẠNG - Giao diện chỉ huy Tiểu Vũ Trụ OKA
#
# Sửa: thiếu customtkinter thì báo tử tế rồi chỉ đường sang bản dòng lệnh,
# thay vì quăng ImportError vào mặt người dùng trên máy mới.

import os
import sys
from datetime import datetime

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

try:
    import customtkinter as ctk
except ImportError:
    print("❌ [NHÃN TẠNG]: Chưa có thư viện giao diện 'customtkinter'.")
    print("   Cài bằng:   pip install customtkinter")
    print("   Hoặc dùng bản dòng lệnh (đầy đủ tính năng):   python main_kosmon.py")
    sys.exit(1)

# Triệu hồi các Tạng Phủ - mỗi module tự nối dây thần kinh khi được import
import nham_mach_store          # noqa: F401
import bang_quang_logger
import dom_validator            # noqa: F401
import tieu_truong_linter       # noqa: F401
import ty_tang_parser           # noqa: F401
import than_tang_backup         # noqa: F401
import dai_truong_cleaner       # noqa: F401
import tam_tieu_network         # noqa: F401
import vong_chan_diagnostic     # noqa: F401
import thiet_chan_pulse         # noqa: F401
from tam_tang_core import tam_tang_trung_uong
from phe_watchdog import khoi_dong_nhip_tho, CO_WATCHDOG


class OkaGui(ctk.CTk):
    def __init__(self, toa_do_du_an=None):
        super().__init__()

        self.benh_nhan = toa_do_du_an or cfg.benh_nhan_hien_tai()
        self.title("M4VN - OKA KOSMON ARCHITECT V2.0")
        self.geometry("1150x720")
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=210, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="OKA SYSTEM",
                     font=("Orbitron", 24, "bold"), text_color="#2ECC71").pack(pady=20)

        nut = [
            ("🍚 NHAI DỰ ÁN", self.lenh_nhai, "#16A085"),
            ("🩺 VỌNG CHẨN", self.lenh_kham, "#2980B9"),
            ("🫀 THIẾT CHẨN", self.lenh_mach, "#D35400"),
            ("📜 XUẤT CHÂN KINH", self.lenh_kinh, "#8E44AD"),
            ("💩 ĐÀO THẢI RÁC", self.lenh_don, "#C0392B"),
        ]
        for text, cmd, mau in nut:
            ctk.CTkButton(self.sidebar, text=text, command=cmd, fg_color=mau).pack(pady=7, padx=20)

        ctk.CTkLabel(self.sidebar, text="Bắt mạch một hàm:",
                     font=("Arial", 11)).pack(pady=(20, 2))
        self.o_nhap_ham = ctk.CTkEntry(self.sidebar, placeholder_text="tên hàm...")
        self.o_nhap_ham.pack(padx=20)
        self.o_nhap_ham.bind("<Return>", lambda e: self.lenh_do_anh_huong())
        ctk.CTkButton(self.sidebar, text="Ai đang gọi?",
                      command=self.lenh_do_anh_huong, fg_color="#34495E").pack(pady=6, padx=20)

        ctk.CTkLabel(self.sidebar, text="Trạng thái Phế:", font=("Arial", 12)).pack(pady=(30, 0))
        self.lbl_status = ctk.CTkLabel(
            self.sidebar,
            text="🟢 ĐANG THỞ" if CO_WATCHDOG else "🟡 THỞ CHẬM",
            text_color="#2ECC71" if CO_WATCHDOG else "#F1C40F",
            font=("Arial", 14, "bold"))
        self.lbl_status.pack()

        # --- MAIN ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.stats_frame = ctk.CTkFrame(self.main_frame, height=110)
        self.stats_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))

        self.o_thong_so = {}
        for i, ten in enumerate(["TÂM (Ký ức)", "TỲ (File)", "THẬN (Nguyên Khí)", "PHẾ (Hô hấp)"]):
            self.o_thong_so[ten] = self._tao_o_thong_so(ten, "...", i)

        self.log_display = ctk.CTkTextbox(self.main_frame, font=("Consolas", 13))
        self.log_display.grid(row=1, column=0, sticky="nsew")

        # Bàng Quang gửi log vào đây thay vì chỉ ra terminal
        xuong_song_trung_uong.dang_ky_nhan_khi("GHI_LOG", self.cap_nhat_log_gui)

        khoi_dong_nhip_tho(self.benh_nhan)
        self.ghi(f"🏥 Bệnh nhân: {self.benh_nhan}")
        if not CO_WATCHDOG:
            self.ghi("ℹ️ Thiếu 'watchdog' → Phế thở chậm (quét mỗi 3 giây).")
        self.ghi("Hệ thống OKA đã khởi động Nhãn Tạng thành công.")
        self.lam_moi_thong_so()

    # ---------- tiện ích ----------

    def _tao_o_thong_so(self, ten, val, col):
        f = ctk.CTkFrame(self.stats_frame, width=150, height=75,
                         border_width=1, border_color="#333")
        f.grid(row=0, column=col, padx=14, pady=14)
        ctk.CTkLabel(f, text=ten, font=("Arial", 11, "bold")).pack()
        lbl = ctk.CTkLabel(f, text=val, font=("Arial", 18), text_color="#2ECC71")
        lbl.pack()
        return lbl

    def ghi(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_display.insert("end", f"[{now}] {msg}\n")
        self.log_display.see("end")

    def cap_nhat_log_gui(self, msg):
        self.ghi(str(msg))
        self.lam_moi_thong_so()

    def lam_moi_thong_so(self):
        """Số liệu thật, không còn là chữ chết cứng trong code như bản cũ"""
        ky_uc = ty_tang_parser.ty_tang_trung_uong.tai_ky_uc(self.benh_nhan)
        so_file = len(ky_uc.get("files", {}))
        kho = cfg.kho_nguyen_khi(self.benh_nhan)
        so_bak = len(os.listdir(kho)) if os.path.isdir(kho) else 0

        self.o_thong_so["TÂM (Ký ức)"].configure(text="OK" if so_file else "Trống")
        self.o_thong_so["TỲ (File)"].configure(text=str(so_file))
        self.o_thong_so["THẬN (Nguyên Khí)"].configure(text=str(so_bak))
        self.o_thong_so["PHẾ (Hô hấp)"].configure(text="Sâu" if CO_WATCHDOG else "Chậm")

    # ---------- khẩu lệnh ----------

    def lenh_nhai(self):
        self.ghi("🍚 Tỳ Tạng đang tiêu hóa dự án...")
        xuong_song_trung_uong.phat_khi("YEU_CAU_NHAI", self.benh_nhan)

    def lenh_kham(self):
        self.ghi("🩺 Vọng Chẩn - xem terminal để đọc báo cáo đầy đủ.")
        xuong_song_trung_uong.phat_khi("YEU_CAU_KHAM_BENH", self.benh_nhan)

    def lenh_mach(self):
        self.ghi("🫀 Thiết Chẩn - xem terminal để đọc báo cáo đầy đủ.")
        xuong_song_trung_uong.phat_khi("YEU_CAU_BAT_MACH", self.benh_nhan)

    def lenh_do_anh_huong(self):
        ten = self.o_nhap_ham.get().strip()
        if not ten:
            return
        kq = thiet_chan_pulse.thiet_chan_trung_uong.do_anh_huong(
            {"ten": ten, "benh_nhan": self.benh_nhan})
        if not kq or not kq["sinh_tai"]:
            self.ghi(f"❓ '{ten}' KHÔNG có trong dự án → nếu AI vừa dùng tên này, nó đang ảo giác.")
        else:
            self.ghi(f"🫀 '{ten}' định nghĩa tại {', '.join(kq['sinh_tai'])}; "
                     f"{len(kq['bi_goi_tai'])} nơi gọi thẳng, {len(kq['bi_nhac_tai'])} nơi nhắc tên.")

    def lenh_kinh(self):
        chan_kinh = tam_tang_trung_uong.xuat_chan_kinh_cho_ai(self.benh_nhan)
        self.log_display.insert("end", f"\n{chan_kinh}\n")
        self.log_display.insert(
            "end", tam_tang_trung_uong.do_cong_luc(self.benh_nhan, chan_kinh) + "\n")
        self.log_display.see("end")

    def lenh_don(self):
        xuong_song_trung_uong.phat_khi("YEU_CAU_DON_RAC", self.benh_nhan)


if __name__ == "__main__":
    duong_dan = sys.argv[1] if len(sys.argv) > 1 else None
    if duong_dan:
        cfg.chon_benh_nhan(duong_dan)
    app = OkaGui(duong_dan)
    app.mainloop()
