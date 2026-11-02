"""第 12 批：11 校换用 2026-11-02 补充素材重做（上外、海大、南理工、吉大、哈工大、上交、西工大、山大、西北大学、北京地大、福大）。

文案沿用原批次配置，只改镜头（和随镜头变化的校园段字幕）。
素材目录由 scripts/merge_supplement.py 生成：原素材仍是 c1–c3，补充素材接在后面（c4、c5……）。
镜头时间来自补充素材的逐 2.5 秒抽帧总表；带字幕/水印/标签的时段已避开，
避不开的用 crop 裁掉（crop = [宽, 高, x, y]，裁后按卡片显示）。
"""
import copy
import importlib.util
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
VIDEOS = "/home/user/cu_merged/videos"


def sh(v, a, b, **kw):
    return {"v": v, "t": [a, b], **kw}


def _base(batch, sid):
    spec = importlib.util.spec_from_file_location(f"b{batch}", HERE / f"batch{batch}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return copy.deepcopy(m.SCHOOLS[sid])


def F(w, h, x, y):
    return {"mode": "framed", "crop": [w, h, x, y]}


SJ4 = F(1280, 720, 213, 0)   # 上交新年航拍 1706 宽：裁掉两侧竖排建筑标签
CG4 = F(1000, 562, 140, 0)   # 北京地大延时：裁掉左下角标和右下建筑名
OC5 = F(900, 506, 62, 0)     # 海大四校区航拍：裁掉左下校区字幕
JC = F(960, 540, 160, 90)    # 吉大春日航拍：去上下黑边
NJ6 = F(1100, 620, 90, 0)    # 南理工绿色校园：裁掉底部作者水印
SD4 = F(836, 470, 94, 0)     # 山大秋景：只取上部，避开底部歌词字幕
NP5 = F(860, 484, 10, 40)    # 西工大友谊校区：裁掉右侧建筑名
NP6 = F(740, 416, 142, 0)    # 西工大长安校区：只取上部，避开底部讲解字幕
SH4 = F(1100, 620, 40, 50)   # 上外云端航拍：裁掉右侧竖排楼名（第四/第八教学楼等）
V = {"mode": "framed", "crop": [576, 700, 0, 160]}

OVR = {
    "sjtu": ("01", dict(
        cover_shot=["c4", 54.0],
        campus_sub=["湖心小岛 绿树环抱", "红砖钟楼 庄重典雅", "春天 花木扶疏"],
        campus_say="湖心小岛，绿树环抱，红砖钟楼，庄重典雅，春天，花木扶疏。",
        shots={
            "hook": [sh("c4", 30.0, 36.0, **SJ4), sh("c5", 2.6, 8.0)],
            "reveal": [sh("c5", 0.1, 2.4)],
            "history": [sh("c4", 30.0, 34.0, **SJ4), sh("c4", 34.0, 38.0, **SJ4), sh("c4", 60.0, 62.3, **SJ4)],
            "data": [sh("c4", 87.5, 92.0, **SJ4), sh("c4", 92.5, 97.0, **SJ4)],
            "majors": [sh("c4", 17.5, 22.0, **SJ4), sh("c4", 80.0, 84.5, **SJ4)],
            "campus": [sh("c4", 40.0, 44.8, chunk=0, tag="湖心岛", **SJ4), sh("c4", 52.5, 59.5, chunk=1, tag="钟楼", **SJ4),
                       sh("c5", 22.5, 34.0, chunk=2, tag="春日交大")],
            "people": [sh("c4", 62.5, 64.5, **SJ4)],
            "fit": [sh("c5", 10.0, 15.0)],
            "ending": [sh("c5", 17.5, 21.5), sh("c4", 92.5, 99.0, **SJ4)],
        })),
    "shisu": ("10", dict(
        cover_shot=["c4", 64.0],
        shots={
            "hook": [sh("c4", 17.5, 23.5, **SH4), sh("c4", 60.0, 66.0, **SH4)],
            "reveal": [sh("c4", 62.5, 68.0, **SH4)],
            "history": [sh("c4", 4.0, 9.0, **SH4), sh("c4", 10.0, 16.0, **SH4), sh("c4", 25.0, 31.0, **SH4)],
            "data": [sh("c4", 47.5, 54.0, **SH4), sh("c4", 32.5, 39.0, **SH4)],
            "majors": [sh("c4", 40.0, 46.0, **SH4), sh("c4", 55.0, 60.0, **SH4)],
            "campus": [sh("c4", 17.5, 24.0, chunk=0, tag="欧式建筑", **SH4), sh("c4", 32.5, 39.5, chunk=1, tag="校园河道", **SH4),
                       sh("c2", 6.5, 20.0, chunk=2, tag="夜色校园")],
            "people": [sh("c4", 25.0, 31.0, **SH4)],
            "fit": [sh("c4", 67.5, 73.5, **SH4)],
            "ending": [sh("c4", 78.0, 81.5, **SH4), sh("c2", 13.0, 20.0)],
        })),
    "cugb": ("07", dict(
        cover_shot=["c4", 57.0],
        campus_sub=["主楼 古朴庄重", "林荫大道 绿意盎然", "秋天 银杏满径"],
        campus_say="主楼，古朴庄重，林荫大道，绿意盎然，秋天，银杏满径。",
        shots={
            "hook": [sh("c4", 55.0, 59.5, **CG4), sh("c4", 2.5, 4.9, **CG4)],
            "reveal": [sh("c4", 45.0, 47.3, **CG4)],
            "history": [sh("c4", 40.0, 44.5, **CG4), sh("c4", 7.5, 9.8, **CG4), sh("c2", 19.3, 21.2)],
            "data": [sh("c4", 47.5, 50.0, **CG4), sh("c4", 35.0, 39.5, **CG4)],
            "majors": [sh("c4", 10.0, 12.3, **CG4), sh("c2", 17.3, 19.3)],
            "campus": [sh("c4", 0.8, 2.4, chunk=0, tag="主楼", **CG4), sh("c5", 0.1, 2.2, chunk=0),
                       sh("c5", 5.0, 10.0, chunk=1, tag="林荫大道"), sh("c1", 0.1, 15.5, chunk=2, tag="银杏", **V)],
            "people": [sh("c4", 65.0, 69.5, **CG4)],
            "fit": [sh("c4", 50.0, 54.5, **CG4)],
            "ending": [sh("c4", 60.0, 64.5, **CG4), sh("c4", 75.2, 79.5, **CG4)],
        })),
    "ouc": ("04", dict(
        cover_shot=["c5", 35.0],
        campus_sub=["红瓦绿树 欧式建筑群", "崂山脚下 青山环抱", "碧海蓝天 近在眼前"],
        campus_say="红瓦绿树，欧式建筑群，崂山脚下，青山环抱，碧海蓝天，近在眼前。",
        shots={
            "hook": [sh("c5", 32.5, 37.5, **OC5), sh("c5", 52.5, 57.0, **OC5)],
            "reveal": [sh("c5", 12.5, 17.4, **OC5)],
            "history": [sh("c5", 40.0, 45.0, **OC5), sh("c4", 95.0, 98.5), sh("c5", 22.5, 26.5, **OC5)],
            "data": [sh("c4", 2.5, 7.4), sh("c5", 47.5, 52.4, **OC5)],
            "majors": [sh("c5", 57.5, 58.8, **OC5), sh("c5", 17.5, 20.0, **OC5)],
            "campus": [sh("c5", 37.5, 45.0, chunk=0, tag="鱼山校区", **OC5), sh("c4", 2.5, 9.9, chunk=1, tag="崂山校区"),
                       sh("c5", 52.5, 57.4, chunk=2, tag="近海", **OC5)],
            "people": [sh("c5", 45.0, 47.4, **OC5), sh("c5", 22.5, 25.0, **OC5)],
            "fit": [sh("c5", 47.5, 52.4, **OC5)],
            "ending": [sh("c5", 30.0, 34.5, **OC5), sh("c5", 12.5, 17.0, **OC5)],
        })),
    "njust": ("04", dict(
        cover_shot=["c1", 19.3],
        campus_sub=["绿树成荫 宛如森林", "楼宇错落 开阔大气", "建筑掩映在绿荫之间"],
        campus_say="绿树成荫，宛如森林，楼宇错落，开阔大气，建筑掩映在绿荫之间。",
        shots={
            "hook": [sh("c6", 37.5, 42.4, **NJ6), sh("c6", 82.5, 88.0, **NJ6)],
            "reveal": [sh("c1", 0.1, 6.0)],
            "history": [sh("c6", 65.0, 71.0, **NJ6), sh("c6", 72.5, 79.5, **NJ6), sh("c1", 12.0, 18.0)],
            "data": [sh("c6", 82.5, 89.5, **NJ6), sh("c1", 18.0, 24.0)],
            "majors": [sh("c6", 10.0, 16.0, **NJ6), sh("c6", 17.5, 24.5, **NJ6)],
            "campus": [sh("c6", 25.0, 34.5, chunk=0, tag="林间花园", **NJ6), sh("c6", 65.0, 72.0, chunk=1, tag="校园全景", **NJ6),
                       sh("c6", 50.0, 60.0, chunk=2, tag="绿荫环抱", **NJ6)],
            "people": [sh("c6", 42.5, 44.9, **NJ6)],
            "fit": [sh("c6", 45.0, 49.9, **NJ6)],
            "ending": [sh("c6", 90.0, 96.5, **NJ6), sh("c6", 10.0, 16.0, **NJ6)],
        })),
    "jlu": ("03", dict(
        cover_shot=["c4", 115.0],
        campus_sub=["校园中轴 气势恢宏", "鼎新楼 宏伟大气", "运动场上 青春飞扬"],
        campus_say="校园中轴，气势恢宏，鼎新楼，宏伟大气，运动场上，青春飞扬。",
        shots={
            "hook": [sh("c4", 25.0, 31.0, **JC), sh("c4", 112.5, 118.0, **JC)],
            "reveal": [sh("c4", 7.5, 13.5, **JC)],
            "history": [sh("c4", 35.0, 41.0, **JC), sh("c4", 52.5, 58.0, **JC), sh("c4", 80.0, 86.0, **JC)],
            "data": [sh("c4", 86.0, 91.9, **JC), sh("c4", 13.5, 19.5, **JC)],
            "majors": [sh("c4", 40.0, 43.3, **JC), sh("c4", 55.0, 58.5, **JC)],
            "campus": [sh("c4", 65.0, 74.5, chunk=0, tag="校园中轴", **JC), sh("c4", 122.5, 128.5, chunk=1, tag="鼎新楼", **JC),
                       sh("c4", 110.0, 112.4, chunk=2, tag="运动场", **JC)],
            "people": [sh("c4", 66.0, 71.0, **JC)],
            "fit": [sh("c4", 30.0, 34.9, **JC)],
            "ending": [sh("c4", 125.0, 128.5, **JC), sh("c4", 35.0, 40.0, **JC)],
        })),
    "hit": ("01", dict(
        cover_shot=["c4", 62.0],
        campus_sub=["校园建筑 庄重大气", "火箭实物 就陈列在路边", "红色HIT标识 远远可见"],
        campus_say="校园建筑，庄重大气，火箭实物，就陈列在路边，红色HIT标识，远远可见。",
        shots={
            "hook": [sh("c4", 0.1, 6.0), sh("c4", 27.5, 32.0)],
            "reveal": [sh("c4", 60.0, 66.5)],
            "history": [sh("c4", 32.5, 38.0), sh("c4", 12.5, 18.0), sh("c4", 7.5, 12.0)],
            "data": [sh("c4", 38.0, 42.3), sh("c4", 18.0, 21.9)],
            "majors": [sh("c4", 45.0, 50.0), sh("c4", 2.5, 7.0)],
            "campus": [sh("c4", 22.5, 27.0, chunk=0, tag="校园建筑"), sh("c4", 52.5, 58.5, chunk=1, tag="火箭"),
                       sh("c4", 42.5, 50.0, chunk=2, tag="HIT大楼")],
            "people": [sh("c2", 8.4, 13.0)],
            "fit": [sh("c4", 12.5, 17.0)],
            "ending": [sh("c4", 60.0, 66.5), sh("c4", 0.1, 5.0)],
        })),
    "sdu": ("02", dict(
        cover_shot=["c3", 1.5],
        campus_sub=["知新楼 高耸挺拔", "秋天 红叶满园", "楼宇错落 秋色连片"],
        campus_say="知新楼，高耸挺拔，秋天，红叶满园，楼宇错落，秋色连片。",
        shots={
            "hook": [sh("c4", 25.0, 30.5, **SD4), sh("c4", 2.5, 7.0, **SD4)],
            "reveal": [sh("c4", 15.0, 19.9, **SD4)],
            "history": [sh("c4", 0.1, 4.9, **SD4), sh("c4", 5.0, 9.5, **SD4), sh("c4", 12.5, 14.9, **SD4)],
            "data": [sh("c4", 35.0, 39.9, **SD4), sh("c4", 42.5, 44.9, **SD4)],
            "majors": [sh("c4", 45.0, 49.9, **SD4), sh("c4", 50.0, 52.4, **SD4)],
            "campus": [sh("c4", 37.5, 42.4, chunk=0, tag="知新楼", **SD4), sh("c4", 0.1, 4.9, chunk=1, tag="秋日校园", **SD4),
                       sh("c4", 52.5, 59.0, chunk=2, tag="校园全景", **SD4)],
            "people": [sh("c4", 45.0, 49.9, **SD4)],
            "fit": [sh("c4", 22.5, 24.9, **SD4)],
            "ending": [sh("c4", 30.0, 34.9, **SD4), sh("c4", 12.5, 14.9, **SD4)],
        })),
    "fzu": ("07", dict(
        cover_shot=["c4", 3.0],
        campus_sub=["旗山脚下 中轴开阔", "湖光山色 绿意环绕", "红砖建筑 闽派风格"],
        campus_say="旗山脚下，中轴开阔，湖光山色，绿意环绕，红砖建筑，闽派风格。",
        shots={
            "hook": [sh("c4", 12.5, 18.0), sh("c4", 25.0, 31.0)],
            "reveal": [sh("c4", 7.5, 12.4)],
            "history": [sh("c1", 12.0, 18.0), sh("c2", 6.0, 12.0), sh("c3", 0.1, 6.0)],
            "data": [sh("c4", 47.5, 53.0), sh("c4", 60.0, 66.0)],
            "majors": [sh("c3", 6.0, 12.0), sh("c4", 37.5, 43.0)],
            "campus": [sh("c4", 0.1, 7.0, chunk=0, tag="旗山校区"), sh("c4", 72.5, 80.0, chunk=1, tag="湖畔长廊"),
                       sh("c1", 30.0, 37.6, chunk=2, tag="红砖建筑")],
            "people": [sh("c2", 26.0, 34.0)],
            "fit": [sh("c4", 97.5, 103.0)],
            "ending": [sh("c4", 7.5, 12.4), sh("c4", 105.0, 112.0)],
        })),
    "nwu": ("07", dict(
        cover_shot=["c4", 12.0],
        campus_sub=["长安校区 现代开阔", "秋天 层林尽染", "绿树环绕 生机盎然"],
        campus_say="长安校区，现代开阔，秋天，层林尽染，绿树环绕，生机盎然。",
        shots={
            "hook": [sh("c4", 10.0, 15.5), sh("c3", 19.3, 21.7)],
            "reveal": [sh("c4", 5.0, 10.0)],
            "history": [sh("c3", 12.0, 13.9), sh("c3", 21.8, 25.9), sh("c3", 14.4, 16.8)],
            "data": [sh("c3", 16.9, 19.2), sh("c4", 21.0, 25.0)],
            "majors": [sh("c3", 7.0, 11.9), sh("c4", 25.0, 30.9)],
            "campus": [sh("c4", 15.5, 21.5, chunk=0, tag="长安校区"), sh("c3", 14.4, 16.8, chunk=1, tag="秋日校园"), sh("c3", 19.3, 21.7, chunk=1),
                       sh("c3", 21.8, 25.9, chunk=2, tag="绿意校园")],
            "people": [sh("c3", 16.9, 19.2)],
            "fit": [sh("c3", 12.0, 13.9)],
            "ending": [sh("c4", 25.0, 30.9), sh("c3", 0.1, 1.4)],
        })),
    "nwpu": ("02", dict(
        cover_shot=["c5", 30.0],
        campus_sub=["长安校区 开阔大气", "湖畔绿地 静谧安然", "友谊校区 秋色正浓"],
        campus_say="长安校区，开阔大气，湖畔绿地，静谧安然，友谊校区，秋色正浓。",
        shots={
            "hook": [sh("c5", 27.5, 33.0, **NP5), sh("c4", 30.0, 36.0)],
            "reveal": [sh("c1", 5.9, 8.2)],
            "history": [sh("c6", 2.5, 8.5, **NP6), sh("c6", 20.0, 26.0, **NP6), sh("c5", 40.0, 45.0, **NP5)],
            "data": [sh("c6", 32.5, 38.0, **NP6), sh("c6", 52.5, 58.0, **NP6)],
            "majors": [sh("c5", 20.0, 25.5, **NP5), sh("c6", 60.0, 66.0, **NP6)],
            "campus": [sh("c6", 32.5, 39.0, chunk=0, tag="长安校区", **NP6), sh("c4", 37.5, 47.0, chunk=1, tag="湖畔绿地"),
                       sh("c5", 55.0, 62.0, chunk=2, tag="友谊校区", **NP5)],
            "people": [sh("c4", 5.0, 11.0)],
            "fit": [sh("c5", 47.5, 53.0, **NP5)],
            "ending": [sh("c5", 62.0, 66.0, **NP5), sh("c6", 52.5, 58.0, **NP6)],
        })),
}

DROP = {"hit": ["footage_credit"]}   # 哈工大不再用深圳校区航拍，片尾来源改回默认写法

SHIFT = 1.25   # 补充素材的抽帧总表（fps=1/2.5）每格实际取自标注时刻后 1.25 秒，选镜时间整体按此校正


def _shift(c):
    src = Path(VIDEOS) / _NAMES[c["_name"]]
    durs = {}
    for sc in c["shots"].values():
        for x in sc:
            if int(x["v"][1:]) <= 3:      # 原素材 c1–c3 的时间来自镜头切分，不用校正
                continue
            if x["v"] not in durs:
                f = sorted(src.glob("*.mp4"))[int(x["v"][1:]) - 1]
                durs[x["v"]] = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                                                    capture_output=True, text=True).stdout)
            a, b = x["t"]
            x["t"] = [round(a + SHIFT, 2), round(min(b + SHIFT, durs[x["v"]] - 0.1), 2)]
    if int(c["cover_shot"][0][1:]) > 3:
        c["cover_shot"] = [c["cover_shot"][0], c["cover_shot"][1] + SHIFT]


_NAMES = {"sjtu": "上海交通大学", "shisu": "上海外国语大学", "cugb": "中国地质大学（北京）", "ouc": "中国海洋大学", "njust": "南京理工大学",
          "jlu": "吉林大学", "hit": "哈尔滨工业大学", "sdu": "山东大学", "fzu": "福州大学", "nwu": "西北大学", "nwpu": "西北工业大学"}

SCHOOLS = {}
for sid, (batch, ovr) in OVR.items():
    c = _base(batch, sid)
    for k in DROP.get(sid, []):
        c.pop(k, None)
    c.update(copy.deepcopy(ovr))
    c["_name"] = sid
    _shift(c)
    del c["_name"]
    SCHOOLS[sid] = c
