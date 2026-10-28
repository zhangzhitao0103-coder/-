# 高考择校 · 名校速览：院校介绍短视频

竖屏 1080×1920、30fps、约 60 秒，面向视频号。画面、配音、背景音乐全部由脚本生成，和海报项目共用学校数据（`../college-posters/data/*.json`）。

## 目录
- `data/<学校>_script.json`：分镜口播稿（每段的字幕 `sub` 和朗读文本 `say`，数字写成汉字保证读音准确）
- `templates/video.html`：9 个场景的动效模板（钩子 → 揭晓 → 历史 → 数据 → 专业 → 故事 → 校友深造 → 适合谁 → 校训片尾）
- `templates/cover.html`：封面（9:16 与 3:4）
- `scripts/tts.py`：离线 AI 配音（sherpa-onnx + Kokoro 中文音色），生成 `voice.wav` 和时间轴
- `scripts/audio.py`：现场合成背景音乐与音效（无版权问题），人声出现时自动压低音乐
- `scripts/render_video.py`：按时间轴逐帧渲染画面；`--preview` 导出预览帧，`--cover` 导出封面
- `output/`：成片与封面
- `视频号发布文案*.md`：标题、简介、话题、评论区互动

## 实景版（有实拍素材的学校）
在动效版基础上，底层换成实拍镜头，动效层透明叠加。示例：`data/zju_script.json`（浙江大学）。
- 口播稿每段加 `shots`：`{"v": 素材代号, "t": [起, 止]}`，可选 `"chunk"`（跟随第几句字幕切换）、`"tag"`（地点标签）、`"crop"`（带边框素材的裁切区域）
- `sources` 写素材文件名，`--src` 指向素材目录；`theme` 设主题色；`cover_hook` / `cover_img` 定制封面
- 原片自带字幕由模板底部的实色字幕带遮住；带绿框的探校素材自动裁成卡片
```bash
python3 scripts/tts.py data/zju_script.json --model $M --out $B
python3 scripts/build_bg.py data/zju_script.json --build $B --src <素材目录>
python3 scripts/audio.py --build $B
python3 scripts/render_live.py data/zju_script.json --build $B --out $B/silent.mp4
ffmpeg -i $B/silent.mp4 -i $B/mix.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 \
  -ar 48000 -c:a aac -b:a 192k -movflags +faststart -shortest output/浙江大学_院校介绍_实景版.mp4
python3 scripts/render_video.py data/zju_script.json --build $B --cover --out output
```

## 出片
```bash
pip install sherpa-onnx soundfile scipy playwright qrcode
# 配音模型（约 350MB，放在仓库外）：
#   https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2
B=/path/to/build; M=/path/to/kokoro-multi-lang-v1_1
python3 scripts/tts.py data/bit_script.json --model $M --out $B
python3 scripts/audio.py --build $B
python3 scripts/render_video.py data/bit_script.json --build $B --out $B/silent.mp4
ffmpeg -i $B/silent.mp4 -i $B/mix.wav -map 0:v -map 1:a -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 \
  -ar 48000 -c:a aac -b:a 192k -movflags +faststart -shortest output/北京理工大学_院校介绍.mp4
python3 scripts/render_video.py data/bit_script.json --build $B --cover --out output
```
音色在口播稿的 `voice_sid` 里换（Kokoro v1.1：3–57 为女声，58–102 为男声），语速用 `voice_speed` 调到总长约 60 秒。
