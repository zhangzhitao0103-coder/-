"""把学校数据 + 配音时间轴渲染成竖屏视频画面（无声 MP4），或导出若干预览帧。

用法：
  python3 scripts/render_video.py data/bit_script.json --build <配音输出目录> --out output/北京理工大学_无声.mp4
  python3 scripts/render_video.py data/bit_script.json --build <配音输出目录> --preview 2,7,15 --out <目录>
  python3 scripts/render_video.py data/bit_script.json --build <配音输出目录> --cover --out <目录>   # 9:16 与 3:4 封面
"""
import argparse
import io
import json
import subprocess
from pathlib import Path

import qrcode
import qrcode.image.svg
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "video.html"
COVER = ROOT / "templates" / "cover.html"
CHROMIUM = next(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"), None)
CHROMIUM = str(CHROMIUM) if CHROMIUM else None
FPS = 30


def qr_svg(url: str) -> str:
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0,
                      error_correction=qrcode.constants.ERROR_CORRECT_M)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    return svg[svg.index("<svg"):]


def open_page(p, script_path: Path, build: Path, template: Path = TEMPLATE, extra: str = ""):
    script = json.loads(script_path.read_text(encoding="utf-8"))
    school_path = (script_path.parent / script["school"]).resolve()
    school = json.loads(school_path.read_text(encoding="utf-8"))
    timeline = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    # 主视觉等素材沿用海报项目的 templates 目录
    asset_base = Path("..") / school_path.parent.parent.relative_to(ROOT.parent) / "templates"
    inject = (f"<script>window.DATA = {json.dumps(school, ensure_ascii=False)};"
              f"window.TIMELINE = {json.dumps(timeline, ensure_ascii=False)};"
              f"window.QR = {json.dumps(qr_svg(school['website']))};"
              f"window.ASSET_BASE = {json.dumps('../' + asset_base.as_posix() + '/')};{extra}</script>")
    tmp = template.parent / f".render_{template.stem}.html"
    tmp.write_text(template.read_text(encoding="utf-8").replace("<!--DATA-->", inject), encoding="utf-8")
    browser = p.chromium.launch(executable_path=CHROMIUM)
    page = browser.new_page(viewport={"width": 1080, "height": 1920})
    page.goto(tmp.as_uri(), wait_until="networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(500)
    return browser, page, timeline, tmp, school


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--build", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--preview", help="逗号分隔的秒数，只导出这些时间点的 PNG")
    ap.add_argument("--cover", action="store_true", help="导出 9:16 和 3:4 两种封面")
    args = ap.parse_args()
    out = Path(args.out)

    if args.cover:
        out.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as p:
            for tag, h in [("9x16", 1920), ("3x4", 1440)]:
                browser, page, _, tmp, school = open_page(p, Path(args.script), Path(args.build), COVER,
                                                          f"window.COVER_H={h};")
                dst = out / f"{school['name']}_封面_{tag}.jpg"
                page.locator("#cover").screenshot(path=str(dst), type="jpeg", quality=92)
                browser.close()
                tmp.unlink(missing_ok=True)
                print(dst)
        return

    with sync_playwright() as p:
        browser, page, timeline, tmp, _ = open_page(p, Path(args.script), Path(args.build))
        try:
            if args.preview:
                out.mkdir(parents=True, exist_ok=True)
                for t in [float(x) for x in args.preview.split(",")]:
                    page.evaluate(f"seek({t})")
                    page.screenshot(path=str(out / f"frame_{t:05.1f}.png"))
                    print(out / f"frame_{t:05.1f}.png")
                return
            n = int(timeline["duration"] * FPS)
            out.parent.mkdir(parents=True, exist_ok=True)
            ff = subprocess.Popen(
                ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                 "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(out)],
                stdin=subprocess.PIPE)
            for i in range(n):
                page.evaluate(f"seek({i / FPS})")
                ff.stdin.write(page.screenshot(type="jpeg", quality=92))
                if i % 150 == 0:
                    print(f"{i}/{n}", flush=True)
            ff.stdin.close()
            ff.wait()
            print(out)
        finally:
            browser.close()
            tmp.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
