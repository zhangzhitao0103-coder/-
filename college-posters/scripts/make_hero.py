"""批量生成各校主视觉示意插画（扁平风格，按学校标志性建筑选造型）。

正式版建议替换为实景照片或 AI 插画：把图片放到 templates/assets/ 并在数据里改 hero 字段即可。
用法：python3 scripts/make_hero.py            # 生成 HEROES 里全部学校
"""
from pathlib import Path

W, H = 1000, 460
ASSETS = Path(__file__).resolve().parent.parent / "templates" / "assets"

# id: (造型, 主墙色, 屋顶/点缀色, 天空色)
HEROES = {
    "thu": ("gate", "#f1ece2", "#8e9aa3", "#cfe3f0"),          # 二校门
    "pku": ("pagoda", "#8b5a3c", "#3f6f5a", "#d7e8f0"),        # 博雅塔 + 未名湖
    "zju": ("clock", "#b65a45", "#5b4a3f", "#d6e9ef"),         # 之江钟楼
    "sjtu": ("library", "#b5543f", "#6b4a3a", "#d3e6f1"),      # 老图书馆红砖楼
    "fudan": ("twin", "#d9d6cf", "#7f8c96", "#d2e4f2"),        # 光华楼双子楼
    "nju": ("clock", "#9a7b5c", "#466b5a", "#d8e8ee"),         # 北大楼钟楼
    "ustc": ("modern", "#e5e1d6", "#2f6f8f", "#cde3f1"),       # 现代教学楼
    "whu": ("castle", "#e8e0cf", "#3c7a6a", "#dbe8f2"),        # 老斋舍 + 樱花
    "hust": ("modern", "#e3ddd0", "#4f7a54", "#d3e7ee"),       # 森林校园
    "xjtu": ("library", "#c8b79c", "#7a4a3c", "#d7e6f0"),      # 兴庆校区 + 樱花道
    "buaa": ("modern", "#e2e4e8", "#2f5f8f", "#cfe2f3"),       # 新主楼
    "hit": ("clock", "#d8cdb6", "#8a5a3c", "#d6e6f0"),         # 苏式主楼
    "sysu": ("library", "#b8573f", "#4f6b5a", "#d3e7ee"),      # 怀士堂红砖楼
    "seu": ("library", "#d9d2c2", "#3f6f78", "#d4e5f0"),       # 大礼堂
    "scu": ("clock", "#9e5d45", "#3f4f5f", "#d6e8ee"),         # 华西钟楼
    "ruc": ("modern", "#e6e0d4", "#a8463a", "#d6e5f0"),        # 明德楼
    "tongji": ("modern", "#e9e9e6", "#4a6f8f", "#d2e4f2"),     # 文远楼
    "bnu": ("library", "#ddd5c4", "#2f5f8f", "#d4e6f1"),       # 主楼
    "tju": ("twin", "#dcd6cb", "#2f5f8f", "#d2e4f2"),          # 北洋园
    "nankai": ("library", "#c9b79a", "#6b3f5f", "#d7e6f0"),    # 主楼 + 马蹄湖
    "sdu": ("clock", "#c8b08f", "#5a4a6b", "#d6e6f0"),         # 洪家楼老校区
    "nwpu": ("modern", "#e3e4e8", "#2f4f8f", "#cfe2f3"),       # 长安校区
    "cau": ("modern", "#e6e2d2", "#4f7a3f", "#d6eadf"),        # 西校区
    "xmu": ("castle", "#ece4d2", "#b5402f", "#cfe6f2"),        # 嘉庚建筑 + 海
    "jlu": ("library", "#d9cfbd", "#2f5f8f", "#d4e6f1"),       # 鼎新图书馆
    "csu": ("clock", "#b8573f", "#3f5f4f", "#d6e8ee"),         # 湘雅老楼
    "dlut": ("modern", "#e4e2dc", "#2f6f8f", "#cfe3f1"),       # 主楼
    "ecnu": ("library", "#dcd3c2", "#7a3f3f", "#d4e6f1"),      # 丽娃河畔
    "hnu": ("gate", "#efe6d6", "#4a4a4a", "#d8e8ee"),          # 岳麓书院
    "scut": ("library", "#d5c9b0", "#3f6f5a", "#d3e7ee"),      # 五山校区
    "uestc": ("modern", "#e4e6ea", "#2f4f8f", "#cfe2f3"),      # 清水河校区
    "cqu": ("clock", "#c9b18f", "#4f5f6f", "#d6e6f0"),         # A区老楼
    "lzu": ("library", "#d6cbb5", "#3f5f7a", "#d8e8f2"),       # 积石堂
    "neu": ("library", "#d0c3a8", "#2f4f6f", "#d4e6f1"),       # 汉卿会堂
    "ouc": ("castle", "#ece4d2", "#2f6f8f", "#cfe6f2"),        # 鱼山校区 + 海
    "nwafu": ("clock", "#cdbb98", "#4f6f3f", "#d6eadf"),       # 三号教学楼
    "muc": ("gate", "#efe6d6", "#a8463a", "#d8e8ee"),          # 民族风格校门
}


def svg(motif, wall, accent, sky):
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
    a(f"""<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{sky}"/><stop offset="0.65" stop-color="#eef5ef"/><stop offset="1" stop-color="#f6f1e4"/>
</linearGradient>
<linearGradient id="lawn" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#9cc58a"/><stop offset="1" stop-color="#6fa565"/>
</linearGradient>
<radialGradient id="sun" cx="0.82" cy="0.18" r="0.35">
  <stop offset="0" stop-color="#fff6d8" stop-opacity="0.95"/><stop offset="1" stop-color="#fff6d8" stop-opacity="0"/>
</radialGradient>
</defs>""")
    a(f'<rect width="{W}" height="{H}" fill="url(#sky)"/><rect width="{W}" height="{H}" fill="url(#sun)"/>')
    for cx, cy, s in [(150, 70, 1.0), (430, 45, 0.7), (760, 90, 0.9)]:
        a(f'<g fill="#fff" opacity="0.85" transform="translate({cx},{cy}) scale({s})">'
          '<ellipse cx="0" cy="0" rx="60" ry="18"/><ellipse cx="35" cy="-12" rx="38" ry="20"/>'
          '<ellipse cx="-30" cy="-8" rx="30" ry="15"/></g>')

    def windows(x0, y0, cols, rows, cw, ch, gx, gy, color="#5d7f8f"):
        for r in range(rows):
            for c in range(cols):
                a(f'<rect x="{x0 + c * (cw + gx):.1f}" y="{y0 + r * (ch + gy):.1f}" width="{cw}" height="{ch}" '
                  f'rx="1.5" fill="{color}" opacity="0.78"/>')

    def flag(x, y):
        a(f'<rect x="{x}" y="{y}" width="2.5" height="18" fill="#6b6b6b"/>')
        a(f'<path d="M{x + 2.5},{y + 1} q10,4 20,0 v10 q-10,4 -20,0z" fill="#d83a2e"/>')

    if motif == "gate":
        # 白色牌坊式校门：四柱三拱
        a(f'<rect x="330" y="140" width="340" height="205" fill="{wall}" stroke="#d6cfc2" stroke-width="3"/>')
        a(f'<path d="M350,140 Q500,80 650,140z" fill="{wall}" stroke="#d6cfc2" stroke-width="3"/>')
        a(f'<rect x="320" y="132" width="360" height="14" fill="{accent}"/>')
        a('<path d="M455,345 v-110 a45,45 0 0 1 90,0 v110z" fill="#5e6b62"/>')
        for x in (365, 595):
            a(f'<path d="M{x},345 v-80 a20,20 0 0 1 40,0 v80z" fill="#5e6b62"/>')
        for x in (335, 425, 555, 645):
            a(f'<rect x="{x}" y="150" width="20" height="195" fill="#e4ddd0"/>')
        a(f'<rect x="440" y="160" width="120" height="34" rx="3" fill="{accent}" opacity="0.8"/>')
        flag(499, 78)
    elif motif == "pagoda":
        # 十三层密檐塔 + 湖面倒影
        for i in range(13):
            w = 70 - i * 3.6
            y = 330 - i * 20
            a(f'<rect x="{500 - w / 2:.1f}" y="{y - 16}" width="{w:.1f}" height="16" fill="{wall}"/>')
            a(f'<rect x="{500 - w / 2 - 8:.1f}" y="{y - 20}" width="{w + 16:.1f}" height="5" fill="{accent}"/>')
        a('<polygon points="490,72 500,46 510,72" fill="#c9a24a"/>')
    elif motif == "clock":
        # 坡屋顶主楼 + 中央钟楼
        a(f'<rect x="300" y="210" width="400" height="135" fill="{wall}"/>')
        a(f'<polygon points="285,212 500,170 715,212" fill="{accent}"/>')
        windows(320, 232, 12, 3, 16, 22, 15, 14, "#e9e2d3")
        a(f'<rect x="455" y="90" width="90" height="255" fill="{wall}"/>')
        a(f'<polygon points="445,92 500,40 555,92" fill="{accent}"/>')
        a('<circle cx="500" cy="130" r="22" fill="#f6f1e4" stroke="#5b4a3f" stroke-width="3"/>')
        a('<path d="M500,130 v-14 M500,130 h10" stroke="#5b4a3f" stroke-width="3"/>')
        windows(475, 175, 2, 4, 16, 22, 18, 16, "#e9e2d3")
        a('<path d="M480,345 v-40 a20,20 0 0 1 40,0 v40z" fill="#5e4a3a"/>')
    elif motif == "library":
        # 红砖古典楼：三段式 + 中央山花
        a(f'<rect x="250" y="190" width="500" height="155" fill="{wall}"/>')
        a(f'<rect x="240" y="180" width="520" height="14" fill="{accent}"/>')
        a(f'<rect x="410" y="140" width="180" height="205" fill="{wall}"/>')
        a(f'<polygon points="400,142 500,95 600,142" fill="{accent}"/>')
        windows(270, 210, 6, 3, 14, 28, 9, 14, "#f3eadb")
        windows(616, 210, 6, 3, 14, 28, 9, 14, "#f3eadb")
        for i in range(5):
            a(f'<rect x="{428 + i * 34}" y="200" width="12" height="145" fill="#efe6d6"/>')
        a('<path d="M478,345 v-50 a22,22 0 0 1 44,0 v50z" fill="#5a4034"/>')
        flag(499, 76)
    elif motif == "twin":
        # 双子塔楼 + 连廊
        for x in (385, 535):
            a(f'<rect x="{x}" y="70" width="80" height="275" fill="{wall}"/>')
            a(f'<rect x="{x - 4}" y="62" width="88" height="10" fill="{accent}"/>')
            windows(x + 10, 84, 4, 14, 10, 12, 8, 6)
        a(f'<rect x="465" y="250" width="70" height="95" fill="{wall}"/>')
        a(f'<rect x="465" y="244" width="70" height="8" fill="{accent}"/>')
        a('<rect x="480" y="300" width="40" height="45" fill="#5e6b72"/>')
    elif motif == "castle":
        # 依山而建的城堡式建筑群（老斋舍）
        a('<path d="M180,345 Q500,120 820,345z" fill="#7fae7a"/>')
        a(f'<rect x="300" y="215" width="400" height="130" fill="{wall}"/>')
        for i in range(10):
            a(f'<rect x="{300 + i * 40}" y="205" width="22" height="12" fill="{wall}"/>')
        a(f'<rect x="460" y="150" width="80" height="195" fill="{wall}"/>')
        a(f'<polygon points="455,152 500,110 545,152" fill="{accent}"/>')
        windows(318, 235, 13, 3, 14, 20, 15, 16)
        a('<path d="M484,345 v-44 a16,16 0 0 1 32,0 v44z" fill="#5e6b62"/>')
        for x, y in [(120, 330), (230, 345), (770, 345), (880, 330), (330, 380), (670, 380)]:
            a(f'<g transform="translate({x},{y})"><rect x="-4" y="-6" width="8" height="40" fill="#7a5a3c"/>'
              '<circle cx="0" cy="-30" r="30" fill="#f4c6d2"/><circle cx="-20" cy="-14" r="22" fill="#f7d6df"/>'
              '<circle cx="20" cy="-16" r="24" fill="#f2b8c8"/></g>')
    else:  # modern
        a(f'<rect x="270" y="170" width="460" height="175" fill="{wall}"/>')
        a(f'<rect x="270" y="160" width="460" height="12" fill="{accent}"/>')
        a(f'<rect x="440" y="100" width="120" height="245" fill="{wall}"/>')
        a(f'<rect x="440" y="92" width="120" height="10" fill="{accent}"/>')
        a(f'<rect x="458" y="112" width="84" height="150" fill="{accent}" opacity="0.55"/>')
        windows(290, 190, 6, 6, 18, 14, 6, 9)
        windows(586, 190, 6, 6, 18, 14, 6, 9)
        a('<rect x="470" y="290" width="60" height="55" fill="#5e6b72"/>')
        flag(499, 72)

    a(f'<path d="M0,345 L{W},345 L{W},{H} L0,{H}z" fill="url(#lawn)"/>')
    if motif == "pagoda":
        a(f'<ellipse cx="500" cy="405" rx="420" ry="50" fill="#8fbfd0" opacity="0.85"/>')
        a('<rect x="485" y="352" width="30" height="80" fill="#8b5a3c" opacity="0.25"/>')
    else:
        a(f'<path d="M455,345 L545,345 L640,{H} L360,{H}z" fill="#e8e0cf"/>')
    for x, y, s in [(40, 345, 1.4), (120, 360, 1.1), (880, 360, 1.1), (960, 345, 1.4), (200, 420, 1.2), (800, 420, 1.2)]:
        a(f'<g transform="translate({x},{y}) scale({s})"><rect x="-4" y="-10" width="8" height="40" fill="#7a5a3c"/>'
          '<circle cx="0" cy="-30" r="30" fill="#4f8a47"/><circle cx="-20" cy="-15" r="22" fill="#6aa65a"/>'
          '<circle cx="20" cy="-18" r="24" fill="#6aa65a"/><circle cx="2" cy="-50" r="20" fill="#6aa65a"/></g>')
    a("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    for sid, args in HEROES.items():
        dst = ASSETS / f"{sid}_hero.svg"
        dst.write_text(svg(*args), encoding="utf-8")
        print(dst)
