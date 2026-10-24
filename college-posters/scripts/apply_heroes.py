"""把 templates/assets/photos/ 里的实景照片或 AI 插画换进海报并重新出图。

文件名用学校 id（见 data/主视觉清单.xlsx），如 thu.jpg。没有图片的学校保留示意插画。
用法：python3 scripts/apply_heroes.py
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "templates" / "assets" / "photos"

changed = []
for img in sorted(PHOTOS.glob("*")):
    if img.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        continue
    data = ROOT / "data" / f"{img.stem}.json"
    if not data.exists():
        print(f"[跳过] {img.name}：没有对应的学校数据")
        continue
    d = json.loads(data.read_text(encoding="utf-8"))
    d["hero"] = f"assets/photos/{img.name}"
    data.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    changed.append(str(data))
if changed:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "render.py"), *changed], check=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / "build_hero_list.py")], check=True)
print(f"已替换 {len(changed)} 所")
