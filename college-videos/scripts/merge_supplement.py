"""把原素材与 2026-11-02 补充素材合并成一个只含软链接的素材目录，供第 12 批（11 校重做）使用。

原素材按原顺序排在前面（c1、c2、c3 不变），补充素材依次排在后面（c4、c5……）。
用法：python3 scripts/merge_supplement.py --repo /home/user/china-universities --out /home/user/cu_merged/videos
"""
import argparse
from pathlib import Path

SUPP = "videos/20261102_11校补充"

ap = argparse.ArgumentParser()
ap.add_argument("--repo", required=True)
ap.add_argument("--out", required=True)
a = ap.parse_args()
repo, out = Path(a.repo), Path(a.out)
for sd in sorted(p for p in (repo / SUPP).iterdir() if p.is_dir() and list(p.glob("*.mp4"))):
    dst = out / sd.name
    dst.mkdir(parents=True, exist_ok=True)
    for old in dst.glob("*.mp4"):
        old.unlink()
    files = sorted((repo / "videos" / sd.name).glob("*.mp4")) + sorted(sd.glob("*.mp4"))
    for i, f in enumerate(files, 1):
        (dst / f"{i:02d}_{f.name}").symlink_to(f.resolve())
        print(f"{sd.name} c{i} {f.name}")
