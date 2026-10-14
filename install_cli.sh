#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

WRAPPER_PATH="$BIN_DIR/agents"
ALIAS_PATH="$BIN_DIR/agent-dispatch"

echo "⚙️  Creating the 'agents' command in $BIN_DIR..."

cat <<EOF > "$WRAPPER_PATH"
#!/usr/bin/env bash
PROJECT_DIR="$DIR"

if [ -f "\$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON_BIN="\$PROJECT_DIR/.venv/bin/python"
elif [ -f "\$PROJECT_DIR/.venv/bin/python3" ]; then
    PYTHON_BIN="\$PROJECT_DIR/.venv/bin/python3"
else
    PYTHON_BIN="\$(which python3)"
fi

exec "\$PYTHON_BIN" "\$PROJECT_DIR/cli.py" "\$@"
EOF

chmod +x "$WRAPPER_PATH"

# Symlink agent-dispatch -> agents
ln -sf "$WRAPPER_PATH" "$ALIAS_PATH"

echo "✅ Installed the 'agents' and 'agent-dispatch' commands in $BIN_DIR"
echo ""
echo "Available commands:"
echo "  agents list             - State of all agents and micro-apps"
echo "  agents status <id>      - Detailed agent diagnostics"
echo "  agents start <id|all>   - Start one service or all of them"
echo "  agents stop <id|all>    - Stop one service or all of them"
echo "  agents restart <id>     - Restart"
echo "  agents logs <id> [-f]   - Show or follow logs"
echo "  agents open <id>        - Open the web interface in a browser"
echo "  agents run <id>         - Run a CLI agent with arguments"
echo "  agents scan             - Discover new micro-apps"
echo "  agents health           - CPU, RAM, disk and network status"
echo "  agents web              - Start the web dashboard"
echo ""
