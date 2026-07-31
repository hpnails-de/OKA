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
import re
import sys
import io
import contextlib
import threading
import queue
import tkinter as tk
from tkinter import filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import oka_config as cfg
from ngon_ngu import t
import ngon_ngu
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
        (t("b_nhai"), "YEU_CAU_NHAI", duong_dan_du_an),
        (t("b_kham"), "YEU_CAU_KHAM_BENH", duong_dan_du_an),
        (t("b_mach"), "YEU_CAU_BAT_MACH", duong_dan_du_an),
        (t("b_goc"), "YEU_CAU_KHAM_GOC", duong_dan_du_an),
        (t("b_bao_mat"), "YEU_CAU_SOI_BAO_MAT", duong_dan_du_an),
        (t("b_chat_luong"), "YEU_CAU_SOI_CHAT_LUONG", duong_dan_du_an),
        (t("b_can_bang"), "YEU_CAU_SOI_CAN_BANG", duong_dan_du_an),
    ]
    for thong_bao, su_kien, du_lieu in cac_buoc:
        bao_trang_thai(thong_bao)
        with contextlib.redirect_stdout(dem):
            xuong_song_trung_uong.phat_khi(su_kien, du_lieu)

    bao_trang_thai(t("b_chan_kinh"))
    with contextlib.redirect_stdout(dem):
        xuong_song_trung_uong.phat_khi("YEU_CAU_CHAN_KINH", {"loc": None})

    # Vẽ Mandala - hỏng ở đây thì báo cáo chữ vẫn phải ra bình thường,
    # nên bọc riêng, không để một hình vẽ làm chết cả lượt khám.
    bao_trang_thai(t("b_mandala"))
    duong_dan_svg = None
    try:
        from thiet_chan_pulse import thiet_chan_trung_uong
        import cum_chuc_nang
        import mandala_svg
        with contextlib.redirect_stdout(dem):
            mach = thiet_chan_trung_uong._tinh_mach(duong_dan_du_an)
        if mach:
            cac_cum = cum_chuc_nang.gom_cum(mach)
            hang_xom = cum_chuc_nang.dung_do_thi_file(mach)
            duong_dan_svg = mandala_svg.ve_mandala(
                cac_cum, hang_xom, ten_du_an,
                os.path.join(duong_dan_du_an, f"OKA_MANDALA_{ten_du_an}.svg"),
            )
    except Exception as e:
        dem.write(f"\n⚠️ Không vẽ được Mandala: {e}\n")

    # Ký ức xoắn ốc - nén TOÀN BỘ lịch sử hội thoại với AI về dự án này.
    # Khác hẳn Chân Kinh (nói về CODE): cái này nói về QUÁ TRÌNH làm việc -
    # đã bàn gì, quyết định gì, sửa gì. Dán cho phiên AI mới là nó nhớ lại
    # được mạch việc từ đầu, thay vì bắt đầu từ con số không.
    bao_trang_thai(t("b_ky_uc"))
    duong_dan_ky_uc = None
    try:
        import xoan_oc_ky_uc
        van_ban_ky_uc, tk_ky_uc = xoan_oc_ky_uc.dung_tu_du_an(duong_dan_du_an)
        if van_ban_ky_uc:
            duong_dan_ky_uc = os.path.join(
                duong_dan_du_an, f"OKA_KY_UC_{ten_du_an}.md"
            )
            with open(duong_dan_ky_uc, "w", encoding="utf-8") as f:
                f.write(
                    f'# {t("ku_tieu_de")} — {ten_du_an}\n\n'
                    f'{t("ku_huong_dan")}\n\n'
                    f'- {tk_ky_uc["so_phien"]} {t("ku_phien")}, '
                    f'{tk_ky_uc["so_su_kien"]:,} {t("xo_luot")}\n'
                    f'- {t("ku_nen_tu")} {tk_ky_uc["ky_tu_goc"]:,} → '
                    f'{tk_ky_uc["ky_tu_ky_uc"]:,} {t("xo_ky_tu")}\n\n'
                    + van_ban_ky_uc
                )
            dem.write(
                f"\n🌀 KÝ ỨC XOẮN ỐC: {tk_ky_uc['so_su_kien']:,} lượt hội thoại "
                f"({tk_ky_uc['so_phien']} phiên) nén còn {tk_ky_uc['so_tang']} tầng, "
                f"{tk_ky_uc['ky_tu_goc']:,} → {tk_ky_uc['ky_tu_ky_uc']:,} ký tự.\n"
            )
        else:
            dem.write(
                "\nℹ️ Chưa có bản ghi hội thoại nào cho dự án này "
                "(chỉ có khi bạn dùng Claude Code trong đúng thư mục đó).\n"
            )
    except Exception as e:
        dem.write(f"\n⚠️ Không dựng được ký ức xoắn ốc: {e}\n")

    duong_dan_bao_cao = os.path.join(
        duong_dan_du_an, f"OKA_BAO_CAO_{ten_du_an}.md"
    )
    ghi_chu_svg = (
        f'\n{t("bc_so_do")} `{os.path.basename(duong_dan_svg)}` '
        f'{t("bc_mo_bang")}\n' if duong_dan_svg else ""
    )
    noi_dung = (
        f'# {t("bc_tieu_de")} — {ten_du_an}\n\n'
        f'{t("bc_huong_dan")}\n'
        f"{ghi_chu_svg}\n"
        f'{t("bc_do_tin_cay")}\n\n'
        "```\n" + dem.getvalue() + "\n```\n"
    )
    with open(duong_dan_bao_cao, "w", encoding="utf-8") as f:
        f.write(noi_dung)

    bao_trang_thai(f'{t("da_luu")} {duong_dan_bao_cao}')
    return duong_dan_bao_cao


def rut_so_lieu(duong_dan_bao_cao):
    """Moi ra vài con số đáng chú ý từ báo cáo, để hiện ngay trên giao diện
    thay vì bắt người dùng mở file mới biết kết quả."""
    so_lieu = {"so_file": "?", "tiet_kiem": "?", "token_goc": "?",
               "token_moi": "?", "so_nhan_dinh": 0, "canh_bao": []}
    try:
        with open(duong_dan_bao_cao, "r", encoding="utf-8") as f:
            noi_dung = f.read()
    except OSError:
        return so_lieu

    m = re.search(r"nhai xong (\d+) file", noi_dung)
    if m:
        so_lieu["so_file"] = m.group(1)

    m = re.search(
        r"Ném cả source: ~([\d,]+) token\s*\|\s*Chân Kinh: ~([\d,]+) token\s*\|\s*Tiết kiệm ~([\d.]+)%",
        noi_dung,
    )
    if m:
        so_lieu["token_goc"] = m.group(1)
        so_lieu["token_moi"] = m.group(2)
        so_lieu["tiet_kiem"] = m.group(3) + "%"

    m = re.search(r"THƯỢNG TRÍ: Đã tổng hợp (\d+) nhận định", noi_dung)
    if m:
        so_lieu["so_nhan_dinh"] = int(m.group(1))

    # Lấy các dòng nhận định của Thượng Trí để hiện tóm tắt
    khoi = re.search(
        r"TỔNG HỢP NHẬN ĐỊNH.*?\n(.*?)\n-{20,}", noi_dung, re.DOTALL
    )
    if khoi:
        for dong in khoi.group(1).splitlines():
            dong = dong.strip()
            if dong and not dong.startswith("🧠"):
                so_lieu["canh_bao"].append(dong)

    return so_lieu


# --- Bảng màu: tối, dịu mắt, tông xanh lá của "thảo dược" ---
NEN = "#12151a"          # nền chính
NEN_THE = "#1b2027"      # nền thẻ
VIEN = "#2a323d"         # viền thẻ
CHU = "#e6e9ef"          # chữ chính
CHU_MO = "#8b95a5"       # chữ phụ
XANH = "#4ade80"         # nhấn (xanh lá)
XANH_DAM = "#22c55e"
VANG = "#fbbf24"         # cảnh báo
DO = "#f87171"           # lỗi


class CuaSoOKA(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(t("tieu_de_app"))
        self.geometry("720x560")
        self.minsize(660, 520)
        self.configure(bg=NEN)

        self.hang_doi = queue.Queue()
        self.dang_chay = False
        self.duong_dan_bao_cao_vua_xong = None
        self.duong_dan_ky_uc = None
        self.duong_dan_da_chon = None

        self._dung_thanh_tieu_de()
        self._dung_khu_chon()
        self._dung_khu_ket_qua()
        self._dung_chan_trang()

    # ---------------- Dựng giao diện ----------------

    def _the(self, cha, **kw):
        """Một 'thẻ' - khối nền sáng hơn, có viền, cho gọn mắt."""
        return tk.Frame(cha, bg=NEN_THE, highlightbackground=VIEN,
                        highlightthickness=1, **kw)

    def _dung_thanh_tieu_de(self):
        dau = tk.Frame(self, bg=NEN)
        dau.pack(fill="x", padx=24, pady=(22, 6))
        tk.Label(dau, text="🌿  OKA", font=("Segoe UI", 22, "bold"),
                 bg=NEN, fg=XANH).pack(side="left")
        tk.Label(dau, text=t("phu_de"), font=("Segoe UI", 11),
                 bg=NEN, fg=CHU_MO).pack(side="left", padx=(12, 0), pady=(10, 0))

        # Nút chuyển ngôn ngữ. Đổi xong phải dựng lại toàn bộ cửa sổ vì
        # tkinter không có cơ chế "văn bản động" - chữ đã đặt vào widget
        # thì nằm cứng ở đó.
        khung_ngon_ngu = tk.Frame(dau, bg=NEN)
        khung_ngon_ngu.pack(side="right", pady=(8, 0))
        self.nut_ngon_ngu = {}
        for ma, nhan in (("vi", "VI"), ("en", "EN")):
            dang_chon = (ngon_ngu.lay() == ma)
            nut = tk.Button(
                khung_ngon_ngu, text=nhan, font=("Segoe UI", 9, "bold"),
                bg=XANH_DAM if dang_chon else NEN_THE,
                fg="#0b1220" if dang_chon else CHU_MO,
                activebackground=XANH, relief="flat", cursor="hand2",
                padx=11, pady=4, borderwidth=0,
                command=lambda m=ma: self.doi_ngon_ngu(m),
            )
            nut.pack(side="left", padx=(4, 0))
            self.nut_ngon_ngu[ma] = nut

        tk.Label(
            self,
            text=t("mo_ta"),
            font=("Segoe UI", 9), bg=NEN, fg=CHU_MO,
            wraplength=660, justify="left",
        ).pack(fill="x", padx=24, pady=(0, 14))

    def _dung_khu_chon(self):
        the = self._the(self)
        the.pack(fill="x", padx=24)

        trong = tk.Frame(the, bg=NEN_THE)
        trong.pack(fill="x", padx=16, pady=14)

        self.nhan_duong_dan = tk.Label(
            trong, text=t("chua_chon"),
            font=("Segoe UI", 10), bg=NEN_THE, fg=CHU_MO,
            anchor="w", wraplength=420, justify="left",
        )
        self.nhan_duong_dan.pack(side="left", fill="x", expand=True)

        self.nut_chon = tk.Button(
            trong, text=t("nut_chon"), font=("Segoe UI", 10, "bold"),
            bg=XANH_DAM, fg="#0b1220", activebackground=XANH,
            activeforeground="#0b1220", relief="flat", cursor="hand2",
            padx=18, pady=8, command=self.chon_thu_muc, borderwidth=0,
        )
        self.nut_chon.pack(side="right")

        # Thanh tiến trình tự vẽ (Canvas) - ttk.Progressbar bám theme hệ điều
        # hành nên trên nền tối thường lệch màu, tự vẽ thì chắc ăn hơn.
        self.thanh_tien_trinh = tk.Canvas(
            the, height=4, bg=VIEN, highlightthickness=0
        )
        self.thanh_tien_trinh.pack(fill="x")
        self._ve_tien_trinh(0)

        self.nhan_trang_thai = tk.Label(
            the, text="", font=("Segoe UI", 9), bg=NEN_THE, fg=CHU_MO,
            anchor="w", wraplength=640, justify="left",
        )
        self.nhan_trang_thai.pack(fill="x", padx=16, pady=(8, 12))

    def _dung_khu_ket_qua(self):
        self.khu_ket_qua = self._the(self)
        self.khu_ket_qua.pack(fill="both", expand=True, padx=24, pady=14)

        # Hàng các ô số liệu
        self.hang_so = tk.Frame(self.khu_ket_qua, bg=NEN_THE)
        self.hang_so.pack(fill="x", padx=16, pady=(14, 6))
        self.o_so = {}
        for khoa in ("so_file", "token_goc", "token_moi", "tiet_kiem"):
            o = tk.Frame(self.hang_so, bg=NEN_THE)
            o.pack(side="left", expand=True, fill="x")
            gia_tri = tk.Label(o, text="—", font=("Segoe UI", 17, "bold"),
                               bg=NEN_THE, fg=CHU)
            gia_tri.pack()
            tk.Label(o, text=t("o_" + khoa), font=("Segoe UI", 8), bg=NEN_THE,
                     fg=CHU_MO).pack()
            self.o_so[khoa] = gia_tri

        tk.Frame(self.khu_ket_qua, bg=VIEN, height=1).pack(
            fill="x", padx=16, pady=(10, 0))

        self.nhan_canh_bao = tk.Label(
            self.khu_ket_qua, text=t("cho_ket_qua"),
            font=("Segoe UI", 9, "bold"), bg=NEN_THE, fg=CHU_MO, anchor="w",
        )
        self.nhan_canh_bao.pack(fill="x", padx=16, pady=(10, 4))

        khung_van_ban = tk.Frame(self.khu_ket_qua, bg=NEN_THE)
        khung_van_ban.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        thanh_cuon = tk.Scrollbar(khung_van_ban)
        thanh_cuon.pack(side="right", fill="y")
        self.o_canh_bao = tk.Text(
            khung_van_ban, height=7, font=("Consolas", 9), bg=NEN, fg=CHU,
            relief="flat", wrap="word", yscrollcommand=thanh_cuon.set,
            insertbackground=CHU, padx=10, pady=8,
        )
        self.o_canh_bao.pack(side="left", fill="both", expand=True)
        thanh_cuon.config(command=self.o_canh_bao.yview)
        self.o_canh_bao.config(state="disabled")

    def _dung_chan_trang(self):
        chan = tk.Frame(self, bg=NEN)
        chan.pack(fill="x", padx=24, pady=(0, 20))

        self.nut_mo_file = tk.Button(
            chan, text=t("nut_mo_file"), font=("Segoe UI", 10),
            bg=NEN_THE, fg=CHU_MO, activebackground=VIEN, relief="flat",
            cursor="hand2", padx=14, pady=7, borderwidth=0,
            state="disabled", command=self.mo_file_bao_cao,
        )
        self.nut_mo_file.pack(side="left")

        self.nut_mo_thu_muc = tk.Button(
            chan, text=t("nut_mo_thu_muc"), font=("Segoe UI", 10),
            bg=NEN_THE, fg=CHU_MO, activebackground=VIEN, relief="flat",
            cursor="hand2", padx=14, pady=7, borderwidth=0,
            state="disabled", command=self.mo_thu_muc_bao_cao,
        )
        self.nut_mo_thu_muc.pack(side="left", padx=(10, 0))

        # Chỉ bật khi dự án thật sự có bản ghi hội thoại
        self.nut_mo_ky_uc = tk.Button(
            chan, text=t("nut_mo_ky_uc"), font=("Segoe UI", 10),
            bg=NEN_THE, fg=CHU_MO, activebackground=VIEN, relief="flat",
            cursor="hand2", padx=14, pady=7, borderwidth=0,
            state="disabled", command=self.mo_file_ky_uc,
        )
        self.nut_mo_ky_uc.pack(side="left", padx=(10, 0))

        self.nut_chep = tk.Button(
            chan, text=t("nut_chep"),
            font=("Segoe UI", 10, "bold"),
            bg=NEN_THE, fg=XANH, activebackground=VIEN, relief="flat",
            cursor="hand2", padx=14, pady=7, borderwidth=0,
            state="disabled", command=self.chep_bao_cao,
        )
        self.nut_chep.pack(side="right")

    def _ve_tien_trinh(self, ty_le):
        """ty_le: 0.0 → 1.0"""
        self.thanh_tien_trinh.delete("all")
        self.update_idletasks()
        rong = self.thanh_tien_trinh.winfo_width() or 660
        if ty_le > 0:
            self.thanh_tien_trinh.create_rectangle(
                0, 0, rong * ty_le, 4, fill=XANH, outline="")

    def doi_ngon_ngu(self, ma):
        """Đổi ngôn ngữ rồi dựng lại cửa sổ.

        Không đổi giữa chừng khi đang khám - dựng lại widget lúc luồng nền
        còn đang bắn tín hiệu vào chúng là sập chương trình.
        """
        if self.dang_chay or ma == ngon_ngu.lay():
            return
        ngon_ngu.dat(ma)
        for w in self.winfo_children():
            w.destroy()
        self.title(t("tieu_de_app"))
        self._dung_thanh_tieu_de()
        self._dung_khu_chon()
        self._dung_khu_ket_qua()
        self._dung_chan_trang()

        # Giữ lại kết quả đã có, hiện lại bằng ngôn ngữ mới
        if self.duong_dan_bao_cao_vua_xong:
            self._hien_ket_qua(self.duong_dan_bao_cao_vua_xong)

    # ---------------- Luồng chạy ----------------

    def chon_thu_muc(self):
        if self.dang_chay:
            return
        duong_dan = filedialog.askdirectory(title=t("hop_thoai_chon"))
        if not duong_dan:
            return

        self.duong_dan_da_chon = duong_dan
        self.nhan_duong_dan.config(text=duong_dan, fg=CHU)
        self.nut_chon.config(state="disabled", text=t("nut_dang_kham"))
        for nut in (self.nut_mo_file, self.nut_mo_thu_muc, self.nut_chep,
                    self.nut_mo_ky_uc):
            nut.config(state="disabled")
        self.dang_chay = True
        self._buoc_hien_tai = 0
        self.nhan_trang_thai.config(text=t("bat_dau"), fg=CHU_MO)

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
                self._buoc_hien_tai += 1
                self._ve_tien_trinh(min(self._buoc_hien_tai / 5.0, 0.95))
                self.nhan_trang_thai.config(text=tin, fg=CHU_MO)
        except queue.Empty:
            pass
        if self.dang_chay:
            self.after(100, self._doc_hang_doi)

    def _hien_ket_qua(self, duong_dan_bao_cao):
        """Đổ số liệu lên giao diện. Tách riêng để nút đổi ngôn ngữ dùng lại
        được mà không phải khám lại từ đầu."""
        self.nhan_trang_thai.config(
            text=f'{t("da_luu")} {duong_dan_bao_cao}', fg=XANH)

        so_lieu = rut_so_lieu(duong_dan_bao_cao)
        for khoa, o in self.o_so.items():
            o.config(text=so_lieu.get(khoa, "—"))
        self.o_so["tiet_kiem"].config(fg=XANH)

        canh_bao = so_lieu["canh_bao"]
        if canh_bao:
            self.nhan_canh_bao.config(
                text=f'⚠  {len(canh_bao)} {t("diem_chu_y")}', fg=VANG)
        else:
            self.nhan_canh_bao.config(text=t("khong_rui_ro"), fg=XANH)

        self.o_canh_bao.config(state="normal")
        self.o_canh_bao.delete("1.0", "end")
        self.o_canh_bao.insert(
            "1.0", "\n\n".join(canh_bao) if canh_bao else t("khong_to_hop")
        )
        self.o_canh_bao.config(state="disabled")

        for nut in (self.nut_mo_file, self.nut_mo_thu_muc, self.nut_chep):
            nut.config(state="normal")

        # Nút ký ức chỉ bật khi dự án có bản ghi hội thoại thật
        thu_muc = os.path.dirname(duong_dan_bao_cao)
        ten = os.path.basename(os.path.normpath(thu_muc))
        ung_vien = os.path.join(thu_muc, f"OKA_KY_UC_{ten}.md")
        if os.path.isfile(ung_vien):
            self.duong_dan_ky_uc = ung_vien
            self.nut_mo_ky_uc.config(state="normal")
        self._ve_tien_trinh(1.0)

    def _hoan_tat(self, duong_dan_bao_cao):
        self.dang_chay = False
        self.duong_dan_bao_cao_vua_xong = duong_dan_bao_cao
        self.nut_chon.config(state="normal", text=t("nut_chon"))
        self._hien_ket_qua(duong_dan_bao_cao)

    def _loi(self, thong_diep_loi):
        self.dang_chay = False
        self.nut_chon.config(state="normal", text=t("nut_chon"))
        self._ve_tien_trinh(0)
        self.nhan_trang_thai.config(text=t("co_loi"), fg=DO)
        messagebox.showerror(t("loi"), f'{t("loi_kham")}\n{thong_diep_loi}')

    # ---------------- Nút chân trang ----------------

    def mo_file_bao_cao(self):
        if self.duong_dan_bao_cao_vua_xong:
            os.startfile(self.duong_dan_bao_cao_vua_xong)

    def mo_thu_muc_bao_cao(self):
        if self.duong_dan_bao_cao_vua_xong:
            os.startfile(os.path.dirname(self.duong_dan_bao_cao_vua_xong))

    def mo_file_ky_uc(self):
        if self.duong_dan_ky_uc and os.path.isfile(self.duong_dan_ky_uc):
            os.startfile(self.duong_dan_ky_uc)

    def chep_bao_cao(self):
        if not self.duong_dan_bao_cao_vua_xong:
            return
        try:
            with open(self.duong_dan_bao_cao_vua_xong, "r", encoding="utf-8") as f:
                noi_dung = f.read()
        except OSError as e:
            messagebox.showerror(t("loi"), f'{t("loi_doc_file")}\n{e}')
            return
        self.clipboard_clear()
        self.clipboard_append(noi_dung)
        self.update()   # giữ clipboard sống sau khi app đóng
        self.nut_chep.config(text=t("da_chep"))
        self.after(2600, lambda: self.nut_chep.config(
            text=t("nut_chep")))


if __name__ == "__main__":
    app = CuaSoOKA()
    app.mainloop()
