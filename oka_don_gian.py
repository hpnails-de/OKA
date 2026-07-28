# oka_don_gian.py
# Giao diện MỘT CÚ CLICK cho người dùng phổ thông - không cần gõ lệnh gì.
#
# Trước đây main_kosmon.py chỉ có giao diện dòng lệnh (gõ 'nhai', 'mach',
# 'kinh'...) - với người quen terminal thì ổn, nhưng với người thường thì
# rối. File này: mở một cửa sổ nhỏ, bấm nút chọn thư mục dự án, OKA tự chạy
# hết toàn bộ chuỗi khám (nhai -> kham -> mach -> goc -> kinh) và xuất RA
# ĐÚNG MỘT FILE duy nhất để dán cho AI - không cần biết gì về Ngũ Tạng/Lục
# Phủ bên trong cũng dùng được.
#
# Chỉ dùng tkinter (có sẵn trong mọi bản cài Python chuẩn) - không cần
# customtkinter, không cần pip install gì cả.

import os
import sys
import io
import contextlib
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

# Triệu hồi các Tạng Phủ cần cho một lượt khám trọn vẹn. KHÔNG triệu hồi
# phe_watchdog/vi_receiver ở đây - tool này chạy một lượt rồi xuất file,
# không cần "thở" liên tục theo dõi thay đổi hay bàn phím dòng lệnh.
import nham_mach_store          # noqa: F401
import bang_quang_logger        # noqa: F401
import dom_validator            # noqa: F401
import tieu_truong_linter       # noqa: F401
import ty_tang_parser           # noqa: F401
import than_tang_backup         # noqa: F401
import tam_tang_core
import dai_truong_cleaner       # noqa: F401
import tam_tieu_network         # noqa: F401
import vong_chan_diagnostic     # noqa: F401
import thiet_chan_pulse         # noqa: F401
import can_tang_goc             # noqa: F401
import thuong_tri_tong_hop      # noqa: F401


def kham_benh_va_xuat_file(duong_dan_du_an, bao_trang_thai=lambda msg: None):
    """Chạy trọn một lượt khám, gom mọi log vào MỘT file duy nhất.

    Trả về đường dẫn file báo cáo đã lưu.
    """
    cfg.chon_benh_nhan(duong_dan_du_an)
    ten_du_an = os.path.basename(os.path.normpath(duong_dan_du_an))

    dem = io.StringIO()

    cac_buoc = [
        ("Đang tiêu hóa dự án (Tỳ Tạng)...", "YEU_CAU_NHAI", duong_dan_du_an),
        ("Đang nhìn sắc diện (Vọng Chẩn)...", "YEU_CAU_KHAM_BENH", duong_dan_du_an),
        ("Đang bắt mạch + tổng hợp (Thiết Chẩn + Thượng Trí)...", "YEU_CAU_BAT_MACH", duong_dan_du_an),
        ("Đang soi gốc quá tải (Can Tạng)...", "YEU_CAU_KHAM_GOC", duong_dan_du_an),
    ]
    for thong_bao, su_kien, du_lieu in cac_buoc:
        bao_trang_thai(thong_bao)
        with contextlib.redirect_stdout(dem):
            xuong_song_trung_uong.phat_khi(su_kien, du_lieu)

    bao_trang_thai("Đang xuất Chân Kinh...")
    with contextlib.redirect_stdout(dem):
        xuong_song_trung_uong.phat_khi("YEU_CAU_CHAN_KINH", {"loc": None})

    duong_dan_bao_cao = os.path.join(
        duong_dan_du_an, f"OKA_BAO_CAO_{ten_du_an}.md"
    )
    noi_dung = (
        f"# Báo cáo khám bệnh OKA — {ten_du_an}\n\n"
        f"Dán TOÀN BỘ file này cho AI trước khi nhờ nó sửa code trong dự án -\n"
        f"AI sẽ biết trước cấu trúc thật, chỗ nào rủi ro, chỗ nào là rác,\n"
        f"thay vì phải đọc lại từng file một.\n\n"
        "```\n" + dem.getvalue() + "\n```\n"
    )
    with open(duong_dan_bao_cao, "w", encoding="utf-8") as f:
        f.write(noi_dung)

    bao_trang_thai(f"✅ Xong! Đã lưu: {duong_dan_bao_cao}")
    return duong_dan_bao_cao


class CuaSoOKA(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌿 OKA - Thầy Thuốc Cho Code")
        self.geometry("540x240")
        self.resizable(False, False)

        self.hang_doi = queue.Queue()
        self.dang_chay = False

        tk.Label(self, text="🌿 OKA_System", font=("Segoe UI", 18, "bold")).pack(pady=(18, 4))
        tk.Label(
            self, text="Chọn thư mục dự án cần khám bệnh",
            font=("Segoe UI", 11),
        ).pack(pady=(0, 12))

        self.nhan_duong_dan = tk.Label(
            self, text="(chưa chọn thư mục nào)",
            font=("Segoe UI", 9), fg="#555555", wraplength=500,
        )
        self.nhan_duong_dan.pack(pady=(0, 10))

        self.nut_chon = tk.Button(
            self, text="📂 Chọn thư mục dự án...", font=("Segoe UI", 11),
            command=self.chon_thu_muc, width=32, height=1,
        )
        self.nut_chon.pack(pady=4)

        self.nhan_trang_thai = tk.Label(
            self, text="", font=("Segoe UI", 9), fg="#0a7a2f", wraplength=500,
        )
        self.nhan_trang_thai.pack(pady=(14, 0))

        self.duong_dan_bao_cao_vua_xong = None
        self.nut_mo_thu_muc = tk.Button(
            self, text="📁 Mở thư mục chứa báo cáo", font=("Segoe UI", 10),
            command=self.mo_thu_muc_bao_cao, state="disabled",
        )
        self.nut_mo_thu_muc.pack(pady=(8, 0))

    def chon_thu_muc(self):
        if self.dang_chay:
            return
        duong_dan = filedialog.askdirectory(title="Chọn thư mục dự án cần khám")
        if not duong_dan:
            return

        self.nhan_duong_dan.config(text=duong_dan)
        self.nut_chon.config(state="disabled")
        self.nut_mo_thu_muc.config(state="disabled")
        self.dang_chay = True
        self.nhan_trang_thai.config(text="Đang bắt đầu...")

        # Chạy nền - tkinter không thread-safe nếu cập nhật UI trực tiếp từ
        # thread khác, nên luồng nền chỉ đẩy chữ vào hàng đợi, UI tự đọc.
        luong = threading.Thread(
            target=self._chay_ngam, args=(duong_dan,), daemon=True
        )
        luong.start()
        self.after(100, self._doc_hang_doi)

    def _chay_ngam(self, duong_dan):
        try:
            duong_dan_bao_cao = kham_benh_va_xuat_file(
                duong_dan, bao_trang_thai=self.hang_doi.put
            )
            self.hang_doi.put(("XONG", duong_dan_bao_cao))
        except Exception as e:
            self.hang_doi.put(("LOI", str(e)))

    def _doc_hang_doi(self):
        try:
            while True:
                tin = self.hang_doi.get_nowait()
                if isinstance(tin, tuple) and tin[0] == "XONG":
                    self._hoan_tat(tin[1])
                    return
                if isinstance(tin, tuple) and tin[0] == "LOI":
                    self._loi(tin[1])
                    return
                self.nhan_trang_thai.config(text=tin)
        except queue.Empty:
            pass
        if self.dang_chay:
            self.after(100, self._doc_hang_doi)

    def _hoan_tat(self, duong_dan_bao_cao):
        self.dang_chay = False
        self.duong_dan_bao_cao_vua_xong = duong_dan_bao_cao
        self.nut_chon.config(state="normal")
        self.nut_mo_thu_muc.config(state="normal")
        self.nhan_trang_thai.config(text=f"✅ Xong! Đã lưu: {duong_dan_bao_cao}")
        messagebox.showinfo(
            "Xong!",
            f"Đã khám xong.\n\nBáo cáo lưu tại:\n{duong_dan_bao_cao}\n\n"
            f"Dán toàn bộ nội dung file này cho AI trước khi nhờ sửa code.",
        )

    def _loi(self, thong_diep_loi):
        self.dang_chay = False
        self.nut_chon.config(state="normal")
        self.nhan_trang_thai.config(text="❌ Có lỗi xảy ra.")
        messagebox.showerror("Lỗi", f"Khám bệnh thất bại:\n{thong_diep_loi}")

    def mo_thu_muc_bao_cao(self):
        if self.duong_dan_bao_cao_vua_xong:
            os.startfile(os.path.dirname(self.duong_dan_bao_cao_vua_xong))


if __name__ == "__main__":
    app = CuaSoOKA()
    app.mainloop()
