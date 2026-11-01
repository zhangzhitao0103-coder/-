"""按批次配置生成实景版口播稿：历史、排名、选科等从海报数据自动生成，钩子、校园、镜头等写在批次配置里。

用法：python3 scripts/gen_live_scripts.py batches/batch01.py
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTERS = ROOT.parent / "college-posters" / "data"
DIG = "零一二三四五六七八九"


def zh_int(n):
    n = int(n)
    if n < 10:
        return DIG[n]
    if n < 20:
        return "十" + (DIG[n % 10] if n % 10 else "")
    if n < 100:
        return DIG[n // 10] + "十" + (DIG[n % 10] if n % 10 else "")
    h, r = divmod(n, 100)
    if r == 0:
        return DIG[h] + "百"
    return DIG[h] + "百" + ("零" + DIG[r] if r < 10 else zh_int(r) if r >= 20 else "一" + zh_int(r))


def zh_year(y):
    return "".join(DIG[int(c)] for c in str(y))


def say_tags(s):
    return s.replace("985", "九八五").replace("211", "二一一").replace("C9", "C九")


def sh(v, a, b, **kw):
    return {"v": v, "t": [a, b], **kw}


def build(sid, c, videos_root):
    d = json.loads((POSTERS / f"{sid}.json").read_text(encoding="utf-8"))
    R = {r["label"]: r for r in d["rankings"]}
    short = c.get("short", d["short"])
    tags = d["tags"]
    extra_tag = next((t for t in tags if t.startswith("C9")), None)
    extra = "C9联盟成员" if extra_tag else c.get("reveal_extra", tags[-1])
    segs = []
    hook = c["hook"]
    segs.append({"scene": "hook", "sub": c.get("hook_sub", [hook[0] + hook[1], hook[2] if len(hook) > 2 else "", "你知道是哪所吗？"]),
                 "say": c["hook_say"]})
    if extra == "国防七子":
        extra += "之一"
    level = "、".join(t for t in tags if t in ("985", "211", "双一流"))
    segs.append({"scene": "reveal", "sub": [f"{d['name']}！", level, extra],
                 "say": f"{d['name']}！{say_tags(level)}，{say_tags(extra)}。"})
    hist = c.get("history", d["history"])
    segs.append({"scene": "history", "sub": [f"{y}年 {t}" for y, t in hist],
                 "say": "，".join(f"{zh_year(y)}年，{t}" for y, t in hist) + "。"})
    data_sub, data_say = [], []
    r0 = R.get("软科中国大学排名") or next((r for r in d["rankings"] if r["label"].startswith("软科") and "世界" not in r["label"]), None)
    if r0:
        data_sub.append(f"{r0['label']} 第{r0['value']}")
        data_say.append(f"{r0['label']}第{zh_int(r0['value'])}")
    qs = R.get("QS世界大学排名")
    if qs and qs["value"].isdigit():
        data_sub.append(f"QS世界大学排名 第{qs['value']}")
        data_say.append(f"世界大学排名第{zh_int(qs['value'])}")
    df = R.get("国家双一流建设学科")
    if df:
        data_sub.append(f"{df['value']}个学科入选国家双一流")
        data_say.append(f"{zh_int(df['value'])}个学科入选国家双一流")
    m = re.search(r"(\d+)个学科", d["eval_note"])
    if m:
        data_sub.append(f"还有{m.group(1)}个A+学科")
        data_say.append(f"还有{zh_int(m.group(1))}个A加学科")
    elif "A+" in d["eval_note"]:
        data_sub.append(d["eval_note"].replace(" 学科评估 A+", " 学科评估A+"))
        data_say.append(d["eval_note"].replace(" 学科评估 A+", "，学科评估，A加").replace("A+", "A加"))
    segs.append({"scene": "data", "sub": data_sub, "say": "，".join(data_say) + "！"})
    mj = c["majors"]
    segs.append({"scene": "majors", "sub": ["、".join(mj[:3]), "、".join(mj[3:]), f"{c['majors_tag'].replace(' · ', '与')} 是金字招牌"],
                 "say": f"{'、'.join(mj[:3])}，{'、'.join(mj[3:])}，{c['majors_tag'].replace(' · ', '与')}，是它的金字招牌。"})
    segs.append({"scene": "campus", "sub": c["campus_sub"], "say": c["campus_say"]})
    al = [a[0] for a in c.get("alumni", d["alumni"])[:2]]
    if "rate_sub" not in c:   # 没有可核实的比例数据：改说主要去向
        dirs = "、".join(d["career"]["directions"][:2])
        c = {**c, "rate_sub": f"主要去向：{dirs}", "rate_say": f"毕业生主要去向，{dirs}"}
    if c.get("people_sub"):   # 没有可核实校友时，前两句由配置给出
        segs.append({"scene": "people", "sub": c["people_sub"] + [c["rate_sub"]], "say": f"{c['people_say']}，{c['rate_say']}。"})
    else:
        segs.append({"scene": "people", "sub": ["、".join(al), c.get("alumni_verb", "都曾在这里求学"), c["rate_sub"]],
                     "say": f"{'、'.join(al)}，{c.get('alumni_verb', '都曾在这里求学')}，{c['rate_say']}。"})
    req = d["subject_req"][0][1]
    segs.append({"scene": "fit", "sub": [f"{c['fit'][0]}、{c['fit'][1]}", f"{c['fit'][2]}？", f"选科要选：{req}"],
                 "say": f"{c['fit'][0]}、{c['fit'][1]}、{c['fit'][2]}？选科要选，{req.replace(' + ', '加')}。"})
    a, b = d["motto"].split()
    label = d.get("motto_label") or "校训"
    motto_sub, motto_say = (a + b, a + b) if len(a + b) <= 4 else (f"{a} {b}", f"{a}，{b}")
    segs.append({"scene": "ending", "sub": [motto_sub, f"这是{short}的{label}", f"目标{short}", "从今天的每一道题开始！"],
                 "say": f"{motto_say}，这是{short}的{label}。目标{short}，从今天的每一道题开始！"})
    for s in segs:
        s["shots"] = c["shots"][s["scene"]]
    src_dir = Path(videos_root) / d["name"]
    sources = {f"c{i}": p.name for i, p in enumerate(sorted(src_dir.glob("*.mp4")), 1)}
    return {"school": f"../../college-posters/data/{sid}.json", "theme": c["theme"], "voice_sid": 80, "voice_speed": 1.38, "gap": 0.32,
            "sources": sources, "src_dir": f"videos/{d['name']}", "framed_sources": c.get("framed_sources", []),
            "hook": hook, "history": hist, "majors": mj, "majors_tag": c["majors_tag"], "fit": c["fit"], "credit_tag": "实景画面", "alumni": c.get("alumni"),
            "footage_credit": c.get("footage_credit", f"部分画面来源：{d['name']}官方及公开视频"),
            "cover_hook": c["cover_hook"], "cover_img": f"assets/{sid}_cover.jpg", "cover_shot": c["cover_shot"], "segments": segs}


if __name__ == "__main__":
    spec = importlib.util.spec_from_file_location("batch", sys.argv[1])
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    for sid, c in mod.SCHOOLS.items():
        out = build(sid, c, mod.VIDEOS)
        (ROOT / "data" / f"{sid}_live_script.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(sid, len(out["sources"]), "条素材", sum(len(s["shots"]) for s in out["segments"]), "个镜头")
