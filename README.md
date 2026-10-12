# ⬡ Agent Dispatcher — Диспетчер Агентів та Мікрододатків

Єдина система оркестрації, моніторингу та керування персональними мікрододатками, фоновими сервісами та ШІ-агентами в Linux.

---

## 🎯 Проблема та Призначення

У вашій системі працює кілька окремих мікрододатків (`Example web application`, `Suppliers DB`, `Example command-line tool`, `Ollama`, `Example CLI application RAG` тощо). Раніше кожен із них запускався по-своєму: через окремі bash-скрипти, systemd-юніти, docker-контейнери або специфічні CLI-обгортки.

**Agent Dispatcher** об'єднує всі ці інструменти в єдиний центр керування з двома інтерфейсами:
1. **Етап 1 (CLI):** Повний контроль із командного рядка (`agents` / `agent-dispatch`) з будь-якої точки системи.
2. **Етап 2 (Web UI):** Сучасний темний веб-дашборд (Dark Slate / Tailwind CSS / Lucide) із живим моніторингом ресурсів, логами та керуванням в один клік.

---

## ⚡ Швидкий старт

### 1. Системні CLI команди
Команди `agents` та `agent-dispatch` уже встановлені у `~/.local/bin/` і доступні в будь-якому терміналі:

```bash
# Переглянути стан усіх агентів
agents

# Детальна діагностика конкретного сервісу
agents status example-web-app
agents status example-service
agents status ollama

# Запуск / Зупинка / Перезапуск
agents start example-web-app
agents stop example-web-app
agents restart example-service

# Запуск або зупинка ВСІХ сервісів одразу
agents start all
agents stop all

# Перегляд та стрімінг логів у реальному часі
agents logs example-web-app
agents logs example-web-app -f    # live follow (як tail -f)

# Відкрити веб-інтерфейс додатку у браузері
agents open example-web-app

# Інтерактивний запуск CLI-агента
agents run asr /path/to/audio.mp3

# Сканування дисків та автовиявлення нових мікрододатків
agents scan

# Системні ресурси (CPU, RAM, Disks, Network IPs)
agents health
```

---

## 🌐 Етап 2: Веб-інтерфейс (Web Dashboard)

Веб-інтерфейс диспетчера запускається однією командою:

```bash
agents web
# або з вказанням власного порту:
agents web --port 8800
```

Сервер автоматично виводить адреси доступу:
- **Локально:** `http://localhost:8800`
- **У локальній мережі (LAN):** `http://192.0.2.10:8800`
- **Через Tailscale:** `http://198.51.100.10:8800`

### Можливості Веб-дашборду:
- 📊 **Моніторинг системи:** Live графіки завантаження CPU, RAM, дискового простору та мережевих IP.
- 🎛️ **Картки додатків:** Індикатори стану (🟢 Працює, ⚪ Зупинено, ⚡ CLI Ready, 🔴 Помилка), споживання пам'яті (RSS MB), аптайм, активні порти.
- ▶️ **Керування в 1 клік:** Старт, Стоп, Перезапуск, кнопка швидкого переходу у веб-інтерфейс відповідного додатку.
- 📜 **Вбудований Log Viewer:** Перегляд останніх 50–250 рядків логів із автопрокруткою.
- 🔍 **Автосканер (Scan & Import):** Пошук мікрододатків у папках проєктів (`~/Projects`, `~/Downloads`) та додавання їх у диспетчер в 1 клік.
- ➕ **Ручне додавання:** Зручна форма реєстрації нових проєктів.

---

## 🏗️ Підтримувані типи додатків

Диспетчер уніфікує роботу з різними типами процесів:
1. **`daemon` (Фоновий процес):** 
   - Керування через PID-файл та процес-групу (`SIGTERM` -> `SIGKILL`).
   - Автоматичне перехоплення та ротація stdout/stderr у файл логу.
   - Автоматична детекція та перевірка слухаючих TCP-портів.
   - Приклад: `Example web application` (`example-app`).
2. **`systemd` (Системні або User сервіси):**
   - Інтеграція з `systemctl --user` та `journalctl`.
   - Приклад: `Example user service` (`example.service`), `Ollama` (`ollama.service`).
3. **`docker` (Контейнери):**
   - Інтеграція з Docker engine (статус, старт, стоп, логи контейнера).
   - Приклад: `Example vector database` (`example-vector-db`).
4. **`cli` (Консольні агенти):**
   - Інтерактивний виклик з передачею довільних аргументів.
   - Приклад: `Example command-line tool`, `Google Antigravity` (`agy`), `Claude Code` (`claude`), `Codex` (`codex`).

---

## 📁 Структура проєкту

```
/path/to/agent-dispatcher/
├── dispatcher/
│   ├── __init__.py
│   ├── config.py         # Збереження налаштувань у ~/.config/agent_dispatcher/
│   ├── models.py         # Моделі даних Agent та AgentLiveStatus
│   ├── system_info.py    # Утиліти CPU, RAM, портів, LAN/Tailscale IP
│   ├── detector.py       # Сканер кодових баз на наявність мікрододатків
│   ├── manager.py        # Життєвий цикл: start, stop, restart, logs, inspect
│   └── web_server.py     # Flask API + Web Dashboard
├── templates/
│   └── index.html        # Сучасний UI на Tailwind CSS + Lucide
├── static/
│   └── js/app.js         # Реактивний клієнтський JS з автооновленням
├── cli.py                # Головна консольна точка входу
├── install_cli.sh        # Скрипт встановлення у ~/.local/bin/
├── run.sh                # Запуск дашборду або CLI
├── requirements.txt      # flask, psutil
└── README.md             # Документація
```

---

## ⚙️ Конфігурація

Всі зареєстровані агенти та налаштування зберігаються у стандартних системних директоріях:
- Реєстр агентів: `~/.config/agent_dispatcher/agents.json`
- Налаштування: `~/.config/agent_dispatcher/settings.json`
- PID-файли диспетчера: `~/.local/state/agent_dispatcher/pids/`
- Логи диспетчера: `~/.local/state/agent_dispatcher/logs/`

Ви можете редагувати `agents.json` вручну або через команди `agents add` / `agents remove`.
