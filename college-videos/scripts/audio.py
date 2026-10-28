"""合成背景音乐和音效，并与配音混音，输出 mix.wav。

背景音乐为脚本现场合成（无版权问题）：112 BPM，C-G-Am-F 进行，
钩子段只有铺底和上升音效，学校揭晓时鼓点进入，天象仪故事段收成半拍，结尾长和弦收尾。
"""
import argparse
import json
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

SR = 44100
BPM = 112
BEAT = 60 / BPM
rng = np.random.default_rng(3)


def note(n):  # MIDI → Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def lp(x, f):
    return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)


def hp(x, f):
    return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)


def add(buf, x, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    x = x[: len(buf) - i]
    buf[i:i + len(x)] += g * x


def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def clap():
    n = int(0.18 * SR)
    return hp(lp(rng.standard_normal(n), 3500), 900) * env(n, 0.002, 0.05)


def hat():
    n = int(0.06 * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.001, 0.015)


def pluck(f, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return x * env(n, 0.003, 0.12)


def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0, 0.004):
            ph = (f * (1 + det) * t) % 1.0
            x += 2 * ph - 1
    x = lp(x / (len(freqs) * 3), 1400)
    a = np.minimum(t / 0.25, 1) * np.minimum((dur - t) / 0.3, 1).clip(0, 1)
    return x * a


def whoosh(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); seg = 512
    for i in range(0, n, seg):
        fc = 400 + 5000 * (i / n)
        out[i:i + seg] = lp(x[max(i - 2048, 0):i + seg], fc)[-len(out[i:i + seg]):]
    return out * np.sin(np.pi * t / dur) ** 2


def pop():
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = 1100 - 500 * t / 0.09
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.03)


def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n); out = np.zeros(n); seg = 1024
    for i in range(0, n, seg):
        out[i:i + seg] = lp(x[max(i - 2048, 0):i + seg], 300 + 6000 * (i / n) ** 2)[-len(out[i:i + seg]):]
    return out * (t / dur) ** 2


def impact():
    k = kick(); n = int(0.6 * SR)
    x = np.zeros(n); x[:len(k)] += 1.2 * k
    x += lp(rng.standard_normal(n), 2500) * env(n, 0.002, 0.18) * 0.6
    return x


PROG = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F


def build(tl, total):
    S = {s["scene"]: s for s in tl["scenes"]}
    bgm = np.zeros(int(total * SR) + SR)
    sfx = np.zeros_like(bgm)
    t0 = S["reveal"]["start"]                       # 鼓点从揭晓开始，对齐小节
    nxt = {a["scene"]: b["start"] for a, b in zip(tl["scenes"], tl["scenes"][1:])}
    story = (S["story"]["start"], nxt["story"]) if "story" in S else (-1, -1)   # 抒情段收成半拍
    end_t = S["ending"]["start"]
    bar = 4 * BEAT
    # 铺底：从 0 开始，按小节换和弦（以 t0 为相位基准）
    first = t0 - bar * np.ceil(t0 / bar)
    b = 0
    t = first
    while t < total:
        chord = PROG[b % 4]
        if t >= end_t:                                # 结尾：一个长和弦收住
            add(bgm, pad([note(n) for n in chord] + [note(chord[0] - 12)], total - t + 0.5), t, 0.55)
            break
        add(bgm, pad([note(n) for n in chord], bar + 0.3), t, 0.45)
        main = t >= t0 - 1e-6
        for k in range(8):                            # 八分音符
            tt = t + k * BEAT / 2
            if tt >= end_t or tt < 0:
                continue
            in_story = story[0] <= tt < story[1]
            arp = chord[[0, 1, 2, 1][k % 4]] + 12
            add(bgm, pluck(note(arp)), tt, 0.22 if main else 0.12)
            if main:
                add(bgm, pluck(note(chord[0] - 24), 0.3), tt, 0.35 if k % 2 == 0 else 0.2)
                if not in_story:
                    if k % 2 == 0:
                        add(bgm, kick(), tt, 0.9)
                    if k in (2, 6):
                        add(bgm, clap(), tt, 0.35)
                    if k % 2 == 1:
                        add(bgm, hat(), tt, 0.25)
                elif k == 0:
                    add(bgm, kick(), tt, 0.6)
        t += bar
        b += 1
    # 音效
    add(sfx, riser(1.6), t0 - 1.6, 0.35)
    add(sfx, impact(), t0, 0.9)
    for s in tl["scenes"][1:]:
        if s["scene"] != "reveal":
            add(sfx, whoosh(), s["start"] - 0.2, 0.45)
    for s in tl["scenes"]:
        for c in s.get("chunks", [])[1:]:
            add(sfx, pop(), c - 0.05, 0.35)
    return bgm, sfx


def chunks(s):
    import re
    lens = [len(re.sub(r"[\s，。、！？：“”+]", "", x)) for x in s["sub"]]
    tot, acc, out = sum(lens), 0, []
    for l in lens:
        out.append(s["start"] + (s["voice_end"] - s["start"]) * acc / tot); acc += l
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", required=True)
    args = ap.parse_args()
    b = Path(args.build)
    tl = json.loads((b / "timeline.json").read_text(encoding="utf-8"))
    for s in tl["scenes"]:
        s["chunks"] = chunks(s)
    S = {s["scene"]: s for s in tl["scenes"]}
    # 数据卡 A+ 盖章、王牌专业落章：加重音
    extra = [S[k]["chunks"][-1] + (0.5 if k == "data" else 0) for k in ("data", "majors") if k in S]

    v, vsr = sf.read(b / "voice.wav", dtype="float32")
    voice = resample_poly(v, SR, vsr) if vsr != SR else v
    total = tl["duration"]
    bgm, sfx = build(tl, total)
    for t in extra:
        add(sfx, impact(), t, 0.5)

    n = int(total * SR)
    voice = np.pad(voice, (0, max(0, n - len(voice))))[:n]
    bgm, sfx = bgm[:n], sfx[:n]
    # 人声出现时压低音乐（侧链闪避）
    w = int(0.05 * SR)
    e = np.sqrt(np.convolve(voice ** 2, np.ones(w) / w, mode="same"))
    duck = 1 - 0.55 * np.clip(e / 0.05, 0, 1)
    duck = np.convolve(duck, np.ones(int(0.15 * SR)) / int(0.15 * SR), mode="same")
    bgm = bgm / (np.abs(bgm).max() + 1e-9)
    fade = np.minimum(1, (n - np.arange(n)) / (1.5 * SR))
    mix = voice * 1.0 + bgm * 0.30 * duck * fade + sfx * 0.5
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.95
    sf.write(b / "mix.wav", mix.astype(np.float32), SR)
    print(b / "mix.wav", f"{n / SR:.1f}s")


if __name__ == "__main__":
    main()
