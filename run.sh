#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Перевірка віртуального оточення
if [ ! -d ".venv" ]; then
    echo "📦 Створення віртуального оточення..."
    uv venv .venv 2>/dev/null || python3 -m venv .venv
fi

# Активація
source .venv/bin/activate

# Перевірка flask та psutil
if ! python3 -c "import flask, psutil" 2>/dev/null; then
    echo "⬇️  Встановлення залежностей..."
    if command -v uv &>/dev/null; then
        uv pip install --python .venv/bin/python -r requirements.txt
    else
        pip install -r requirements.txt
    fi
fi

# Якщо передано аргументи — запускаємо cli.py
if [ $# -gt 0 ]; then
    exec python3 cli.py "$@"
else
    # За замовчуванням запускаємо Web Dashboard
    exec python3 cli.py web
fi
