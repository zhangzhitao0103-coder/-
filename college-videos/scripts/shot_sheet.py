"""素材体检：对一所学校的全部素材做镜头切分，输出镜头表和带标号的缩略图总表，供挑选镜头。

用法：python3 scripts/shot_sheet.py <学校素材目录> --out <输出目录>
素材按文件名排序编号为 c1、c2、c3……，与口播稿 sources 对应。
"""
import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"


def probe(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height:format=duration",
                          "-of", "json", str(f)], capture_output=True, text=True).stdout
    j = json.loads(out)
    return j["streams"][0]["width"], j["streams"][0]["height"], float(j["format"]["duration"])


def cuts(f):
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(f), "-vf", "scale=160:-2,select='gt(scene,0.3)',showinfo",
                          "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [float(x.split(":")[1]) for x in log.split() if x.startswith("pts_time:")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(Path(args.src).glob("*.mp4"))
    font = ImageFont.truetype(FONT, 18)
    info, tiles = {"sources": {}, "shots": {}}, []
    for i, f in enumerate(files, 1):
        code = f"c{i}"
        w, h, d = probe(f)
        info["sources"][code] = {"file": f.name, "w": w, "h": h, "dur": round(d, 2)}
        bounds = [0.0] + cuts(f) + [d]
        shots = [(round(a, 2), round(b, 2)) for a, b in zip(bounds, bounds[1:]) if b - a >= 1.0]
        info["shots"][code] = shots
        for k, (a, b) in enumerate(shots):
            jpg = out / f"{code}_{k:02d}.jpg"
            subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str((a + b) / 2), "-i", str(f), "-frames:v", "1",
                            "-vf", "scale=240:240:force_original_aspect_ratio=decrease,pad=240:240:(ow-iw)/2:(oh-ih)/2", str(jpg)])
            im = Image.open(jpg)
            dr = ImageDraw.Draw(im)
            dr.rectangle((0, 0, 240, 22), fill="black")
            dr.text((3, 1), f"{code}#{k} {a:.1f}-{b:.1f}", fill="yellow", font=font)
            tiles.append(im)
    cols = 8
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 240, rows * 240), "white")
    for k, im in enumerate(tiles):
        sheet.paste(im, ((k % cols) * 240, (k // cols) * 240))
    sheet.save(out / "sheet.jpg", quality=82)
    (out / "shots.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out / "sheet.jpg", sum(len(v) for v in info["shots"].values()), "个镜头",
          {k: f"{v['w']}x{v['h']} {v['dur']}s" for k, v in info["sources"].items()})


if __name__ == "__main__":
    main()
