# 每日一所好大学 · 985/211 院校海报

面向高中生和家长的朋友圈院校介绍海报，每天一所学校。

## 目录
- `data/<学校>.json`：单个学校的海报字段（模板直接读取）
- `data/字段表_*.xlsx`：字段字典 + 全量内容、海报精简内容、来源与核验状态
- `templates/style_a.html`：A 版，信息图式（米色纸张 + 书法标题 + 7 个色块模块）
- `templates/style_b.html`：B 版，栏目卡片式（头图 + 数据条 + 4 个编号栏目）
- `templates/assets/`：主视觉图片（当前北理工为示意插画，正式版替换为实景照片或 AI 插画）
- `scripts/render.py`：数据 → PNG（1080×1920，2 倍清晰度，官网二维码自动生成）
- `output/`：导出的海报

## 出图
```bash
pip install playwright qrcode openpyxl
python3 scripts/render.py data/bit.json            # A、B 两版
python3 scripts/render.py data/bit.json --style a  # 只出 A 版
```
内容超出版面时，脚本会打印「内容溢出」警告，按提示删减对应字段即可。
