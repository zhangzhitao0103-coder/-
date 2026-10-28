"""实景版：把透明动效层逐帧叠到实拍背景轨 bg.mp4 上，输出无声 MP4 或预览帧。

用法：
  python3 scripts/render_live.py data/zju_script.json --build <构建目录> --out <构建目录>/silent.mp4
  python3 scripts/render_live.py data/zju_script.json --build <构建目录> --preview 2,9,20 --out <目录>
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from render_video import FPS, ROOT, open_page  # noqa: E402

TEMPLATE = ROOT / "templates" / "video_live.html"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--build", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview")
    args = ap.parse_args()
    build, out = Path(args.build), Path(args.out)
    shots = (build / "shots.json").read_text(encoding="utf-8")

    with sync_playwright() as p:
        browser, page, timeline, tmp, _ = open_page(p, Path(args.script), build, TEMPLATE, f"window.SHOTS={shots};")
        try:
            if args.preview:
                out.mkdir(parents=True, exist_ok=True)
                for t in [float(x) for x in args.preview.split(",")]:
                    page.evaluate(f"seek({t})")
                    layer = out / f"layer_{t:05.1f}.png"
                    page.screenshot(path=str(layer), omit_background=True)
                    dst = out / f"frame_{t:05.1f}.png"
                    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(build / "bg.mp4"), "-i", str(layer),
                                    "-filter_complex", "[0:v][1:v]overlay=0:0", "-frames:v", "1", str(dst)], check=True)
                    layer.unlink()
                    print(dst)
                return
            n = int(timeline["duration"] * FPS)
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-i", str(build / "bg.mp4"),
                 "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                 "-filter_complex", "[0:v][1:v]overlay=0:0:shortest=1,format=yuv420p",
                 "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(FPS), str(out)],
                stdin=subprocess.PIPE)
            for i in range(n):
                page.evaluate(f"seek({i / FPS})")
                ff.stdin.write(page.screenshot(type="png", omit_background=True))
                if i % 300 == 0:
                    print(f"{i}/{n}", flush=True)
            ff.stdin.close()
            ff.wait()
            print(out)
        finally:
            browser.close()
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
