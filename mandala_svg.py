# mandala_svg.py
# MANDALA - vẽ dự án thành sơ đồ tâm-vòng, mở bằng trình duyệt.
#
# Ý tưởng lấy từ Mật Tông (Kim Cang Thừa): "thân vi tế chính là Mandala bên
# trong tương ứng với Mandala bên ngoài là vũ trụ" - một vòng tròn nhỏ phản
# chiếu đầy đủ cái toàn thể. Áp vào đây: mỗi CỤM CHỨC NĂNG là một vòng tròn,
# cụm càng lớn vòng càng to; các cụm có gọi qua lại nhau thì nối bằng đường.
#
# Tự sinh SVG bằng chuỗi thuần - KHÔNG cần graphviz/matplotlib/pyvis. Mở
# file .svg bằng bất kỳ trình duyệt nào là xem được, không cần cài gì.

import os
import math
from collections import defaultdict

# Bảng màu dịu, đủ tương phản trên nền tối
MAU_CUM = [
    "#4ade80", "#60a5fa", "#f472b6", "#fbbf24",
    "#a78bfa", "#22d3ee", "#fb923c", "#94a3b8",
]
NEN = "#12151a"
CHU = "#e6e9ef"
CHU_MO = "#8b95a5"
VIEN = "#2a323d"


def _thoat(s):
    """Escape ký tự đặc biệt của XML - tên file có thể chứa & < >."""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _lien_ket_giua_cum(cac_cum, hang_xom):
    """Đếm số lần gọi qua lại giữa từng cặp cụm."""
    cum_cua_file = {}
    for i, (_, ds) in enumerate(cac_cum):
        for f in ds:
            cum_cua_file[f] = i

    canh = defaultdict(int)
    for f, ke in hang_xom.items():
        i = cum_cua_file.get(f)
        if i is None:
            continue
        for hx, trong_so in ke.items():
            j = cum_cua_file.get(hx)
            if j is None or j == i:
                continue
            canh[(min(i, j), max(i, j))] += trong_so
    return canh


def ve_mandala(cac_cum, hang_xom, ten_du_an, duong_dan_ra,
               rong=1100, cao=820):
    """Sinh file SVG. Trả về đường dẫn đã ghi."""
    if not cac_cum:
        return None

    tam_x, tam_y = rong / 2, cao / 2 + 20
    ban_kinh_vong = min(rong, cao) * 0.32

    # Cụm lớn nhất nằm giữa, còn lại xếp đều quanh vòng
    lon_nhat = max(len(ds) for _, ds in cac_cum)
    vi_tri = []
    for i, (_, ds) in enumerate(cac_cum):
        if i == 0:
            vi_tri.append((tam_x, tam_y))
        else:
            goc = 2 * math.pi * (i - 1) / max(1, len(cac_cum) - 1) - math.pi / 2
            vi_tri.append((tam_x + ban_kinh_vong * math.cos(goc),
                           tam_y + ban_kinh_vong * math.sin(goc)))

    canh = _lien_ket_giua_cum(cac_cum, hang_xom)
    manh = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{rong}" height="{cao}" '
        f'viewBox="0 0 {rong} {cao}" font-family="Segoe UI, sans-serif">',
        f'<rect width="{rong}" height="{cao}" fill="{NEN}"/>',
        f'<text x="{rong/2}" y="42" fill="{CHU}" font-size="23" font-weight="600" '
        f'text-anchor="middle">🌿 Mandala dự án — {_thoat(ten_du_an)}</text>',
        f'<text x="{rong/2}" y="68" fill="{CHU_MO}" font-size="12.5" '
        f'text-anchor="middle">Mỗi vòng là một cụm chức năng · đường nối = số lần '
        f'gọi qua lại · vòng to = nhiều file</text>',
    ]

    # Vẽ đường nối TRƯỚC để nằm dưới các vòng tròn
    if canh:
        manh_nhat = max(canh.values())
        for (i, j), trong_so in sorted(canh.items(), key=lambda x: x[1]):
            x1, y1 = vi_tri[i]
            x2, y2 = vi_tri[j]
            day = 1 + 5 * (trong_so / manh_nhat)
            mo = 0.18 + 0.5 * (trong_so / manh_nhat)
            manh.append(
                f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" '
                f'stroke="{MAU_CUM[i % len(MAU_CUM)]}" stroke-width="{day:.1f}" '
                f'stroke-opacity="{mo:.2f}"/>'
            )
            gx, gy = (x1 + x2) / 2, (y1 + y2) / 2
            manh.append(
                f'<text x="{gx:.0f}" y="{gy:.0f}" fill="{CHU_MO}" font-size="10.5" '
                f'text-anchor="middle">{trong_so}</text>'
            )

    for i, (ten_cum, ds) in enumerate(cac_cum):
        x, y = vi_tri[i]
        mau = MAU_CUM[i % len(MAU_CUM)]
        r = 28 + 46 * math.sqrt(len(ds) / lon_nhat)

        manh.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.0f}" fill="{mau}" '
            f'fill-opacity="0.16" stroke="{mau}" stroke-width="2"/>'
        )
        manh.append(
            f'<text x="{x:.0f}" y="{y+7:.0f}" fill="{mau}" font-size="21" '
            f'font-weight="700" text-anchor="middle">{len(ds)}</text>'
        )

        # Nhãn tên cụm đặt ngoài vòng, cắt bớt cho khỏi tràn khung
        nhan = ten_cum if len(ten_cum) <= 40 else ten_cum[:38] + "…"
        manh.append(
            f'<text x="{x:.0f}" y="{y + r + 17:.0f}" fill="{CHU}" font-size="12" '
            f'text-anchor="middle">{_thoat(nhan)}</text>'
        )

    manh.append(
        f'<text x="{rong/2}" y="{cao-16}" fill="{VIEN}" font-size="11" '
        f'text-anchor="middle">Sinh bởi OKA_System — không dùng thư viện đồ họa nào</text>'
    )
    manh.append("</svg>")

    with open(duong_dan_ra, "w", encoding="utf-8") as f:
        f.write("\n".join(manh))
    return duong_dan_ra
