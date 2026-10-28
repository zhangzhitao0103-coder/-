"""发布顺序：985 按软科 2026 排序（北理工排在第 13 名中山之后），再 211 各批，军校最后。"""
from build_batch_table import BATCHES  # noqa: E402  (build_batch_table 只在 __main__ 时生成文件)

ORDER = []
for ids in BATCHES.values():
    for sid in ids:
        ORDER.append(sid)
        if sid == "sysu":
            ORDER.append("bit")
