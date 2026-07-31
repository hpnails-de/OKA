# ve_khi_bao_ve.py
# VỆ KHÍ (衛氣) - không nằm trong Ngũ Tạng/Lục Phủ gốc, mà là một khái niệm
# riêng trong Đông Y: thứ khí "hành ở ngoài mạch", tuần hành ngoài bì mao
# (da lông) ngày đêm, nhiệm vụ DUY NHẤT là ngăn ngoại tà xâm nhập từ bên
# ngoài vào. Khác Đởm (dom_validator.py - xét code TỰ nó có lỗi cú pháp hay
# không) và khác Miễn Dịch (mien_dich.py - nhớ lại bệnh cũ ĐàI PHÁT bên
# trong) - Vệ Khí chỉ nhìn ra CỬA: chỗ nào dữ liệu từ bên ngoài (input
# người dùng, mạng, shell) có thể chui thẳng vào chỗ nguy hiểm.
#
# Lý do thêm module này: khảo sát thực tế người dùng AI coding assistant
# (Reddit/HN/khảo sát ngành 2026) cho thấy ~1/4 đoạn code AI sinh ra chứa
# lỗ hổng bảo mật đã biết, phần lớn vì AI không có ngữ cảnh "input này có
# tin được không" - nó chỉ viết code CHẠY ĐƯỢC, không viết code AN TOÀN,
# trừ khi được nhắc. Vệ Khí không cố sửa - chỉ đứng gác, chỉ ra ĐÚNG chỗ để
# người/AI tự quyết định.
#
# QUAN TRỌNG: đây là quét bằng REGEX (đúng nguyên tắc không cài đặt của cả
# dự án), KHÔNG phải phân tích luồng dữ liệu (taint analysis) thật. Nó thấy
# MẪU đáng ngờ, không thấy được ngữ cảnh (dữ liệu đó có thật sự đến từ
# người dùng không). Vì vậy MỌI nhận định ở đây đều gắn nhãn SUY ĐOÁN,
# không có ngoại lệ - kể cả khi mẫu regex khớp 100% chính xác cú pháp, việc
# "đây có phải lỗ hổng thật" vẫn là suy luận, không phải phép đếm.

import os
import re

import oka_config as cfg
from doc_mach_bus import xuong_song_trung_uong

# (mẫu, tên_ngắn, lời_giải_thích)
MAU_PY = [
    (re.compile(r"\b(eval|exec)\s*\("), "eval/exec",
     "chạy chuỗi như code - nếu chuỗi đó chứa dữ liệu người dùng thì kẻ tấn công chạy được lệnh tùy ý"),
    (re.compile(r"\bos\.system\s*\("), "os.system",
     "chạy lệnh shell trực tiếp - ghép chuỗi người dùng vào đây là command injection"),
    (re.compile(r"shell\s*=\s*True"), "subprocess shell=True",
     "bật shell khi gọi subprocess - nếu tham số có dữ liệu người dùng thì injection được"),
    (re.compile(r"\bpickle\.(loads?|Unpickler)\s*\("), "pickle.load",
     "giải nén pickle từ nguồn không tin được có thể thực thi code tùy ý"),
    (re.compile(r"yaml\.load\s*\((?!.*SafeLoader)"), "yaml.load không SafeLoader",
     "yaml.load mặc định có thể khởi tạo object tùy ý - nên dùng yaml.safe_load"),
    (re.compile(r"verify\s*=\s*False"), "verify=False",
     "tắt xác thực chứng chỉ TLS - dễ bị man-in-the-middle"),
    (re.compile(r"CERT_NONE|_create_unverified_context"), "SSL không kiểm chứng chỉ",
     "tắt kiểm tra chứng chỉ SSL/TLS hoàn toàn"),
    (re.compile(r"debug\s*=\s*True"), "debug=True",
     "chạy ở chế độ debug trong môi trường thật lộ traceback/biến nội bộ cho người ngoài"),
    (re.compile(r"\.execute\s*\(\s*f[\"']|\.execute\s*\([^)]*%\s*\("), "SQL nối chuỗi trực tiếp",
     "ghép chuỗi vào câu SQL thay vì dùng tham số hóa (parameterized query) - cửa mở cho SQL injection"),
    (re.compile(r"chmod\s*\(\s*[^,]+,\s*0o?7[0-7][0-7]\b"), "chmod quá quyền",
     "cấp quyền ghi/thực thi cho mọi người trên file/thư mục"),
]

MAU_JS = [
    (re.compile(r"\beval\s*\("), "eval",
     "chạy chuỗi như code - dữ liệu người dùng lọt vào đây là chạy được mã tùy ý"),
    (re.compile(r"\bnew Function\s*\("), "new Function()",
     "tương đương eval - dựng hàm từ chuỗi bất kỳ lúc chạy"),
    (re.compile(r"\bdangerouslySetInnerHTML\b"), "dangerouslySetInnerHTML",
     "chèn HTML thô vào DOM - dữ liệu người dùng ở đây là cửa XSS"),
    (re.compile(r"document\.write\s*\("), "document.write",
     "ghi HTML thô ra trang - dễ dính XSS nếu có dữ liệu người dùng"),
    (re.compile(r"rejectUnauthorized\s*:\s*false"), "rejectUnauthorized: false",
     "tắt xác thực chứng chỉ TLS phía Node.js"),
    (re.compile(r"Access-Control-Allow-Origin.{0,10}\*"), "CORS mở toàn bộ (*)",
     "cho phép MỌI domain gọi API này - nên giới hạn danh sách domain cụ thể"),
    (re.compile(r"exec(Sync)?\s*\(\s*`[^`]*\$\{"), "child_process.exec với template string",
     "ghép biến trực tiếp vào lệnh shell qua template literal - command injection"),
    (re.compile(r"localStorage\.setItem\([^)]*(token|jwt)", re.IGNORECASE), "token lưu ở localStorage",
     "localStorage đọc được bởi mọi script trên trang (kể cả script XSS chèn vào) - token nhạy cảm nên ưu tiên cookie httpOnly"),
]

# Biến trông như bí mật gán trực tiếp chuỗi literal - áp dụng cho cả 2 ngôn ngữ
MAU_BI_MAT = re.compile(
    r"(?i)\b(api[_-]?key|secret[_-]?key|secret|password|passwd|access[_-]?token|"
    r"private[_-]?key)\s*[:=]\s*[\"']([^\"']{8,})[\"']"
)
_GIA_TRI_MAU = re.compile(
    r"(?i)^(x{3,}|\*{3,}|changeme|your[_-]|example|placeholder|<.*>|\$\{|\.\.\.|test|dummy|fake|none|null)"
)


def _co_ve_la_bi_mat_that(gia_tri):
    """Loại bớt placeholder rõ ràng (YOUR_KEY_HERE, xxx, <secret>...) để đỡ
    ồn - dù vậy phần còn lại vẫn chỉ là SUY ĐOÁN, không chắc chắn là bí mật
    thật hay chỉ là ví dụ/test fixture."""
    return not _GIA_TRI_MAU.match(gia_tri.strip())


def _quet_file(duong_dan, mau_ngon_ngu):
    ket_qua = []
    try:
        with open(duong_dan, "r", encoding="utf-8", errors="replace") as f:
            dong_list = f.readlines()
    except OSError:
        return ket_qua

    for so_dong, dong in enumerate(dong_list, start=1):
        for mau, ten, giai_thich in mau_ngon_ngu:
            if mau.search(dong):
                ket_qua.append((so_dong, ten, giai_thich, dong.strip()[:100]))
        m = MAU_BI_MAT.search(dong)
        if m and _co_ve_la_bi_mat_that(m.group(2)):
            ket_qua.append((
                so_dong, "chuỗi bí mật viết cứng",
                "biến trông như API key/mật khẩu/token được gán thẳng bằng chuỗi trong code, "
                "thay vì đọc từ biến môi trường - lộ ra ngay nếu code này lên git công khai",
                dong.strip()[:100],
            ))
    return ket_qua


def quet(benh_nhan=None):
    """Tính thuần túy, không in - để Thượng Trí gọi lại dùng chung."""
    benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
    if not os.path.isdir(benh_nhan):
        return []

    phat_hien = []  # [(rel_path, so_dong, ten, giai_thich, dong_ma), ...]
    for root, dirs, files in os.walk(benh_nhan):
        dirs[:] = [
            d for d in dirs
            if d not in cfg.TA_KHI_DIRS
            and not cfg.la_thu_muc_trinh_duyet(os.path.join(root, d))
        ]
        for ten_file in files:
            # Bỏ qua chính module này - chuỗi các mẫu regex viết ra tự
            # khớp với chính nó (vd dòng chứa r"shell\s*=\s*True" bị chính
            # mẫu shell=True bắt trúng), phát hiện khi chạy thử trên
            # OKA_System.
            if ten_file == "ve_khi_bao_ve.py":
                continue
            duoi = os.path.splitext(ten_file)[1].lower()
            if duoi not in cfg.CAC_DUOI_HO_TRO:
                continue
            full_path = os.path.join(root, ten_file)
            if cfg.la_file_sinh_tu_dong(full_path):
                continue

            if duoi == ".py":
                mau_ngon_ngu = MAU_PY
            elif duoi in (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"):
                mau_ngon_ngu = MAU_JS
            else:
                continue

            rel = os.path.relpath(full_path, benh_nhan)
            for so_dong, ten, giai_thich, dong_ma in _quet_file(full_path, mau_ngon_ngu):
                phat_hien.append((rel, so_dong, ten, giai_thich, dong_ma))

    return phat_hien


def ke_lai(phat_hien, gioi_han_hien=15):
    """Định dạng thành các dòng nhận định SUY ĐOÁN cho Thượng Trí."""
    if not phat_hien:
        return []

    theo_loai = {}
    for rel, so_dong, ten, giai_thich, dong_ma in phat_hien:
        theo_loai.setdefault(ten, []).append((rel, so_dong, giai_thich, dong_ma))

    dong = [
        f"🛡️ VỆ KHÍ: {len(phat_hien)} dấu hiệu bảo mật đáng chú ý "
        f"({len(theo_loai)} loại) - quét bằng mẫu regex, KHÔNG phân tích luồng "
        f"dữ liệu thật, nên có thể có báo động giả. Tự kiểm tra từng chỗ trước khi sửa:"
    ]
    da_hien = 0
    for ten, ds in sorted(theo_loai.items(), key=lambda x: -len(x[1])):
        vi_du = ds[0]
        dong.append(
            f"   • {ten} ({len(ds)} chỗ, vd {vi_du[0]}:{vi_du[1]}) - {vi_du[2]}"
        )
        da_hien += 1
        if da_hien >= gioi_han_hien:
            con_lai = len(theo_loai) - da_hien
            if con_lai > 0:
                dong.append(f"   … và {con_lai} loại khác chưa liệt kê.")
            break

    return ["\n".join(dong)]


class VeKhi:
    def __init__(self):
        xuong_song_trung_uong.dang_ky_nhan_khi("YEU_CAU_SOI_BAO_MAT", self.soi_va_bao_cao)

    def soi_va_bao_cao(self, benh_nhan=None):
        benh_nhan = benh_nhan or cfg.benh_nhan_hien_tai()
        phat_hien = quet(benh_nhan)

        print("\n" + "🛡️ " * 5)
        print(f"🛡️ [VỆ KHÍ]: SOI CỬA NGÕ BẢO MẬT - {os.path.basename(benh_nhan)}")
        print("🛡️ " * 5)

        if not phat_hien:
            print("\n🟢 Không thấy mẫu bảo mật đáng ngờ nào (quét bằng regex, "
                  "không thay được rà soát bảo mật thật).")
        else:
            for van in ke_lai(phat_hien, gioi_han_hien=30):
                print(van)

        print("-" * 60 + "\n")
        xuong_song_trung_uong.phat_khi(
            "GHI_LOG", f"VỆ KHÍ: Đã soi {len(phat_hien)} dấu hiệu bảo mật."
        )
        return phat_hien


ve_khi_trung_uong = VeKhi()
