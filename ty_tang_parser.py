# ty_tang_parser.py
# TỲ TẠNG - Chủ vận hóa: nhai file code thô, rút lấy Tinh Hoa (bộ xương)
#
# Nâng cấp so với bản đầu:
#   1. Mỗi bệnh nhân một ký ức riêng (hết cảnh bệnh án trộn lẫn)
#   2. Rút cả CHỮ KÝ hàm và QUAN HỆ GỌI NHAU, không chỉ tên trơ trọi
#      (Levels of Processing: xử lý sâu thì nhớ bền, dù tốn thêm chút chỗ)
#   3. CỔNG PREDICTION-ERROR: cấu trúc không đổi thì không ghi, không báo,
#      không đánh thức Thận đi backup. Không có gì mới thì không tốn tài nguyên.

import os
import re
import ast
import json
import hashlib
from datetime import datetime

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

# Tăng số này mỗi khi Tỳ Tạng học được cách rút thêm tinh hoa mới,
# để ký ức cũ tự lỗi thời và được nhai lại.
PHIEN_BAN_TINH_HOA = 3   # +1: thêm nhánh JS/TS (regex)

# ====================================================================
# NHÁNH JS/TS/JSX/TSX - regex nhẹ, KHÔNG phải AST thật.
#
# Vì sao không dùng AST thật cho JS: cần thư viện ngoài (vd tree-sitter),
# đi ngược triết lý "không cần cài gì thêm" của cả dự án. Regex thô hơn
# (có thể sót vài kiểu cú pháp lạ) nhưng đủ để rút tên hàm/class/import -
# tốt hơn nhiều so với bỏ qua hoàn toàn cả phần frontend như trước đây.
# ====================================================================
_RE_JS_FUNC = re.compile(
    r'^[ \t]*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)',
    re.MULTILINE,
)
_RE_JS_ARROW_CONST = re.compile(
    r'^[ \t]*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*(?::\s*[^=]+)?=\s*(?:async\s*)?\(([^)]*)\)\s*(?::\s*[^=]+)?=>',
    re.MULTILINE,
)
_RE_JS_CLASS = re.compile(
    r'^[ \t]*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)(?:\s+extends\s+([A-Za-z_$][\w$.]*))?',
    re.MULTILINE,
)
_RE_JS_METHOD_SHORTHAND = re.compile(
    r'^[ \t]*(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*([A-Za-z_$][\w$]*)\s*\(([^)]*)\)\s*(?::\s*[^{]+)?\{',
    re.MULTILINE,
)
_RE_JS_IMPORT = re.compile(
    r'''^[ \t]*import\s+(?:[\w${},\s*]+\s+from\s+)?['"]([^'"]+)['"]''',
    re.MULTILINE,
)
_RE_JS_REQUIRE = re.compile(r'''require\(\s*['"]([^'"]+)['"]\s*\)''')
_RE_JS_CALL = re.compile(r'\b([A-Za-z_$][\w$]*)\s*\(')
_JS_TU_KHOA = {
    'if', 'for', 'while', 'switch', 'catch', 'function', 'return', 'typeof',
    'new', 'in', 'of', 'else', 'do', 'try', 'throw', 'await', 'yield',
    'constructor', 'super',
}


def _tim_khoi_dong(noi_dung, vi_tri_mo_ngoac):
    """Tìm vị trí dấu '}' khớp với dấu '{' tại vi_tri_mo_ngoac (đếm độ sâu
    ngoặc thô - không hiểu string/comment chứa ngoặc, nhưng đủ dùng cho
    phần lớn code thật)."""
    do_sau = 0
    for i in range(vi_tri_mo_ngoac, len(noi_dung)):
        if noi_dung[i] == '{':
            do_sau += 1
        elif noi_dung[i] == '}':
            do_sau -= 1
            if do_sau == 0:
                return i
    return None


def _boc_tach_js(noi_dung):
    """Rút tinh hoa từ JS/TS/JSX/TSX - xem ghi chú nhánh JS/TS phía trên."""
    ham = {}
    for m in _RE_JS_FUNC.finditer(noi_dung):
        ham[m.group(1)] = f"({m.group(2).strip()})"
    for m in _RE_JS_ARROW_CONST.finditer(noi_dung):
        ham.setdefault(m.group(1), f"({m.group(2).strip()})")

    classes = {}
    for m in _RE_JS_CLASS.finditer(noi_dung):
        ten_cls, ke_thua = m.group(1), m.group(2)
        vi_tri_mo = noi_dung.find('{', m.end())
        methods = {}
        if vi_tri_mo != -1:
            vi_tri_dong = _tim_khoi_dong(noi_dung, vi_tri_mo)
            than = noi_dung[vi_tri_mo:vi_tri_dong] if vi_tri_dong else noi_dung[vi_tri_mo:vi_tri_mo + 3000]
            for mm in _RE_JS_METHOD_SHORTHAND.finditer(than):
                ten_m = mm.group(1)
                if ten_m in _JS_TU_KHOA:
                    continue
                methods[ten_m] = f"({mm.group(2).strip()})"
        classes[ten_cls] = {
            "ke_thua": [ke_thua] if ke_thua else [],
            "methods": methods,
        }

    imports = set()
    for m in _RE_JS_IMPORT.finditer(noi_dung):
        goc = m.group(1)
        if goc.startswith('.'):
            continue  # import nội bộ dự án (./foo) - chỉ giữ thư viện ngoài
        imports.add(goc.split('/')[0])
    for m in _RE_JS_REQUIRE.finditer(noi_dung):
        goc = m.group(1)
        if not goc.startswith('.'):
            imports.add(goc.split('/')[0])

    goi = {m.group(1) for m in _RE_JS_CALL.finditer(noi_dung)} - _JS_TU_KHOA

    return {
        "dong": noi_dung.count('\n') + 1,
        "classes": classes,
        "ham": ham,
        "goi": sorted(goi),
        "tham_chieu": [],
        "import": sorted(imports),
    }


def _ten_duoc_goi(node):
    """Lấy tên hàm được gọi trong một biểu thức Call"""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _chu_ky(node):
    """Chữ ký hàm dạng người đọc được: (a, b=1, *args)"""
    try:
        return f"({ast.unparse(node.args)})"
    except Exception:
        return "(...)"


class TyTang:
    def __init__(self):
        self._ky_uc = {}   # benh_nhan -> dữ liệu ký ức

        # Tỳ tự nối dây thần kinh của mình, không để main/gui nối hộ.
        # Trước đây main và gui mỗi nơi nối một kiểu nên dễ nối trùng, nối sót.
        xuong_song_trung_uong.dang_ky_nhan_khi("CODE_HOAN_HAO", self.tieu_hoa_code)
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_NHAI", self.tieu_hoa_toan_bo)

    # ---------------- Ký ức trên ổ cứng ----------------

    def tai_ky_uc(self, benh_nhan):
        if benh_nhan in self._ky_uc:
            return self._ky_uc[benh_nhan]

        duong_dan = cfg.duong_dan_ky_uc(benh_nhan)
        du_lieu = {"benh_nhan": benh_nhan, "cap_nhat": None, "files": {}}
        if os.path.exists(duong_dan):
            try:
                with open(duong_dan, 'r', encoding='utf-8') as f:
                    da_luu = json.load(f)
                if isinstance(da_luu, dict) and "files" in da_luu:
                    du_lieu = da_luu
            except (json.JSONDecodeError, OSError):
                pass

        self._ky_uc[benh_nhan] = du_lieu
        return du_lieu

    def luu_ky_uc(self, benh_nhan):
        du_lieu = self.tai_ky_uc(benh_nhan)
        du_lieu["cap_nhat"] = datetime.now().isoformat(timespec='seconds')
        with open(cfg.duong_dan_ky_uc(benh_nhan), 'w', encoding='utf-8') as f:
            json.dump(du_lieu, f, indent=2, ensure_ascii=False)

    # ---------------- Nhai code, rút bộ xương ----------------

    def boc_tach(self, duong_dan_file):
        """Đọc một file code, trả về bộ xương của nó (hoặc None nếu không
        nhai được). Python dùng ast thật; JS/TS/JSX/TSX dùng regex nhẹ
        (xem _boc_tach_js) - đuôi lạ khác thì chưa hỗ trợ, trả về None."""
        _, duoi = os.path.splitext(duong_dan_file)
        duoi = duoi.lower()

        try:
            with open(duong_dan_file, 'r', encoding='utf-8') as f:
                noi_dung = f.read()
        except OSError:
            return None

        if duoi != '.py':
            if duoi not in cfg.CAC_DUOI_HO_TRO:
                return None
            tinh_hoa = _boc_tach_js(noi_dung)
            tinh_hoa["van_tay"] = self._van_tay(tinh_hoa)
            return tinh_hoa

        try:
            cay_code = ast.parse(noi_dung)
        except (SyntaxError, ValueError):
            return None

        tinh_hoa = {
            "dong": noi_dung.count('\n') + 1,
            "classes": {},
            "ham": {},
            "goi": [],
            "import": [],
        }

        # Đi đúng tầng, không dùng ast.walk phẳng lì:
        # method nằm trong class thì thuộc về class, không trồi lên thành hàm tự do
        for node in cay_code.body:
            if isinstance(node, ast.ClassDef):
                methods = {}
                for con in node.body:
                    if isinstance(con, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods[con.name] = _chu_ky(con)
                tinh_hoa["classes"][node.name] = {
                    "ke_thua": [ast.unparse(b) for b in node.bases],
                    "methods": methods,
                }
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                tinh_hoa["ham"][node.name] = _chu_ky(node)

        # Quét toàn cây để lấy quan hệ gọi nhau + import
        #
        # Phải phân biệt hai kiểu dùng, nếu không sẽ mù trước kiến trúc event-driven:
        #   GỌI       : phat_khi(...)              - gọi thẳng
        #   THAM CHIẾU: dang_ky(..., self.ghi_log) - đưa tên hàm đi gửi, chưa gọi ngay
        # Chỉ đếm kiểu thứ nhất thì mọi callback đều bị kết oan là "code chết".
        da_goi = set()
        da_tham_chieu = set()
        da_import = set()

        for node in ast.walk(cay_code):
            if isinstance(node, ast.Call):
                ten = _ten_duoc_goi(node)
                if ten:
                    da_goi.add(ten)
            elif isinstance(node, ast.Attribute):
                da_tham_chieu.add(node.attr)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                da_tham_chieu.add(node.id)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    da_import.add(a.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    da_import.add(node.module.split('.')[0])

        tinh_hoa["goi"] = sorted(da_goi)
        tinh_hoa["tham_chieu"] = sorted(da_tham_chieu - da_goi)
        tinh_hoa["import"] = sorted(da_import)
        tinh_hoa["van_tay"] = self._van_tay(tinh_hoa)
        return tinh_hoa

    @staticmethod
    def _van_tay(tinh_hoa):
        """Vân tay CẤU TRÚC - đổi khoảng trắng hay comment thì vân tay không đổi.
        Đây là lõi của cổng Prediction-error.

        PHIEN_BAN_TINH_HOA nằm trong vân tay để khi Tỳ Tạng được nâng cấp
        (biết rút thêm thứ mới), ký ức cũ tự động lỗi thời và được nhai lại.
        Không có nó, chính cái cổng tiết kiệm tài nguyên sẽ khóa luôn bản nâng cấp.
        """
        loi = json.dumps(
            {
                "v": PHIEN_BAN_TINH_HOA,
                "classes": tinh_hoa["classes"],
                "ham": tinh_hoa["ham"],
                "import": tinh_hoa["import"],
            },
            sort_keys=True, ensure_ascii=False
        )
        return hashlib.sha1(loi.encode('utf-8')).hexdigest()[:12]

    # ---------------- So sánh: cái gì thực sự đổi? ----------------

    @staticmethod
    def so_sanh(cu, moi):
        """Diff CẤU TRÚC, không phải diff dòng.
        Giúp bạn duyệt thay đổi trong 10 giây thay vì đọc 500 dòng.

        Phải soi cả method BÊN TRONG class. Bản đầu chỉ đối chiếu hàm tầng ngoài
        và tên class, nên với dự án viết theo lối hướng đối tượng - tức gần như
        mọi dự án - nó báo "cấu trúc giữ nguyên" ngay cả khi vừa thêm hẳn một
        method mới. Mù đúng vào loại thay đổi phổ biến nhất.
        """
        if cu is None:
            return {"moi_tinh": True}

        ham_cu, ham_moi = set(cu.get("ham", {})), set(moi.get("ham", {}))
        cls_cu_d, cls_moi_d = cu.get("classes", {}), moi.get("classes", {})
        cls_cu, cls_moi = set(cls_cu_d), set(cls_moi_d)

        doi_chu_ky = [
            t for t in (ham_cu & ham_moi)
            if cu["ham"][t] != moi["ham"][t]
        ]

        # Soi vào trong từng class còn tồn tại ở cả hai bên
        method_them, method_mat = [], []
        for ten_cls in (cls_cu & cls_moi):
            m_cu = cls_cu_d[ten_cls].get("methods", {})
            m_moi = cls_moi_d[ten_cls].get("methods", {})
            for m in sorted(set(m_moi) - set(m_cu)):
                method_them.append(f"{ten_cls}.{m}")
            for m in sorted(set(m_cu) - set(m_moi)):
                method_mat.append(f"{ten_cls}.{m}")
            for m in sorted(set(m_cu) & set(m_moi)):
                if m_cu[m] != m_moi[m]:
                    doi_chu_ky.append(f"{ten_cls}.{m}")

        return {
            "moi_tinh": False,
            "ham_them": sorted(ham_moi - ham_cu),
            "ham_mat": sorted(ham_cu - ham_moi),
            "class_them": sorted(cls_moi - cls_cu),
            "class_mat": sorted(cls_cu - cls_moi),
            "method_them": method_them,
            "method_mat": method_mat,
            "doi_chu_ky": sorted(doi_chu_ky),
        }

    @staticmethod
    def ke_lai_thay_doi(ten_file, khac_biet):
        if khac_biet.get("moi_tinh"):
            return f"📥 File mới vào ký ức: {ten_file}"

        def _gom(nhan, ds, dau):
            return f"{dau}{len(ds)} {nhan} ({', '.join(ds)})" if ds else None

        manh = [m for m in (
            _gom("class", khac_biet["class_them"], "+"),
            _gom("class", khac_biet["class_mat"], "-"),
            _gom("hàm", khac_biet["ham_them"], "+"),
            _gom("hàm", khac_biet["ham_mat"], "-"),
            _gom("method", khac_biet.get("method_them", []), "+"),
            _gom("method", khac_biet.get("method_mat", []), "-"),
        ) if m]

        if khac_biet["doi_chu_ky"]:
            manh.append(f"⚠ đổi chữ ký: {', '.join(khac_biet['doi_chu_ky'])}")

        # Vân tay đổi mà không chỉ ra được đổi ở đâu thì phải nói thật là
        # "chỉ đổi phần thân", đừng báo "giữ nguyên" khiến người đọc hiểu nhầm
        return f"🔍 {ten_file}: " + ("; ".join(manh) if manh else "chỉ đổi phần thân hàm")

    # ---------------- Cửa vào chính ----------------

    def tieu_hoa_code(self, duong_dan_file):
        """Nhận một file vừa đổi. Chỉ ghi nhớ nếu CẤU TRÚC thực sự khác trước."""
        if not duong_dan_file or os.path.splitext(str(duong_dan_file))[1].lower() not in cfg.CAC_DUOI_HO_TRO:
            return
        if cfg.la_ta_khi(duong_dan_file):
            return

        benh_nhan = cfg.tim_benh_nhan_cua(duong_dan_file)
        ky_uc = self.tai_ky_uc(benh_nhan)

        tinh_hoa = self.boc_tach(duong_dan_file)
        if tinh_hoa is None:
            xuong_song_trung_uong.phat_khi(
                "GHI_LOG", f"TỲ TẠNG: Không nhai nổi {os.path.basename(duong_dan_file)} (cú pháp hỏng)."
            )
            return

        try:
            khoa = os.path.relpath(duong_dan_file, benh_nhan)
        except ValueError:
            khoa = os.path.basename(duong_dan_file)

        cu = ky_uc["files"].get(khoa)

        # === CỔNG PREDICTION-ERROR ===
        # Không có gì bất ngờ thì không tiêu tốn gì thêm.
        if cu and cu.get("van_tay") == tinh_hoa["van_tay"]:
            return

        khac_biet = self.so_sanh(cu, tinh_hoa)
        ky_uc["files"][khoa] = tinh_hoa
        self.luu_ky_uc(benh_nhan)

        xuong_song_trung_uong.phat_khi("GHI_LOG", self.ke_lai_thay_doi(khoa, khac_biet))

        # Chỉ khi cấu trúc đổi thật mới đánh thức Thận đi cất Nguyên Khí
        xuong_song_trung_uong.phat_khi("CAU_TRUC_DA_DOI", {
            "benh_nhan": benh_nhan,
            "file": duong_dan_file,
            "khoa": khoa,
            "khac_biet": khac_biet,
        })

        # Báo cho Tâm Tạng cập nhật bối cảnh (dây thần kinh trước đây bị đứt)
        xuong_song_trung_uong.phat_khi("CODE_DA_TIEU_HOA", benh_nhan)

    def tieu_hoa_toan_bo(self, benh_nhan=None):
        """Nhai trọn một dự án - dùng khi mới nhận bệnh nhân"""
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        so_file = 0

        for root, dirs, files in os.walk(benh_nhan):
            dirs[:] = [d for d in dirs if d not in cfg.TA_KHI_DIRS]
            for ten in files:
                if os.path.splitext(ten)[1].lower() in cfg.CAC_DUOI_HO_TRO:
                    self.tieu_hoa_code(os.path.join(root, ten))
                    so_file += 1

        ky_uc = self.tai_ky_uc(benh_nhan)
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG",
            f"TỲ TẠNG: Đã nhai xong {so_file} file, ký ức đang giữ {len(ky_uc['files'])} bộ xương."
        )
        return ky_uc


# Tạo ra thực thể Tỳ Tạng duy nhất
ty_tang_trung_uong = TyTang()
