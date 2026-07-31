# vo_rong.py
# VỎ RỖNG - hiện tượng, không phải tạng phủ: một hàm mà TOÀN BỘ thân chỉ
# làm đúng một việc - gọi lại một hàm/phương thức khác và trả kết quả về
# nguyên xi, không thêm logic gì. Một cái thỉnh thoảng là hoàn toàn bình
# thường (adapter, tuân thủ interface). Nhiều cái DỒN vào một file là dấu
# hiệu "over-engineering" - khảo sát developer 2026 xếp lớp bọc không cần
# thiết vào nhóm nguồn nợ kỹ thuật AI tạo ra nhiều nhất.
#
# Chỉ hỗ trợ Python (cần AST thật để biết THÂN HÀM chỉ có đúng 1 câu lệnh).

import ast
import os

import oka_config as cfg

NGUONG_SO_VO = 3          # ít nhất bấy nhiêu cái trong 1 file mới đáng nói
TEN_QUY_UOC = {
    '__init__', '__repr__', '__str__', '__enter__', '__exit__',
}


def _la_ve_thang(func_node):
    """Thân hàm (bỏ docstring) chỉ có đúng 1 câu lệnh, và câu đó là
    return/gọi thẳng một hàm khác mà MỌI tham số truyền vào chỉ là biến
    trần trụi (không có biểu thức/tính toán gì thêm)."""
    than = func_node.body
    if (than and isinstance(than[0], ast.Expr)
            and isinstance(than[0].value, ast.Constant)
            and isinstance(than[0].value.value, str)):
        than = than[1:]
    if len(than) != 1:
        return False

    stmt = than[0]
    if isinstance(stmt, ast.Return):
        goi = stmt.value
    elif isinstance(stmt, ast.Expr):
        goi = stmt.value
    else:
        return False

    if not isinstance(goi, ast.Call):
        return False

    for a in goi.args:
        if not isinstance(a, ast.Name):
            return False
    for kw in goi.keywords:
        if kw.value is not None and not isinstance(kw.value, ast.Name):
            return False
    return True


def quet(benh_nhan=None):
    """Tính thuần túy. Trả về {rel_path: [(ten_ham, dong), ...]} - chỉ file
    có >= NGUONG_SO_VO hàm vỏ rỗng."""
    benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
    if not os.path.isdir(benh_nhan):
        return {}

    theo_file = {}
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
            try:
                with open(full, "r", encoding="utf-8", errors="replace") as f:
                    cay = ast.parse(f.read(), filename=full)
            except (SyntaxError, ValueError, OSError):
                continue

            rel = os.path.relpath(full, benh_nhan)
            vo = []
            for node in ast.walk(cay):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name in TEN_QUY_UOC:
                    continue
                if _la_ve_thang(node):
                    vo.append((node.name, node.lineno))
            if len(vo) >= NGUONG_SO_VO:
                theo_file[rel] = vo

    return theo_file


def ke_lai(theo_file, gioi_han=8):
    if not theo_file:
        return []
    dong = [
        f"🫧 VỎ RỖNG: {len(theo_file)} file có từ {NGUONG_SO_VO} hàm trở lên chỉ "
        f"làm mỗi việc GỌI LẠI một hàm khác, không thêm logic gì - dấu hiệu lớp "
        f"bọc (wrapper) có thể không cần thiết. Không sai kỹ thuật, nhưng đáng "
        f"tự hỏi: lớp này có thật sự cần không, hay chỉ để 'trông có kiến trúc'?"
    ]
    xep = sorted(theo_file.items(), key=lambda x: -len(x[1]))
    for rel, ds in xep[:gioi_han]:
        vi_du = ", ".join(f"{ten}:{dong_so}" for ten, dong_so in ds[:5])
        if len(ds) > 5:
            vi_du += f" +{len(ds) - 5} nữa"
        dong.append(f"   • {rel} ({len(ds)} hàm vỏ rỗng): {vi_du}")
    if len(xep) > gioi_han:
        dong.append(f"   … và {len(xep) - gioi_han} file khác.")
    return ["\n".join(dong)]
