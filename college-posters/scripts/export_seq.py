"""按发布顺序导出带序号的海报：output/发布序号版/001_清华大学.png，并生成 data/发布顺序.xlsx。
直接复制 output/ 下已渲染好的图（改了数据先跑 render.py 再跑本脚本）。"""
import json
import shutil
import sys
from pathlib import Path

import openpyxl
from openpyxl.styles import Font

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from build_batch_table import BATCHES  # noqa: E402
from order import ORDER  # noqa: E402

DST = ROOT / "output" / "发布序号版"
if DST.exists():
    shutil.rmtree(DST)
DST.mkdir(parents=True)

batch_of = {sid: b for b, ids in BATCHES.items() for sid in ids}
batch_of["bit"] = "第二批（补）"
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "发布顺序"
ws.append(["序号", "校名", "层次", "制作批次", "文件名"])
for c in ws[1]:
    c.font = Font(bold=True)
for i, sid in enumerate(ORDER, 1):
    d = json.loads((ROOT / "data" / f"{sid}.json").read_text(encoding="utf-8"))
    src = ROOT / "output" / f"{d['name']}.png"
    name = f"{i:03d}_{d['name']}.png"
    shutil.copy2(src, DST / name)
    tier = "985" if not batch_of[sid].startswith(("211", "最后")) else "211"
    ws.append([i, d["name"], tier, batch_of[sid], name])
for col, w in zip("ABCDE", (6, 20, 10, 14, 30)):
    ws.column_dimensions[col].width = w
wb.save(ROOT / "data" / "发布顺序.xlsx")
print(len(ORDER), "张 →", DST)
