# trung_anh.py
# TRÙNG ẢNH (bóng trùng) - không phải Tạng Phủ, là một HIỆN TƯỢNG, cùng
# kiểu đặt tên như Phản Vũ/Tý Ngọ Lưu Chú (hiện tượng, không phải bộ phận
# cơ thể).
#
# Vì sao thêm: khảo sát developer 2026 - 40% nói AI làm TĂNG nợ kỹ thuật vì
# tạo code trùng lặp/dư thừa. Lý do: không AI nào (kể cả trong một phiên
# dài) nhớ hết những gì ĐÃ có trong dự án, nên nó viết lại logic đã tồn tại
# ở file khác dưới một cái tên khác. Trùng Ảnh đi tìm "cặp bóng" này: hai
# hàm ở hai file khác nhau có CẤU TRÚC LOGIC giống hệt nhau sau khi bỏ qua
# tên biến/tham số cụ thể.
#
# Chỉ hỗ trợ Python (cần AST thật để chuẩn hóa cấu trúc). JS/TS không có
# AST thật trong dự án này (xem ty_tang_parser.py) - thà bỏ qua còn hơn báo
# sai.
#
# BÀI HỌC từ Phản Vũ bản đầu (xem phan_vu_vong.py): chuẩn hóa quá tay từng
# gây trùng khớp giả tràn lan trên một dự án thật. Ở đây CỐ Ý KHÔNG đổi tên
# hàm/phương thức được GỌI (chỉ đổi tên biến/tham số) - hai hàm gọi hai hàm
# KHÁC NHAU sẽ không bao giờ bị coi là trùng, dù hình dạng câu lệnh giống
# nhau. Thà bỏ sót còn hơn báo giả.

import ast
import copy
import hashlib
import os

import oka_config as cfg

NGUONG_SO_NUT = 8   # hàm quá nhỏ (getter/setter một dòng...) bỏ qua, đỡ ồn
TEN_QUY_UOC = {
    '__init__', 'run', 'stop', 'start', 'main', 'setup_ui', 'update',
    'close', 'connect', '__repr__', '__str__', '__eq__', '__len__',
}


class _DoiTenBienChuan:
    def __init__(self):
        self.anh_xa = {}
        self.dem = 0

    def doi(self, ten):
        if ten not in self.anh_xa:
            self.anh_xa[ten] = f"v{self.dem}"
            self.dem += 1
        return self.anh_xa[ten]


class _ChuanHoa(ast.NodeTransformer):
    def __init__(self):
        self.doi_ten = _DoiTenBienChuan()

    def visit_Name(self, node):
        node.id = self.doi_ten.doi(node.id)
        return node

    def visit_arg(self, node):
        node.arg = self.doi_ten.doi(node.arg)
        return node

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        node.name = "FN"
        return node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        # KHÔNG đổi tên node.func - giữ nguyên tên hàm/phương thức được
        # gọi. Chỉ đổi tên các THAM SỐ truyền vào. Xem lời giải thích ở đầu
        # file: đây là điểm mấu chốt tránh trùng khớp giả.
        node.args = [self.visit(a) for a in node.args]
        node.keywords = [self.visit(k) for k in node.keywords]
        return node


def _chuan_hoa(func_node):
    """Trả về chuỗi cấu trúc CHUẨN HÓA của một hàm - chỉ còn lại HÌNH DẠNG
    logic thuần túy, tên biến/tham số bị xóa, docstring bị bỏ."""
    ban_sao = copy.deepcopy(func_node)
    ban_sao.name = "FN"
    _ChuanHoa().visit(ban_sao)

    than = ban_sao.body
    if (than and isinstance(than[0], ast.Expr)
            and isinstance(than[0].value, ast.Constant)
            and isinstance(than[0].value.value, str)):
        than = than[1:]
    if not than:
        return None

    return "|".join(ast.dump(stmt, annotate_fields=False) for stmt in than)


def _thu_thap_ham(duong_dan, rel):
    ket_qua = []
    try:
        with open(duong_dan, "r", encoding="utf-8", errors="replace") as f:
            cay = ast.parse(f.read(), filename=duong_dan)
    except (SyntaxError, ValueError, OSError):
        return ket_qua

    for node in ast.walk(cay):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name in TEN_QUY_UOC or node.name.startswith('_'):
            continue
        so_nut = sum(1 for _ in ast.walk(node))
        if so_nut < NGUONG_SO_NUT:
            continue
        chuan = _chuan_hoa(node)
        if chuan is None:
            continue
        bam = hashlib.sha1(chuan.encode("utf-8")).hexdigest()
        ket_qua.append((bam, rel, node.name, node.lineno, so_nut))
    return ket_qua


def quet(benh_nhan=None):
    """Tính thuần túy. Trả về [(bam, [(rel, ten_ham, dong, so_nut), ...]), ...]
    chỉ gồm những nhóm có >=2 hàm nằm ở >=2 FILE KHÁC NHAU."""
    benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
    if not os.path.isdir(benh_nhan):
        return []

    theo_bam = {}
    for root, dirs, files in os.walk(benh_nhan):
        dirs[:] = [
            d for d in dirs
            if d not in cfg.TA_KHI_DIRS
            and not cfg.la_thu_muc_trinh_duyet(os.path.join(root, d))
        ]
        for ten_file in files:
            if not ten_file.endswith(".py"):
                continue
            full = os.path.join(root, ten_file)
            if cfg.la_file_sinh_tu_dong(full):
                continue
            rel = os.path.relpath(full, benh_nhan)
            for bam, rel2, ten_ham, dong, so_nut in _thu_thap_ham(full, rel):
                theo_bam.setdefault(bam, []).append((rel2, ten_ham, dong, so_nut))

    nhom_trung = []
    for bam, ds in theo_bam.items():
        file_khac_nhau = {rel for rel, _, _, _ in ds}
        if len(ds) >= 2 and len(file_khac_nhau) >= 2:
            nhom_trung.append((bam, ds))

    nhom_trung.sort(key=lambda x: -len(x[1]))
    return nhom_trung


def ke_lai(nhom_trung, gioi_han=8):
    if not nhom_trung:
        return []
    dong = [
        f"🪞 TRÙNG ẢNH: {len(nhom_trung)} nhóm hàm có CẤU TRÚC LOGIC giống hệt "
        f"nhau (sau khi chuẩn hóa tên biến) nằm ở CÁC FILE KHÁC NHAU - dấu hiệu "
        f"logic bị viết lại thay vì tái dùng lại cái đã có. Chỉ so được cấu "
        f"trúc, không so được 'có nên gộp lại không' (CRUD boilerplate giống "
        f"nhau tự nhiên cũng khớp mẫu này):"
    ]
    for bam, ds in nhom_trung[:gioi_han]:
        noi = ", ".join(f"{rel}:{dong_so} ({ten})" for rel, ten, dong_so, _ in ds[:4])
        if len(ds) > 4:
            noi += f" +{len(ds) - 4} nữa"
        dong.append(f"   • {noi}")
    if len(nhom_trung) > gioi_han:
        dong.append(f"   … và {len(nhom_trung) - gioi_han} nhóm khác.")
    return ["\n".join(dong)]
