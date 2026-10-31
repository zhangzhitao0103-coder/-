"""实景版一键出片：配音 → 背景轨 → 配乐 → 动效叠加 → 混音 → 封面。

用法：python3 scripts/make_live.py data/thu_live_script.json --repo /home/user/china-universities --model <Kokoro目录> \
        --build <构建目录> --out <成片目录>
口播稿里 src_dir 为素材目录（相对 --repo），cover_shot 为封面取帧 [素材代号, 秒]。
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(*cmd):
    print("+", " ".join(map(str, cmd)), flush=True)
    subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--repo", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--build", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    sc = json.loads(Path(args.script).read_text(encoding="utf-8"))
    school = json.loads((Path(args.script).parent / sc["school"]).read_text(encoding="utf-8"))
    src = Path(args.repo) / sc["src_dir"]
    b, out = Path(args.build), Path(args.out)
    b.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    py = sys.executable
    run(py, HERE / "tts.py", args.script, "--model", args.model, "--out", b)
    run(py, HERE / "build_bg.py", args.script, "--build", b, "--src", src)
    run(py, HERE / "audio.py", "--build", b)
    run(py, HERE / "render_live.py", args.script, "--build", b, "--out", b / "silent.mp4")
    mp4 = out / f"{school['name']}_院校介绍_实景版.mp4"
    run("ffmpeg", "-y", "-loglevel", "error", "-i", b / "silent.mp4", "-i", b / "mix.wav", "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", mp4)
    if sc.get("cover_shot"):
        code, t = sc["cover_shot"]
        img = HERE.parent / sc["cover_img"]
        img.parent.mkdir(exist_ok=True)
        run("ffmpeg", "-y", "-loglevel", "error", "-ss", t, "-i", src / sc["sources"][code], "-frames:v", "1", "-q:v", "3", img)
    run(py, HERE / "render_video.py", args.script, "--build", b, "--cover", "--out", out)
    print("DONE", mp4)


if __name__ == "__main__":
    main()
