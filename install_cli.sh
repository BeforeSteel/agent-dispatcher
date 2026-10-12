#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"

WRAPPER_PATH="$BIN_DIR/agents"
ALIAS_PATH="$BIN_DIR/agent-dispatch"

echo "⚙️  Створення системної CLI-команди 'agents' у $BIN_DIR..."

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

echo "✅ Команди 'agents' та 'agent-dispatch' успішно встановлено у $BIN_DIR!"
echo ""
echo "Тепер із будь-якого каталогу доступні команди:"
echo "  agents list             - Стан усіх агентів та мікрододатків"
echo "  agents status <id>      - Детальна діагностика агента"
echo "  agents start <id|all>   - Запуск сервісу або всіх"
echo "  agents stop <id|all>    - Зупинка сервісу або всіх"
echo "  agents restart <id>     - Перезапуск"
echo "  agents logs <id> [-f]   - Перегляд або стрімінг логів"
echo "  agents open <id>        - Відкрити веб-інтерфейс у браузері"
echo "  agents run <id>         - Запуск CLI агента з параметрами"
echo "  agents scan             - Пошук нових мікрододатків у системі"
echo "  agents health           - Стан CPU, RAM, дисків та портів"
echo "  agents web              - Запуск Web-інтерфейсу диспетчера"
echo ""
