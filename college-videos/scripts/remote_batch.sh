#!/usr/bin/env bash
# 在另一个云会话里渲染一整批实景视频，成片推到 china-universities 的 render/batchNN 分支。
# 用法（在 china-universities 仓库根目录执行）：
#   git clone --depth 1 -b claude/epic-ramanujan-eo7iju https://github.com/zhangzhitao0103-coder/- ../dash
#   bash ../dash/college-videos/scripts/remote_batch.sh 07
set -euo pipefail
B=$1
REPO=$(pwd)
DASH=$(cd "$(dirname "$0")/../.." && pwd)
CV=$DASH/college-videos
WORK=${WORK:-/tmp/render_b$B}
MODEL=$WORK/kokoro-multi-lang-v1_1
mkdir -p "$WORK"

pip install -q sherpa-onnx soundfile scipy playwright qrcode openpyxl >/dev/null 2>&1 || true
if [ ! -f "$MODEL/model.onnx" ]; then
  curl -sSL -o "$WORK/k.tar.bz2" https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/kokoro-multi-lang-v1_1.tar.bz2
  tar xjf "$WORK/k.tar.bz2" -C "$WORK" && rm "$WORK/k.tar.bz2"
fi

cd "$CV"
python3 scripts/gen_live_scripts.py "batches/batch$B.py"
mapfile -t SIDS < <(python3 - "$B" <<'EOF'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("b", f"batches/batch{sys.argv[1]}.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
print("\n".join(m.SCHOOLS))
EOF
)
NAMES=$(for s in "${SIDS[@]}"; do python3 -c "import json;print(json.load(open('../college-posters/data/$s.json'))['name'])"; done)
INC=$(for n in $NAMES; do printf 'videos/%s/*,' "$n"; done)
(cd "$REPO" && git lfs pull --include "${INC%,}")

OUT=$REPO/renders/batch$B
mkdir -p "$OUT"
run() { python3 scripts/make_live.py "data/$1_live_script.json" --repo "$REPO" --model "$MODEL" --build "$WORK/$1" --out "$OUT" > "$WORK/$1.log" 2>&1 && echo "OK $1" || { echo "FAIL $1"; tail -5 "$WORK/$1.log"; }; }
half=$(( (${#SIDS[@]} + 1) / 2 ))
( for s in "${SIDS[@]:0:$half}"; do run "$s"; done ) &
( for s in "${SIDS[@]:$half}"; do run "$s"; done ) &
wait

cd "$REPO"
git checkout -B "render/batch$B"
git add "renders/batch$B"
git -c user.name="Claude" -c user.email="noreply@anthropic.com" commit -q -m "第 $B 批实景版成片与封面" || true
for i in 1 2 3 4; do git push -u origin "render/batch$B" && break || sleep $((2**i)); done
ls "$OUT"
