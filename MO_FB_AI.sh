#!/bin/bash
# Chạy: bấm đúp file này (macOS: chuột phải > Open, hoặc "Open With > Terminal")
# hoặc gõ ./MO_FB_AI.sh trong terminal. Không cần mở VSCode.
set -e
cd "$(dirname "$0")"

BASE="$(pwd)"
VENV="$BASE/fb_ai_manager/venv"

echo "Đang kiểm tra Python..."
PYTHON_BIN="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON_BIN" ]; then
    echo "[LỖI] Chưa cài Python 3. Vào python.org/downloads để cài."
    read -p "Bấm Enter để đóng..."
    exit 1
fi

if [ ! -f "$VENV/bin/python" ]; then
    echo "Đang tạo môi trường ảo riêng cho tool (lần đầu sẽ hơi lâu)..."
    "$PYTHON_BIN" -m venv "$VENV"
fi

echo "Đang cài thư viện cần thiết (flask, requests) trong môi trường ảo..."
"$VENV/bin/python" -m pip install -q -r "$BASE/fb_ai_manager/requirements.txt"

echo "Đang mở FB AI Manager..."
"$VENV/bin/python" "$BASE/fb_ai_manager/run.py"

read -p "Bấm Enter để đóng..."
