# oka_mcp_server.py
# Bọc OKA thành MCP server để Claude gọi tool trực tiếp, thay vì bạn phải
# copy-paste Chân Kinh thủ công từ terminal.
#
# Lưu ý quan trọng: nhiều hàm lõi của OKA (bat_mach, do_anh_huong,
# soi_va_bao_cao...) in thẳng ra stdout - đúng cho CLI, nhưng transport
# stdio của MCP dành RIÊNG stdout cho giao thức JSON-RPC. In lẫn vào đó sẽ
# phá hỏng kết nối. Nên mọi tool ở đây gom phần in ra bằng
# contextlib.redirect_stdout rồi trả về dưới dạng text, không sửa gì ở các
# module gốc.

import contextlib
import io

from mcp.server.mcpserver import MCPServer

# Phải tắt TRƯỚC khi import bất kỳ module lõi nào bên dưới: mỗi module
# đăng ký (subscribe) vào Đốc Mạch ngay lúc import, và mặc định việc đăng
# ký này tự in "🔗 [ĐỐC MẠCH]..." ra stdout - đúng cho CLI nhưng phá hỏng
# giao thức JSON-RPC của MCP qua stdio (xác nhận bằng test client thật:
# dòng in này khiến client báo lỗi parse JSON ngay tin nhắn đầu tiên).
from doc_mach_bus import xuong_song_trung_uong
xuong_song_trung_uong.im_lang = True

import oka_config as cfg
from ty_tang_parser import ty_tang_trung_uong
from tam_tang_core import tam_tang_trung_uong
from thuong_tri_tong_hop import thuong_tri_trung_uong
from thiet_chan_pulse import thiet_chan_trung_uong
from ve_khi_bao_ve import ve_khi_trung_uong
from can_tang_goc import can_tang_trung_uong
from soi_chat_luong import soi_chat_luong_trung_uong

mcp = MCPServer("oka")


def _capture(fn, *args, **kwargs):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fn(*args, **kwargs)
    return buf.getvalue().strip() or "(không có output)"


def _chuan_hoa_benh_nhan(project_path):
    """OKA đòi benh_nhan phải là đường dẫn TUYỆT ĐỐI đã ĐĂNG KÝ qua
    cfg.chon_benh_nhan - nếu không, tieu_hoa_code() tự tra lại bệnh nhân
    bằng tim_benh_nhan_cua() và ghi ký ức vào một khóa KHÁC với khóa vừa
    truyền vào, khiến đọc lại luôn ra rỗng (bug thật, bắt được khi test
    bằng MCP client thay vì gọi hàm Python trần)."""
    return cfg.chon_benh_nhan(project_path)


def _dam_bao_da_nhai(benh_nhan):
    """Claude không biết phải gõ 'nhai' trước - tự tiêu hóa nếu ký ức
    dự án này còn trống, để mỗi tool tự chứa, không cần bước dọn đường."""
    ky_uc = ty_tang_trung_uong.tai_ky_uc(benh_nhan)
    if not ky_uc.get("files"):
        ty_tang_trung_uong.tieu_hoa_toan_bo(benh_nhan)


@mcp.tool()
def oka_context(project_path: str, keyword: str = "") -> str:
    """Đọc cấu trúc dự án (Chân Kinh) + cảnh báo rủi ro TRƯỚC khi sửa code.
    Luôn gọi tool này đầu tiên khi bắt đầu làm việc với một dự án.
    keyword: chỉ lọc lấy file có chứa từ khóa này (để bỏ trống nếu muốn toàn bộ)."""
    benh_nhan = _chuan_hoa_benh_nhan(project_path)
    _dam_bao_da_nhai(benh_nhan)
    _capture(thuong_tri_trung_uong.tong_hop, benh_nhan)
    chan_kinh = tam_tang_trung_uong.xuat_chan_kinh_cho_ai(benh_nhan, loc=keyword or None)
    so_lieu = tam_tang_trung_uong.do_cong_luc(benh_nhan, chan_kinh, loc=keyword or None)
    return f"{chan_kinh}\n\n{so_lieu}" if so_lieu else chan_kinh


@mcp.tool()
def oka_impact(project_path: str, function_name: str) -> str:
    """Sửa hàm này thì hỏng những đâu? Trả về nơi định nghĩa và mọi nơi gọi tới."""
    benh_nhan = _chuan_hoa_benh_nhan(project_path)
    _dam_bao_da_nhai(benh_nhan)
    return _capture(
        thiet_chan_trung_uong.do_anh_huong,
        {"ten": function_name, "benh_nhan": benh_nhan},
    )


@mcp.tool()
def oka_security_scan(project_path: str) -> str:
    """Soi dấu hiệu bảo mật ở cửa ngõ: secret viết cứng, eval, SQL nối
    chuỗi, TLS tắt xác thực. Quét bằng regex, KHÔNG thay thế rà soát bảo mật thật."""
    benh_nhan = _chuan_hoa_benh_nhan(project_path)
    _dam_bao_da_nhai(benh_nhan)
    return _capture(ve_khi_trung_uong.soi_va_bao_cao, benh_nhan)


@mcp.tool()
def oka_root_cause(project_path: str) -> str:
    """File nào đang bị vá triệu chứng lặp đi lặp lại (sửa cấu trúc nhiều
    lần trong thời gian ngắn) mà chưa chạm gốc."""
    benh_nhan = _chuan_hoa_benh_nhan(project_path)
    return _capture(can_tang_trung_uong.kham_qua_tai, benh_nhan)


@mcp.tool()
def oka_quality_scan(project_path: str) -> str:
    """Soi code trùng lặp (Trùng Ảnh), lớp bọc thừa (Vỏ Rỗng), test bị làm
    yếu thay vì sửa lỗi thật (Giả Khỏi)."""
    benh_nhan = _chuan_hoa_benh_nhan(project_path)
    _dam_bao_da_nhai(benh_nhan)
    return _capture(soi_chat_luong_trung_uong.soi_va_bao_cao, benh_nhan)


if __name__ == "__main__":
    mcp.run(transport="stdio")
