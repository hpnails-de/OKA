# vong_chan_diagnostic.py
# VỌNG CHẨN (望診) - Phép thứ nhất trong Tứ Chẩn: NHÌN sắc diện bên ngoài
#
# Vọng Chẩn chỉ thấy được da lông: file dài bao nhiêu, tên gọi ra sao,
# có kẻ lạ nào lẫn vào không. Muốn biết bên trong khí huyết chạy thế nào
# thì phải nhờ tới Thiết Chẩn (bắt mạch) - xem thiet_chan_pulse.py

import os
import ast

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong


class VongChan:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_KHAM_BENH", self.bat_dau_kham)

        # Dấu hiệu của "Nguyên Khí" - code do chính chủ đúc ra
        self.NGUYEN_KHI_KEYWORDS = [
            'tab_', 'suno_', 'oka_', 'gui_', 'main', 'engine', 'bot', 'master',
            'tang_', 'mach_', 'chan_', 'app', 'core',
        ]
        # Tên thư mục package gần như phổ quát trong mọi dự án Python (không
        # phải suy đoán riêng cho dự án nào) - kể cả khi thiếu __init__.py
        # (namespace package hoặc code cũ), đây vẫn gần như chắc chắn là code
        # thật, không phải rác/scratch.
        self.THU_MUC_PHO_QUAT = {
            'utils', 'util', 'lib', 'core', 'common', 'helpers', 'helper',
            'services', 'models', 'src',
        }

    def _dem_dong(self, duong_dan):
        try:
            with open(duong_dan, 'r', encoding='utf-8', errors='replace') as f:
                return sum(1 for _ in f)
        except OSError:
            return 0

    def _phan_tich(self, benh_nhan):
        """Tính thuần túy, KHÔNG in gì - để Thượng Trí gọi lại mà không bị
        Vọng Chẩn in report một lần nữa (bat_dau_kham() vẫn in như cũ,
        gọi hàm này bên trong).

        Trả về (nguyen_khi_files, di_vat_files) đều là DỮ LIỆU có cấu trúc:
          nguyen_khi_files: [(relpath, dòng, số_hàm), ...]
          di_vat_files:     [(relpath, dòng, lý_do), ...]  lý_do: 'la'|'hong'
        """
        nguyen_khi_files = []   # code chính chủ
        di_vat_files = []       # code lạ hoặc hỏng

        for root, dirs, files in os.walk(benh_nhan):
            dirs[:] = [d for d in dirs if d not in cfg.TA_KHI_DIRS]

            for ten in files:
                if not ten.endswith(".py"):
                    continue

                full_path = os.path.join(root, ten)
                loc = self._dem_dong(full_path)
                rel = os.path.relpath(full_path, benh_nhan)
                la_goc = (os.path.normpath(root) == os.path.normpath(benh_nhan))
                co_dau_hieu = any(kw in ten.lower() for kw in self.NGUYEN_KHI_KEYWORDS)
                # Tín hiệu đáng tin hơn so khớp tên: thư mục có __init__.py là
                # package Python thật - việc ĐẶT TÊN không đoán ra được nhưng
                # cấu trúc package thì không thể giả. Thiếu tín hiệu này khiến
                # cả utils/*.py và ui/tabs/*.py (code thật, không phải dị vật)
                # từng bị chấm nhầm thành dị vật chỉ vì tên file không khớp
                # từ khóa may rủi (phát hiện qua chính Thượng Trí soi lại).
                la_package = '__init__.py' in files
                ten_thu_muc = os.path.basename(os.path.normpath(root)).lower()
                la_thu_muc_pho_quat = ten_thu_muc in self.THU_MUC_PHO_QUAT

                if la_goc or co_dau_hieu or la_package or la_thu_muc_pho_quat:
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            cay = ast.parse(f.read())
                        so_ham = sum(
                            1 for n in ast.walk(cay)
                            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                        )
                        nguyen_khi_files.append((rel, loc, so_ham))
                    except (OSError, SyntaxError, ValueError):
                        di_vat_files.append((rel, loc, 'hong'))
                else:
                    di_vat_files.append((rel, loc, 'la'))

        return nguyen_khi_files, di_vat_files

    def bat_dau_kham(self, duong_dan_du_an=None):
        benh_nhan = duong_dan_du_an or cfg.benh_nhan_hien_tai()
        if not os.path.isdir(benh_nhan):
            print(f"❌ [VỌNG CHẨN]: Không tìm thấy bệnh nhân tại '{benh_nhan}'")
            return None

        print("\n" + "✨ " * 5)
        print(f"👁️ [VỌNG CHẨN]: GẠN ĐỤC KHƠI TRONG TẠI {benh_nhan}")
        print("✨ " * 5)

        nguyen_khi_files, di_vat_files = self._phan_tich(benh_nhan)

        # --- BÁO CÁO ---
        print("\n💎 [NGUYÊN KHÍ - CODE CHÍNH CHỦ]:")
        if not nguyen_khi_files:
            print("   (Trống rỗng - kiểm tra lại đường dẫn bệnh nhân!)")
        for f, l, h in sorted(nguyen_khi_files, key=lambda x: -x[1]):
            status = "🟢" if l <= cfg.NGUONG_PHINH_TO else "🔴"
            print(f"{status} {f:<42} | {l:>5} dòng | {h:>3} hàm")

        if di_vat_files:
            print(f"\n👽 [DỊ VẬT - {len(di_vat_files)} kẻ lạ]:")
            for rel, loc, ly_do in di_vat_files[:20]:
                if ly_do == 'hong':
                    print(f"   ⚠️ {rel} (cú pháp hỏng - Đởm sẽ chặn)")
                else:
                    print(f"   ❓ {rel} ({loc} dòng) - không rõ có thuộc dự án không")
            if len(di_vat_files) > 20:
                print(f"   ... và {len(di_vat_files) - 20} dị vật khác.")

        qua_kho = [f for f, l, _ in nguyen_khi_files if l > cfg.NGUONG_PHINH_TO]
        if qua_kho:
            print(f"\n🔴 CẢNH BÁO PHÌNH TO: {len(qua_kho)} file vượt {cfg.NGUONG_PHINH_TO} dòng.")
            print("   Đây là lúc AI hay bắt đầu 'sửa chỗ này hỏng chỗ kia'.")
            print("   → Gõ 'mach' để Thiết Chẩn bắt mạch xem chỗ nào là huyệt hiểm.")

        print(f"\n📊 TỔNG KẾT: {len(nguyen_khi_files)} file Nguyên Khí.")
        print("-" * 60)

        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"VỌNG CHẨN: Đã lọc {len(nguyen_khi_files)} file chính chủ."
        )
        return nguyen_khi_files


vong_chan_trung_uong = VongChan()
