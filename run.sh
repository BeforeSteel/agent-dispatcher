#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

# Create the virtual environment if needed
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    uv venv .venv 2>/dev/null || python3 -m venv .venv
fi

# Activate it
source .venv/bin/activate

# Install Flask and psutil if they are missing
if ! python3 -c "import flask, psutil" 2>/dev/null; then
    echo "⬇️  Installing dependencies..."
    if command -v uv &>/dev/null; then
        uv pip install --python .venv/bin/python -r requirements.txt
    else
        pip install -r requirements.txt
    fi
fi

# With arguments, run the CLI
if [ $# -gt 0 ]; then
    exec python3 cli.py "$@"
else
    # Without arguments, start the web dashboard
    exec python3 cli.py web
fi
