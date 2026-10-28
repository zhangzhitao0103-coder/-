"""按口播时间轴拼接实景镜头，生成 1080×1920 背景轨 bg.mp4（无声）。

镜头写在口播稿每段的 shots 里：{"v": 素材代号, "t": [起, 止]}，同一段内的镜头平分该段时长；
镜头加 "chunk": 字幕句序号 时，画面跟着字幕逐句切换。
- 全屏素材（1080×1920）：铺满画面，带缓慢推镜；原片压的字幕由模板底部字幕带盖住。
- 带边框素材（探校系列 720×1280 绿框）：裁出画面内区，做成卡片放在同一画面的虚化放大背景上；
  单个镜头可用 "crop": [宽, 高, x, y] 改裁切区域。
源镜头不够长时最多放慢到 0.5 倍，再不够就定格最后一帧补齐。

用法：python3 scripts/build_bg.py data/zju_script.json --build <配音输出目录> --src <素材目录>
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

W, H, FPS = 1080, 1920, 30
# 探校系列绿框视频的画面内区（720×1280 源）：去掉边框、底部字幕和右下角装饰
FRAMED_CROP = (620, 825, 50, 25)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    w, h = map(int, out.strip().split(",")[:2])
    return w, h


def shot_filter(framed, src_len, need, zoom_from, zoom_to, crop=FRAMED_CROP):
    speed = min(1.0, max(0.5, src_len / need))       # <1 表示放慢
    pts = f"setpts=PTS/{speed:.4f}"
    z = f"({zoom_from}+({zoom_to}-{zoom_from})*t/{need:.3f})"
    if not framed:
        return (f"[0:v]{pts},fps={FPS},scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"scale=w='{W}*{z}':h='{H}*{z}':eval=frame,crop={W}:{H},"
                f"tpad=stop_mode=clone:stop_duration={need:.3f},trim=end_frame={round(need * FPS)},setsar=1[out]")
    cw, ch, cx, cy = crop
    card_w = 900
    card_h = int(card_w * ch / cw) // 2 * 2
    return (f"[0:v]{pts},fps={FPS},crop={cw}:{ch}:{cx}:{cy},split[a][b];"
            f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=30:2,eq=brightness=-0.12[bg];"
            f"[b]scale=w='{card_w}*{z}':h='{card_h}*{z}':eval=frame,crop={card_w}:{card_h}[card];"
            f"[bg][card]overlay=({W}-{card_w})/2:250,"
            f"tpad=stop_mode=clone:stop_duration={need:.3f},trim=end_frame={round(need * FPS)},setsar=1[out]")


def chunk_starts(scene):
    """与模板一致：按字数比例把配音时长分给各句字幕。"""
    lens = [len(re.sub(r"[\s，。、！？：“”+]", "", x)) for x in scene["sub"]]
    tot, acc, out = sum(lens), 0, []
    for n in lens:
        out.append(scene["start"] + (scene["voice_end"] - scene["start"]) * acc / tot)
        acc += n
    return out


def shot_durations(scene, shots, t0):
    """默认平分；镜头写了 "chunk"（字幕句序号）时，按句切换，同一句内的镜头平分这一句。"""
    if not all("chunk" in sh for sh in shots):
        return [(scene["end"] - t0) / len(shots)] * len(shots)
    cs = chunk_starts(scene)
    bounds = [t0] + cs[1:] + [scene["end"]]
    out = []
    for c in range(len(cs)):
        group = [sh for sh in shots if sh["chunk"] == c]
        out += [(bounds[c + 1] - bounds[c]) / len(group)] * len(group)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--build", required=True)
    ap.add_argument("--src", required=True)
    args = ap.parse_args()
    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    build = Path(args.build)
    tl = json.loads((build / "timeline.json").read_text(encoding="utf-8"))
    segs = {s["scene"]: s for s in script["segments"]}
    src = {k: Path(args.src) / v for k, v in script["sources"].items()}
    sizes = {k: probe(p) for k, p in src.items()}

    parts, plan = [], []
    tmp = build / "shots"
    tmp.mkdir(exist_ok=True)
    n = 0
    clock = 0.0       # 理论时间
    frame = 0         # 已排好的整帧数：每个镜头按整帧切，避免误差累积导致画面与字幕错位
    for i, scene in enumerate(tl["scenes"]):
        shots = segs[scene["scene"]]["shots"]
        t0 = 0 if i == 0 else scene["start"]                      # 第一段从 0 秒起，补上配音前的留白
        durs = shot_durations(scene, shots, t0)
        for k, (sh, d) in enumerate(zip(shots, durs)):
            clock += d
            frames = round(clock * FPS) - frame
            frame += frames
            each = frames / FPS
            a, b = sh["t"]
            framed = sizes[sh["v"]] != (W, H)
            zf, zt = (1.0, 1.07) if k % 2 == 0 else (1.07, 1.0)   # 推拉交替
            out = tmp / f"{n:03d}.mp4"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(a), "-t", str(b - a), "-i", str(src[sh["v"]]),
                            "-filter_complex", shot_filter(framed, b - a, each, zf, zt, tuple(sh.get("crop", FRAMED_CROP))), "-map", "[out]", "-an", "-frames:v", str(frames),
                            "-c:v", "libx264", "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", str(out)], check=True)
            parts.append(out)
            plan.append({"scene": scene["scene"], "src": sh["v"], "t": sh["t"], "dur": round(each, 4),
                         "framed": framed, "tag": sh.get("tag", "")})
            n += 1
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-c", "copy", str(build / "bg.mp4")], check=True)
    # 镜头计划交给动效模板（地点标签、卡片位置）
    t = 0.0
    for p in plan:
        p["start"] = round(t, 3)
        t += p["dur"]
    (build / "shots.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(build / "bg.mp4", f"{len(parts)} 个镜头")


if __name__ == "__main__":
    main()
