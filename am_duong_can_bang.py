# am_duong_can_bang.py
# CÂN BẰNG ÂM DƯƠNG - mở rộng của Đởm (dom_validator.py chỉ bắt lỗi CÚ
# PHÁP), nhắm thẳng vào "Ảo giác Hệ thống" trong Tam Độc gốc: AI gọi một
# hàm/phương thức KHÔNG HỀ tồn tại.
#
# Ẩn dụ: mỗi LỜI GỌI HÀM (Dương - hành động) phải có một LỜI ĐỊNH NGHĨA
# tương ứng (Âm - phản ứng) tồn tại thật ở đâu đó. Gọi mà không có định
# nghĩa là "liên kết không cân bằng".
#
# QUAN TRỌNG - phạm vi CỐ Ý thu hẹp để tránh lặp lại thảm họa Phản Vũ bản
# đầu (báo giả tràn lan trên dự án thật vì suy diễn quá tay):
#   1. CHỈ kiểm tra lời gọi TÊN TRẦN (bare name: `foo()`), bỏ qua lời gọi
#      qua thuộc tính như `module.foo()` hay `obj.foo()` - loại này cần
#      suy luận kiểu dữ liệu mới xác minh đúng được, rủi ro báo giả cao.
#   2. CHỈ kiểm tra `self.method()` bên trong lớp KHÔNG kế thừa gì (hoặc
#      chỉ kế thừa `object`) - lớp có kế thừa thì method thừa hưởng từ lớp
#      cha sẽ bị báo giả là "không tồn tại" nếu chỉ xét thân lớp con.
#   3. File có `from x import *` bị bỏ qua HOÀN TOÀN - không biết star-
#      import mang tên gì vào, thà bỏ sót còn hơn báo sai.
#   4. Chỉ hỗ trợ Python (cần AST thật).
#
# Vẫn có thể báo giả (tên gán qua globals()[...]=, entry point động...) -
# vì vậy MỌI phát hiện ở đây là SUY ĐOÁN, không phải CHẮC CHẮN.

import ast
import builtins
import os

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

_BUILTINS = set(dir(builtins)) | {"self", "cls", "__class__"}


def _thu_thap_dinh_nghia_va_star(cay):
    """Mọi tên coi là 'đã định nghĩa' trong file: hàm/lớp, import, và bất
    kỳ tên nào từng được GÁN (Name với ctx=Store) ở bất kỳ đâu - rộng tay
    có chủ đích để giảm báo giả, chấp nhận bỏ sót một số ca thật."""
    dinh_nghia = set()
    co_star_import = False

    for node in ast.walk(cay):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            dinh_nghia.add(node.name)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    co_star_import = True
                else:
                    dinh_nghia.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                dinh_nghia.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            dinh_nghia.add(node.id)
        elif isinstance(node, ast.arg):
            dinh_nghia.add(node.arg)

    return dinh_nghia, co_star_import


def _thu_thap_loi_goi_ten_tran(cay):
    """[(ten_ham, dong), ...] - CHỈ lời gọi tên trần foo(), bỏ qua a.b()."""
    return [
        (node.func.id, node.lineno)
        for node in ast.walk(cay)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    ]


def _duyet_tru_lop_con(node):
    """Duyệt mọi node con của `node`, TRỪ việc đi sâu vào bên trong một
    ClassDef LỒNG bên trong - lớp lồng có `self` riêng, không thuộc phạm vi
    lớp ngoài. Hàm lồng bình thường (không phải class) vẫn được đi vào,
    vì `self` bên trong closure vẫn là self của phương thức ngoài.

    BÀI HỌC THẬT: bản đầu gộp theo TÊN lớp vào một dict dùng chung. Đo trên
    TOOL_YOUTUBE_NEW thật phát hiện file có 4 lớp lồng CÙNG TÊN `GUILogger`
    định nghĩa ở 4 chỗ khác nhau trong cùng file (mẫu hay gặp: logger nội
    bộ định nghĩa lại trong từng hàm) - lớp sau ghi đè thông tin lớp trước
    trong dict, khiến 3/4 lớp bị đối chiếu NHẦM với thân lớp của lớp thứ 4,
    báo giả `self.log_func()` dù nó được định nghĩa đúng trong chính lớp
    đó. Sửa bằng cách xử lý MỖI NODE lớp độc lập theo danh tính, không gộp
    theo tên."""
    for con in ast.iter_child_nodes(node):
        yield con
        if not isinstance(con, ast.ClassDef):
            yield from _duyet_tru_lop_con(con)


def _quet_mot_lop(class_node):
    """Trả về (ten_biet, danh_sach_goi_self) cho MỘT node lớp cụ thể,
    phạm vi CHỈ trong thân lớp này. None nếu lớp có kế thừa (bỏ qua để
    tránh báo giả method thừa hưởng từ lớp cha)."""
    an_toan = (not class_node.bases) or all(
        isinstance(b, ast.Name) and b.id == "object" for b in class_node.bases
    )
    if not an_toan:
        return None

    # Lớp lồng định nghĩa trực tiếp trong thân lớp (vd `class MyLogger:`
    # bên trong `class MusicDownloader:`) cũng là thuộc tính hợp lệ truy
    # cập qua self.TenLop(...) - bỏ sót điều này gây báo giả thật, bắt
    # được khi chạy trên TOOL_YOUTUBE_NEW (self.MyLogger()).
    ten_biet = {
        n.name for n in class_node.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }
    goi_self = []
    for n in _duyet_tru_lop_con(class_node):
        if (isinstance(n, ast.Attribute) and isinstance(n.ctx, ast.Store)
                and isinstance(n.value, ast.Name) and n.value.id == "self"):
            ten_biet.add(n.attr)
    for n in _duyet_tru_lop_con(class_node):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"):
            ten = n.func.attr
            if not ten.startswith("__"):
                goi_self.append((ten, n.lineno))

    return ten_biet, goi_self


def _thu_thap_loi_goi_self_toan_file(cay):
    """[(ten_lop, ten_method, dong), ...] - mỗi lớp xét ĐỘC LẬP theo node,
    không gộp theo tên."""
    ket_qua = []
    for node in ast.walk(cay):
        if not isinstance(node, ast.ClassDef):
            continue
        ket = _quet_mot_lop(node)
        if ket is None:
            continue
        ten_biet, goi_self = ket
        for ten, dong in goi_self:
            if ten not in ten_biet:
                ket_qua.append((node.name, ten, dong))
    return ket_qua


def _kiem_tra_file(duong_dan):
    try:
        with open(duong_dan, "r", encoding="utf-8", errors="replace") as f:
            cay = ast.parse(f.read(), filename=duong_dan)
    except (SyntaxError, ValueError, OSError):
        return []

    dinh_nghia, co_star_import = _thu_thap_dinh_nghia_va_star(cay)
    if co_star_import:
        return []

    phat_hien = []
    for ten, dong in _thu_thap_loi_goi_ten_tran(cay):
        if ten in _BUILTINS or ten in dinh_nghia:
            continue
        phat_hien.append(("goi_ten_tran", None, ten, dong))

    for ten_lop, ten_method, dong in _thu_thap_loi_goi_self_toan_file(cay):
        phat_hien.append(("goi_self", ten_lop, ten_method, dong))

    return phat_hien


def kiem_tra_mot_file(duong_dan_file):
    """Dùng cho phản hồi tức thời ngay sau khi một file được lưu (Đởm gọi
    qua sự kiện FILE_DA_LUU)."""
    return _kiem_tra_file(duong_dan_file)


def quet(benh_nhan=None):
    """Quét toàn dự án. Trả về {rel_path: [phát hiện, ...]}."""
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
            phat_hien = _kiem_tra_file(full)
            if phat_hien:
                rel = os.path.relpath(full, benh_nhan)
                theo_file[rel] = phat_hien

    return theo_file


def _dong_hien_thi(loai, ten_lop, ten, dong):
    if loai == "goi_ten_tran":
        return f"dòng {dong}: gọi `{ten}()` nhưng không thấy định nghĩa/import tên này trong file"
    return f"dòng {dong}: `self.{ten}()` nhưng lớp `{ten_lop}` không có phương thức/thuộc tính này"


def ke_lai(theo_file, gioi_han_file=8, gioi_han_moi_file=5):
    if not theo_file:
        return []

    tong = sum(len(ds) for ds in theo_file.values())
    dong = [
        f"⚖️ CÂN BẰNG ÂM DƯƠNG: {tong} lời gọi (Dương) không tìm thấy định "
        f"nghĩa tương ứng (Âm) trong {len(theo_file)} file - dấu hiệu AI gọi "
        f"hàm/phương thức KHÔNG TỒN TẠI. Chỉ xét lời gọi tên trần và "
        f"self.method() trong lớp không kế thừa - CÓ THỂ báo giả với tên tạo "
        f"động (globals()[...], entry point qua route/CLI...):"
    ]
    xep = sorted(theo_file.items(), key=lambda x: -len(x[1]))
    for rel, ds in xep[:gioi_han_file]:
        dong.append(f"   • {rel}:")
        for loai, ten_lop, ten, so_dong in ds[:gioi_han_moi_file]:
            dong.append(f"      - {_dong_hien_thi(loai, ten_lop, ten, so_dong)}")
        if len(ds) > gioi_han_moi_file:
            dong.append(f"      … và {len(ds) - gioi_han_moi_file} chỗ khác trong file này.")
    if len(xep) > gioi_han_file:
        dong.append(f"   … và {len(xep) - gioi_han_file} file khác.")
    return ["\n".join(dong)]


class CanBangAmDuong:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_SOI_CAN_BANG", self.soi_va_bao_cao)
        # Phản hồi tức thời ngay sau khi MỘT file được lưu - đúng tinh
        # thần Đởm gốc (dom_validator.py), chỉ khác là kiểm cân bằng gọi
        # hàm/định nghĩa thay vì cú pháp.
        xuong_song_trung_uong.dang_ky_nhan_khi("FILE_DA_LUU", self._kiem_tra_ngay)

    def _kiem_tra_ngay(self, duong_dan_file):
        if not duong_dan_file or not str(duong_dan_file).endswith(".py"):
            return
        phat_hien = kiem_tra_mot_file(duong_dan_file)
        if not phat_hien:
            return
        ten_file = os.path.basename(duong_dan_file)
        for loai, ten_lop, ten, dong in phat_hien[:5]:
            xuong_song_trung_uong.phat_khi(
                "GHI_LOG",
                f"⚖️ CÂN BẰNG ÂM DƯƠNG: {ten_file} - {_dong_hien_thi(loai, ten_lop, ten, dong)}",
            )

    def soi_va_bao_cao(self, benh_nhan=None):
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        theo_file = quet(benh_nhan)

        print("\n" + "⚖️ " * 5)
        print(f"⚖️ [CÂN BẰNG ÂM DƯƠNG]: {os.path.basename(benh_nhan)}")
        print("⚖️ " * 5)

        if not theo_file:
            print("\n🟢 Không thấy lời gọi nào thiếu định nghĩa tương ứng "
                  "(trong phạm vi kiểm tra được - xem giới hạn ở đầu file).")
        else:
            for van in ke_lai(theo_file, gioi_han_file=30, gioi_han_moi_file=15):
                print(van)

        print("-" * 60 + "\n")
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG",
            f"CÂN BẰNG ÂM DƯƠNG: đã soi {sum(len(d) for d in theo_file.values())} dấu hiệu.",
        )
        return theo_file


can_bang_am_duong_trung_uong = CanBangAmDuong()
