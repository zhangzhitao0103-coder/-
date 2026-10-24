# 每日一所好大学 · 985/211 院校海报

面向高中生和家长的朋友圈院校介绍海报，每天一所学校。

## 目录
- `data/<学校>.json`：单个学校的海报字段（模板直接读取）
- `data/字段表_*.xlsx`：字段字典 + 全量内容、海报精简内容、来源与核验状态
- `templates/poster.html`：海报模板（A 版信息图式主体 + B 版深色底栏，不带期数序号）
- `templates/assets/`：主视觉图片（当前北理工为示意插画，正式版替换为实景照片或 AI 插画）
- `scripts/render.py`：数据 → PNG（1080×1920，2 倍清晰度，官网二维码自动生成）
- `output/`：导出的海报

## 出图
```bash
pip install playwright qrcode openpyxl
python3 scripts/render.py data/bit.json        # 输出 output/北京理工大学.png
python3 scripts/render.py data/*.json --seq    # 批量：按传入顺序命名 001_xxx.png
```
内容超出版面时，脚本会打印「内容溢出」警告，按提示删减对应字段即可。
