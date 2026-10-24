"""生成北理工主视觉示意插画（中关村校区主楼风格的扁平插画）。

正式版建议替换为实景照片或 AI 插画：把图片放到 assets/ 并在数据里改 hero 字段即可。
"""
from pathlib import Path

W, H = 1000, 460
out = []
a = out.append

a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
a("""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#cfe6f2"/><stop offset="0.65" stop-color="#eef5ef"/><stop offset="1" stop-color="#f6f1e4"/>
</linearGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#e9e2d3"/><stop offset="1" stop-color="#d6ccb8"/>
</linearGradient>
<linearGradient id="wallDark" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#d9d0bd"/><stop offset="1" stop-color="#c4b8a1"/>
</linearGradient>
<linearGradient id="lawn" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#9cc58a"/><stop offset="1" stop-color="#6fa565"/>
</linearGradient>
<radialGradient id="sun" cx="0.82" cy="0.18" r="0.35">
  <stop offset="0" stop-color="#fff6d8" stop-opacity="0.95"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/>
</radialGradient>
</defs>""")
a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>')
a(f'<rect width="{W}" height="{H}" fill="url(#sun)"/>')

# 远处云与城市剪影
for cx, cy, s in [(150, 70, 1.0), (430, 45, 0.7), (760, 90, 0.9)]:
    a(f'<g fill="#ffffff" opacity="0.85" transform="translate({cx},{cy}) scale({s})">'
      '<ellipse cx="0" cy="0" rx="60" ry="18"/><ellipse cx="35" cy="-12" rx="38" ry="20"/>'
      '<ellipse cx="-30" cy="-8" rx="30" ry="15"/></g>')
for x, w, h in [(20, 60, 120), (85, 40, 90), (880, 50, 130), (935, 55, 100), (150, 35, 70), (830, 40, 80)]:
    a(f'<rect x="{x}" y="{330-h}" width="{w}" height="{h}" fill="#b9c9cf" opacity="0.55"/>')


def windows(x0, y0, cols, rows, cw, ch, gx, gy, color="#5d7f8f"):
    for r in range(rows):
        for c in range(cols):
            x = x0 + c * (cw + gx)
            y = y0 + r * (ch + gy)
            a(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cw}" height="{ch}" rx="1.5" fill="{color}" opacity="0.78"/>')


# 两翼
for side in (-1, 1):
    x = 500 + side * 260 - 170
    a(f'<rect x="{x}" y="190" width="340" height="150" fill="url(#wall)"/>')
    a(f'<rect x="{x-6}" y="182" width="352" height="12" fill="#bfb39b"/>')
    windows(x + 18, 206, 10, 5, 18, 16, 14, 11)
# 中部主体
a('<rect x="380" y="130" width="240" height="210" fill="url(#wallDark)"/>')
a('<rect x="372" y="120" width="256" height="14" fill="#b3a68c"/>')
windows(398, 146, 7, 7, 16, 15, 14, 9)
# 中央塔楼
a('<rect x="450" y="70" width="100" height="62" fill="url(#wall)"/>')
a('<rect x="444" y="62" width="112" height="10" fill="#b3a68c"/>')
windows(464, 82, 3, 2, 18, 14, 10, 10)
a('<rect x="485" y="30" width="30" height="34" fill="#d6ccb8"/>')
a('<polygon points="480,32 500,14 520,32" fill="#9c8f74"/>')
# 旗杆与红旗
a('<rect x="499" y="2" width="2.5" height="16" fill="#6b6b6b"/>')
a('<path d="M501.5,3 q10,4 20,0 v10 q-10,4 -20,0z" fill="#d83a2e"/>')
# 入口与台阶
a('<rect x="455" y="270" width="90" height="70" fill="#cdbfa4"/>')
for i in range(4):
    a(f'<rect x="{468+i*20}" y="282" width="10" height="58" fill="#efe8da"/>')
a('<rect x="440" y="262" width="120" height="10" fill="#a99b80"/>')
for i in range(4):
    a(f'<rect x="{430-i*10}" y="{340+i*5}" width="{140+i*20}" height="5" fill="#e3dccb"/>')

# 草坪、道路
a(f'<path d="M0,345 L{W},345 L{W},{H} L0,{H}z" fill="url(#lawn)"/>')
a(f'<path d="M455,345 L545,345 L640,{H} L360,{H}z" fill="#e8e0cf"/>')
a(f'<path d="M497,345 L503,345 L506,{H} L494,{H}z" fill="#d6ccb8"/>')
# 花坛
a('<ellipse cx="500" cy="405" rx="95" ry="22" fill="#5f8f4e"/>')
for i, col in enumerate(["#e85d4a", "#f2c14e", "#e88aa0", "#f08a3c", "#e85d4a", "#f2c14e", "#e88aa0"]):
    a(f'<ellipse cx="{430+i*23}" cy="{400 + (i%2)*6}" rx="10" ry="6" fill="{col}"/>')


def tree(x, y, s, c1="#4f8a47", c2="#6aa65a"):
    a(f'<g transform="translate({x},{y}) scale({s})">'
      f'<rect x="-4" y="-10" width="8" height="40" fill="#7a5a3c"/>'
      f'<circle cx="0" cy="-30" r="30" fill="{c1}"/><circle cx="-20" cy="-15" r="22" fill="{c2}"/>'
      f'<circle cx="20" cy="-18" r="24" fill="{c2}"/><circle cx="2" cy="-50" r="20" fill="{c2}"/></g>')


for x, y, s in [(40, 345, 1.4), (120, 360, 1.1), (300, 355, 0.9), (700, 355, 0.9), (880, 360, 1.1), (960, 345, 1.4)]:
    tree(x, y, s)
for x, y, s in [(200, 420, 1.2), (800, 420, 1.2)]:
    tree(x, y, s, "#3f7a3c", "#5a9850")
a('</svg>')

dst = Path(__file__).resolve().parent.parent / "templates" / "assets" / "bit_hero.svg"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text("\n".join(out), encoding="utf-8")
print(dst)
