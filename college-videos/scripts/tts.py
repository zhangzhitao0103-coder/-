"""逐段合成配音，输出 wav 和时间轴 timeline.json。

模型：sherpa-onnx 的 Kokoro 多语种 v1.1（离线运行，103 个音色，中文 3–102）
  下载：https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2
  解压后用 --model 指向目录；音色在脚本 JSON 的 voice_sid 里设置。
"""
import argparse
import json
from pathlib import Path

import numpy as np
import sherpa_onnx
import soundfile as sf

SR = 24000


def load_tts(d: Path):
    cfg = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(
                model=str(d / "model.onnx"), voices=str(d / "voices.bin"), tokens=str(d / "tokens.txt"),
                data_dir=str(d / "espeak-ng-data"), dict_dir=str(d / "dict"),
                lexicon=f"{d / 'lexicon-us-en.txt'},{d / 'lexicon-zh.txt'}"),
            num_threads=4),
        rule_fsts=",".join(str(d / f) for f in ["date-zh.fst", "number-zh.fst", "phone-zh.fst"]),
        max_num_sentences=1)
    return sherpa_onnx.OfflineTts(cfg)


def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if len(idx) == 0:
        return x
    a, b = max(idx[0] - int(0.03 * SR), 0), min(idx[-1] + int(0.08 * SR), len(x))
    return x[a:b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("script")
    ap.add_argument("--model", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    tts = load_tts(Path(args.model))
    lead, gap = 0.25, script.get("gap", 0.3)

    voice, t, timeline = [np.zeros(int(lead * SR), np.float32)], lead, []
    for seg in script["segments"]:
        a = tts.generate(seg["say"], sid=script.get("voice_sid", 80), speed=script.get("voice_speed", 1.0))
        assert a.sample_rate == SR, a.sample_rate
        x = trim(np.asarray(a.samples, np.float32))
        dur = len(x) / SR
        timeline.append({"scene": seg["scene"], "start": round(t, 3), "voice_end": round(t + dur, 3),
                         "sub": seg["sub"], "say": seg["say"]})
        voice += [x, np.zeros(int(gap * SR), np.float32)]
        t += dur + gap
    tail = 2.2  # 片尾留白：音乐收尾
    voice.append(np.zeros(int(tail * SR), np.float32))
    total = t + tail
    for i, s in enumerate(timeline):
        s["end"] = timeline[i + 1]["start"] if i + 1 < len(timeline) else round(total, 3)
    v = np.concatenate(voice)
    v = v / (np.abs(v).max() + 1e-6) * 0.89
    sf.write(out / "voice.wav", v, SR)
    (out / "timeline.json").write_text(json.dumps({"duration": round(total, 3), "scenes": timeline},
                                                  ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"总时长 {total:.1f}s")
    for s in timeline:
        print(f"{s['scene']:8s} {s['start']:6.2f} → {s['end']:6.2f}")


if __name__ == "__main__":
    main()
