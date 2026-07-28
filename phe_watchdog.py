# phe_watchdog.py
# PHẾ TẠNG - Phế chủ hô hấp, cai quản phần ranh giới (File System Watcher)
#
# Sửa so với bản đầu:
#   1. Thiếu thư viện 'watchdog' thì Phế KHÔNG chết - nó chuyển sang
#      "thở chậm" (tự quét theo chu kỳ). Tool chép sang máy mới vẫn chạy.
#   2. Nhịp thở giữ riêng cho từng file. Trước đây dùng chung một mốc thời gian,
#      nên lưu 2 file cách nhau dưới 2 giây là file thứ hai bị nuốt mất.

import os
import time
import threading

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    CO_WATCHDOG = True
except ImportError:
    CO_WATCHDOG = False
    FileSystemEventHandler = object   # để định nghĩa class bên dưới không lỗi

NHIP_TOI_THIEU = 1.5   # giây, cho mỗi file


class _NhipTho:
    """Phần chung: quyết định một file có đáng đánh thức cả cơ thể không"""

    def __init__(self):
        self._nhip = {}          # đường dẫn -> lần thở gần nhất
        self._khoa = threading.Lock()

    def dang_hoi_thuoc(self, duong_dan):
        if not duong_dan or not str(duong_dan).endswith('.py'):
            return False
        if cfg.la_ta_khi(duong_dan):
            return False

        bay_gio = time.time()
        with self._khoa:
            if bay_gio - self._nhip.get(duong_dan, 0) < NHIP_TOI_THIEU:
                return False
            self._nhip[duong_dan] = bay_gio
        return True

    def hit_vao(self, duong_dan):
        if not self.dang_hoi_thuoc(duong_dan):
            return
        print(f"🫁 [PHẾ]: (Hít vào) {os.path.basename(duong_dan)}")
        xuong_song_trung_uong.phat_khi("FILE_DA_LUU", duong_dan)


class PheTang(FileSystemEventHandler):
    """Chế độ thở thật - cần thư viện watchdog"""

    def __init__(self, nhip_tho):
        if CO_WATCHDOG:
            super().__init__()
        self.nhip_tho = nhip_tho

    def on_modified(self, event):
        if not getattr(event, 'is_directory', False):
            self.nhip_tho.hit_vao(event.src_path)

    def on_created(self, event):
        self.on_modified(event)


class PheThoCham:
    """Chế độ thở chậm - không cần thư viện nào, tự quét theo chu kỳ"""

    def __init__(self, duong_dan, nhip_tho, chu_ky=3.0):
        self.duong_dan = duong_dan
        self.nhip_tho = nhip_tho
        self.chu_ky = chu_ky
        self._dung = threading.Event()
        self._dau_vet = {}
        self._luong = threading.Thread(target=self._vong_tho, daemon=True)

    def start(self):
        self._quet(lan_dau=True)   # lần đầu chỉ ghi nhớ, không báo động
        self._luong.start()

    def stop(self):
        self._dung.set()

    def _quet(self, lan_dau=False):
        for root, dirs, files in os.walk(self.duong_dan):
            dirs[:] = [d for d in dirs if d not in cfg.TA_KHI_DIRS]
            for ten in files:
                if not ten.endswith('.py'):
                    continue
                dd = os.path.join(root, ten)
                try:
                    moc = os.path.getmtime(dd)
                except OSError:
                    continue
                if self._dau_vet.get(dd) != moc:
                    self._dau_vet[dd] = moc
                    if not lan_dau:
                        self.nhip_tho.hit_vao(dd)

    def _vong_tho(self):
        while not self._dung.wait(self.chu_ky):
            try:
                self._quet()
            except Exception as e:
                print(f"⚠️ [PHẾ]: Nghẹt thở khi quét → {e}")


def khoi_dong_nhip_tho(duong_dan=None):
    """Mở Phế trên một bệnh nhân. Trả về đối tượng có .stop()"""
    duong_dan = duong_dan or cfg.benh_nhan_hien_tai()
    if not os.path.isdir(duong_dan):
        print(f"❌ [PHẾ]: Không tìm thấy bệnh nhân tại '{duong_dan}'.")
        return None

    nhip_tho = _NhipTho()

    if CO_WATCHDOG:
        observer = Observer()
        observer.schedule(PheTang(nhip_tho), duong_dan, recursive=True)
        observer.start()
        print(f"🌿 [PHẾ]: Đã mở, đang hô hấp tại {duong_dan}")
        return observer

    phe = PheThoCham(duong_dan, nhip_tho)
    phe.start()
    print(f"🌿 [PHẾ]: Thiếu thư viện 'watchdog' → chuyển sang THỞ CHẬM (quét mỗi 3 giây).")
    print(f"   Muốn thở sâu, hãy cài: pip install watchdog")
    return phe
