# test_mcp_client.py
# KIỂM CHỨNG MCP SERVER BẰNG CLIENT THẬT
#
# Vì sao phải test đường này: transport stdio của MCP dành RIÊNG stdout cho
# JSON-RPC. Một dòng in thừa (đăng ký Đốc Mạch, log GHI_LOG...) là client
# vỡ ngay tin nhắn đầu tiên - bug đã từng bắt được trong dự án này và CHỈ
# lộ khi chạy qua client, không bao giờ lộ khi gọi hàm Python trần.
#
# Kịch bản: khởi động server như một tiến trình con y hệt cách Claude chạy,
# rồi gọi LIÊN TIẾP nhiều tool trong cùng một phiên (đúng tình huống dùng
# thật) — oka_task_context 2 lần với 2 task khác nhau + oka_impact.

import asyncio
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

DU_AN = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(DU_AN, "oka_mcp_server.py")
BENH_NHAN = DU_AN   # khám chính repo OKA


async def main():
    from mcp.client.stdio import stdio_client

    params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER],
    )
    async with stdio_client(params) as (doc, viet):
        async with ClientSession(doc, viet) as s:
            await s.initialize()
            print("✅ 1. Kết nối + initialize OK")

            tools = await s.list_tools()
            ten = sorted(t.name for t in tools.tools)
            print(f"✅ 2. list_tools OK: {len(ten)} tools: {', '.join(ten)}")
            assert "oka_task_context" in ten, "Thiếu tool mới oka_task_context!"

            # Gọi LIÊN TIẾP 3 tool khác nhau trong cùng một phiên -
            # tình huống mà tài liệu mục 3.3 nói chưa từng test.
            kq1 = await s.call_tool(
                "oka_task_context",
                {"project_path": BENH_NHAN, "task": "sua ham boc_tach trong ty_tang_parser"},
            )
            text1 = kq1.content[0].text
            assert "ty_tang_parser.py" in text1, "Chọn nhầm file!"
            print(f"✅ 3. oka_task_context OK (bắt đầu bằng: {text1[:70]!r})")

            kq2 = await s.call_tool(
                "oka_task_context",
                {"project_path": BENH_NHAN, "task": "nhan biet chat memory trong vi_receiver"},
            )
            text2 = kq2.content[0].text
            assert "vi_receiver.py" in text2, "Task 2 chọn sai file!"
            print("✅ 4. Gọi tool thứ 2 liên tiếp OK (không vỡ protocol)")

            kq3 = await s.call_tool(
                "oka_impact",
                {"project_path": BENH_NHAN, "function_name": "boc_tach"},
            )
            text3 = kq3.content[0].text
            assert "boc_tach" in text3
            print("✅ 5. Gọi tool thứ 3 liên tiếp OK")

            print("\n🎉 TẤT CẢ PASS: server chạy ổn qua client MCP thật, "
                  "gọi liên tiếp nhiều tool không lỗi.")


if __name__ == "__main__":
    asyncio.run(main())