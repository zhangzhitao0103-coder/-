"""把学校数据填进海报模板，导出 PNG。

用法：
  python3 scripts/render.py data/bit.json            # 两版都出
  python3 scripts/render.py data/bit.json --style a  # 只出 A 版
"""
import argparse
import io
import json
from pathlib import Path

import qrcode
import qrcode.image.svg
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "templates"
OUTPUT = ROOT / "output"
CHROMIUM = next(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome"), None)
CHROMIUM = str(CHROMIUM) if CHROMIUM else None
STYLES = {"a": "style_a.html", "b": "style_b.html"}


def qr_svg(url: str) -> str:
    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgPathImage, border=0,
                      error_correction=qrcode.constants.ERROR_CORRECT_M)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    return svg[svg.index("<svg"):]


def render(data_path: Path, styles):
    data = json.loads(data_path.read_text(encoding="utf-8"))
    inject = (f"<script>window.DATA = {json.dumps(data, ensure_ascii=False)};"
              f"window.QR = {json.dumps(qr_svg(data['website']))};</script>")
    OUTPUT.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROMIUM)
        page = browser.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=2)
        for s in styles:
            html = (TEMPLATES / STYLES[s]).read_text(encoding="utf-8").replace("<!--DATA-->", inject)
            tmp = TEMPLATES / f".render_{s}.html"
            tmp.write_text(html, encoding="utf-8")
            page.goto(tmp.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(300)
            overflow = page.evaluate("window.checkOverflow ? window.checkOverflow() : []")
            if overflow:
                print(f"[警告] {data['name']} {s.upper()}版 内容溢出：{overflow}")
            dst = OUTPUT / f"{data['no']:03d}_{data['name']}_{s.upper()}版.png"
            page.locator("#poster").screenshot(path=str(dst))
            tmp.unlink()
            print(dst)
        browser.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="+")
    ap.add_argument("--style", choices=["a", "b"], action="append")
    args = ap.parse_args()
    for d in args.data:
        render(Path(d), args.style or ["a", "b"])
