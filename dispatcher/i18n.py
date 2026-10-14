"""Internationalization (i18n) engine for Agent Dispatcher (CLI & Web)."""

import os
from typing import Dict, Any, Optional
from pathlib import Path

# Supported languages
SUPPORTED_LANGUAGES = ["uk", "en", "ru"]
DEFAULT_LANGUAGE = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "uk": {
        # General / App
        "app.title": "Agent Dispatcher",
        "app.subtitle": "Запуск і моніторинг локальних додатків, сервісів і контейнерів",
        "app.version": "v0.1.0",
        
        # Header & Stats
        "stats.cpu": "CPU",
        "stats.ram": "RAM",
        "stats.host": "Хост",
        "stats.gpu": "GPU",
        "stats.vram": "VRAM",
        "stats.temp": "Temp",
        "stats.gpu_tooltip": "Завантаження GPU ядра",
        "stats.vram_tooltip": "Відеопам'ять (VRAM)",
        "stats.temp_tooltip": "Температура GPU",

        # Header Buttons
        "btn.scan": "Сканувати",
        "btn.add": "Додати",
        "btn.refresh": "Оновити стан",
        "btn.start_all": "Старт всі",
        "btn.stop_all": "Стоп всі",
        "btn.theme": "Перемкнути тему (світла/темна)",

        # Tabs & Filters
        "tab.all": "Всі",
        "tab.running": "Активні",
        "tab.web": "Веб-додатки",
        "tab.cli": "CLI Агенти",
        "search.placeholder": "Пошук агента...",

        # Card status
        "status.running": "Працює",
        "status.stopped": "Зупинено",
        "status.ready": "CLI Ready",
        "status.failed": "Помилка",
        "status.missing": "Відсутній",
        
        # Card metrics
        "card.memory": "Пам'ять",
        "card.cpu": "CPU",
        "card.uptime": "Аптайм",
        
        # Card buttons
        "btn.start": "Запустити",
        "btn.stop": "Стоп",
        "btn.restart": "Перезапустити",
        "btn.logs": "Логи",
        "btn.open_ui": "Відкрити інтерфейс",

        # Modals
        "modal.logs.title": "Логи агента",
        "modal.logs.refresh": "Оновити",
        "modal.logs.empty": "Логи порожні.",
        "modal.scan.title": "Сканування системи на наявність мікрододатків",
        "modal.scan.loading": "Пошук мікрододатків у системних директоріях...",
        "modal.scan.empty": "Мікрододатків не знайдено.",
        "modal.scan.registered": "Вже у реєстрі",
        "modal.scan.registered_as": "Вже у реєстрі як {id}",
        "modal.add.title": "Додати новий мікрододаток",
        "modal.add.id": "ID агента (slug)*",
        "modal.add.name": "Назва*",
        "modal.add.desc": "Опис",
        "modal.add.type": "Тип запуску",
        "modal.add.port": "Порт (якщо веб)",
        "modal.add.dir": "Робочий каталог (working dir)",
        "modal.add.cmd": "Команда запуску (start_cmd)",
        "modal.add.cancel": "Скасувати",
        "modal.add.save": "Зберегти",

        # Misc UI strings
        "state.loading": "Завантаження стану агентів...",
        "state.empty": "Жодного агента не знайдено за заданими критеріями.",
        "stats.of": "з",
        "stats.cores": "ядер",
        "modal.logs.loading": "Очікування логів...",
        "modal.logs.lines": "{n} рядків",
        "modal.logs.error": "Помилка завантаження логів: {err}",
        "modal.scan.add": "Додати",
        "modal.scan.error": "Помилка сканування: {err}",
        "modal.add.desc_ph": "Короткий опис функціоналу",
        "modal.add.type.daemon": "daemon (фоновий процес)",
        "modal.add.type.systemd": "systemd юніт",
        "modal.add.type.cli": "cli інструмент",
        "modal.add.type.docker": "docker контейнер",
        "toast.starting": "Запуск {id}...",
        "toast.stopping": "Зупинка {id}...",
        "toast.restarting": "Перезапуск {id}...",
        "toast.batch_running": "Виконується групова дія...",
        "toast.batch_done": "Групову дію виконано!",
        "toast.added": "Додано: {name}",
        "toast.error": "Помилка: {err}",

        # CLI Messages
        "cli.header": "Диспетчер Агентів",
        "cli.active_agents": "активних",
        "cli.cli_tools": "CLI",
        "cli.total": "всього",
        "cli.col.status": "СТАН",
        "cli.col.id": "ID",
        "cli.col.name": "НАЗВА",
        "cli.col.type": "ТИП",
        "cli.col.port": "ПОРТ",
        "cli.col.pid": "PID",
        "cli.col.res": "РЕСУРСИ",
        "cli.commands_hint": "Команди: `agents start <id>`, `agents stop <id>`, `agents logs <id>`, `agents open <id>`",
        "cli.status_agent": "Статус агента",
        "cli.description": "Опис",
        "cli.category": "Категорія",
        "cli.port": "Порт",
        "cli.urls": "Веб-адреси",
        "cli.dir": "Каталог",
        "cli.log_file": "Файл логів",
        "cli.recent_logs": "Останні рядки логу",
        "cli.stopped_state": "ЗУПИНЕНО",
        "cli.running_state": "ПРАЦЮЄ",
        "cli.failed_state": "ПОМИЛКА",
        "cli.ready_state": "ГОТОВИЙ ДО ЗАПУСКУ",

        # CLI messages, help and web server console output
        "cli.empty_registry": "Реєстр порожній. Виконайте `agents scan` для пошуку додатків.",
        "cli.agent_not_found": "Агента '{id}' не знайдено в реєстрі.",
        "cli.start_all": "Масовий запуск усіх фонових сервісів...",
        "cli.start_failed": "Помилка запуску: {msg}",
        "cli.stop_all": "Зупинка всіх активних сервісів...",
        "cli.stop_failed": "Помилка зупинки: {msg}",
        "cli.restarting": "Перезапуск {id}...",
        "cli.logs_title": "Логи: {name} (останні {n} рядків)",
        "cli.logs_follow_title": "Стрім логів: {name} (Ctrl+C для виходу)",
        "cli.logs_waiting": "Файл логів поки що не створено. Очікування...",
        "cli.logs_follow_done": "Стрімінг завершено.",
        "cli.scanning": "Сканування системи на наявність мікрододатків та агентів...",
        "cli.scan_found": "Знайдено нові мікрододатки ({n}):",
        "cli.col.dir": "КАТАЛОГ",
        "cli.scan_add_hint": "Щоб додати знайдений додаток у диспетчер, виконайте:",
        "cli.scan_all_registered": "Всі знайдені мікрододатки вже зареєстровані в диспетчері!",
        "cli.scan_already_count": "Вже зареєстровано в системі: {n} додатків.",
        "cli.already_registered_as": "'{id}' вже зареєстрований як '{existing}'.",
        "cli.prompt_id": "Введіть ID агента (наприклад: my-bot): ",
        "cli.id_empty": "ID не може бути порожнім.",
        "cli.prompt_name": "Введіть назву (наприклад: My Bot Service): ",
        "cli.prompt_dir": "Шлях до каталогу: ",
        "cli.default_desc": "Мікрододаток {name}",
        "cli.health_title": "Системні ресурси ({host})",
        "cli.health_cpu": "Завантаження CPU",
        "cli.health_ram": "Оперативна пам'ять",
        "cli.health_gpu": "Відеокарта ({name})",
        "cli.health_gpu_load": "Завантаження GPU",
        "cli.health_vram": "Відеопам'ять VRAM",
        "cli.health_temp": "Температура",
        "cli.health_power": "Потужність",
        "cli.health_disks": "Дисковий простір",
        "cli.health_disk_line": "Вільних: {free} GB із {total} GB ({percent}% зайнято)",
        "cli.health_net": "Мережеві інтерфейси",
        "cli.lang_current": "Поточна мова",
        "cli.lang_supported": "Підтримуються",
        "cli.lang_switch": "Змінити",
        "cli.lang_unsupported": "Непідтримувана мова: {code}. Доступні: {available}",
        "cli.lang_changed": "Мову інтерфейсу змінено на {code}!",
        "cli.help.description": "⬡ Диспетчер Агентів та Мікрододатків — запуск, контроль та моніторинг",
        "cli.help.lang": "Мова інтерфейсу для цієї команди (uk, en, ru)",
        "cli.help.command": "Команда диспетчера",
        "cli.help.lang_cmd": "Переглянути або змінити мову інтерфейсу (uk, en, ru)",
        "cli.help.lang_code": "Код мови",
        "cli.help.list": "Список усіх агентів та їх стан",
        "cli.help.status": "Детальний статус конкретного агента",
        "cli.help.agent_id": "ID агента",
        "cli.help.agent_id_or_all": "ID агента або 'all'",
        "cli.help.start": "Запустити агента або сервіс (або 'all')",
        "cli.help.stop": "Зупинити агента або сервіс (або 'all')",
        "cli.help.restart": "Перезапустити агента",
        "cli.help.logs": "Переглянути логи агента",
        "cli.help.lines": "Кількість рядків",
        "cli.help.follow": "Стрімінг нових рядків (live follow)",
        "cli.help.open": "Відкрити веб-інтерфейс у браузері",
        "cli.help.run": "Запустити CLI агента з параметрами",
        "cli.help.extra_args": "Аргументи для команди агента",
        "cli.help.scan": "Пошук нових мікрододатків у системі",
        "cli.help.add": "Зареєструвати новий додаток у диспетчер",
        "cli.help.name": "Назва",
        "cli.help.dir": "Каталог проєкту",
        "cli.help.port": "Порт",
        "cli.help.type": "Тип",
        "cli.help.start_cmd": "Команда запуску",
        "cli.help.desc": "Опис",
        "cli.help.remove": "Видалити додаток із реєстру",
        "cli.help.health": "Стан системних ресурсів (CPU, RAM, диски, мережа)",
        "cli.help.web": "Запустити веб-інтерфейс диспетчера",
        "cli.help.web_port": "Порт веб-сервера (за замовчуванням: web_port із налаштувань, інакше 8800)",
        "cli.help.web_host": "Адреса для прослуховування (за замовчуванням: web_host із налаштувань, інакше 127.0.0.1). 0.0.0.0 відкриває дашборд без авторизації для всієї мережі",
        "web.started": "Диспетчер Агентів — Web Dashboard запущено!",
        "web.local": "Локально",
        "web.lan": "У мережі LAN",
        "web.local_only": "Доступний лише з цього комп'ютера. Для віддаленого доступу використовуйте SSH-тунель (див. README).",
        "web.exposed_warning": "УВАГА: дашборд слухає {host} і не має авторизації. Будь-хто, хто може дістатися до цієї адреси, може виконувати команди від вашого користувача.",
        "web.stop_hint": "Натисніть CTRL+C для зупинки сервера.",

        # Agent names and descriptions come from user registrations.
    },
    "en": {
        # General / App
        "app.title": "Agent Dispatcher",
        "app.subtitle": "Run and monitor your local apps, services and containers",
        "app.version": "v0.1.0",
        
        # Header & Stats
        "stats.cpu": "CPU",
        "stats.ram": "RAM",
        "stats.host": "Host",
        "stats.gpu": "GPU",
        "stats.vram": "VRAM",
        "stats.temp": "Temp",
        "stats.gpu_tooltip": "GPU Core Utilization",
        "stats.vram_tooltip": "Video Memory (VRAM)",
        "stats.temp_tooltip": "GPU Temperature",

        # Header Buttons
        "btn.scan": "Scan",
        "btn.add": "Add Agent",
        "btn.refresh": "Refresh",
        "btn.start_all": "Start All",
        "btn.stop_all": "Stop All",
        "btn.theme": "Toggle theme (light/dark)",

        # Tabs & Filters
        "tab.all": "All",
        "tab.running": "Running",
        "tab.web": "Web Apps",
        "tab.cli": "CLI Agents",
        "search.placeholder": "Search agent...",

        # Card status
        "status.running": "Running",
        "status.stopped": "Stopped",
        "status.ready": "CLI Ready",
        "status.failed": "Failed",
        "status.missing": "Missing",
        
        # Card metrics
        "card.memory": "Memory",
        "card.cpu": "CPU",
        "card.uptime": "Uptime",
        
        # Card buttons
        "btn.start": "Start",
        "btn.stop": "Stop",
        "btn.restart": "Restart",
        "btn.logs": "Logs",
        "btn.open_ui": "Open Web UI",

        # Modals
        "modal.logs.title": "Agent Logs",
        "modal.logs.refresh": "Refresh",
        "modal.logs.empty": "Logs are empty.",
        "modal.scan.title": "System Scan for Micro-Applications",
        "modal.scan.loading": "Scanning project directories...",
        "modal.scan.empty": "No micro-applications found.",
        "modal.scan.registered": "Already in registry",
        "modal.scan.registered_as": "Already in registry as {id}",
        "modal.add.title": "Register New Micro-Application",
        "modal.add.id": "Agent ID (slug)*",
        "modal.add.name": "Name*",
        "modal.add.desc": "Description",
        "modal.add.type": "Process Type",
        "modal.add.port": "Port (if web app)",
        "modal.add.dir": "Working Directory",
        "modal.add.cmd": "Start Command (start_cmd)",
        "modal.add.cancel": "Cancel",
        "modal.add.save": "Save",

        # Misc UI strings
        "state.loading": "Loading agent status...",
        "state.empty": "No agents match the current filters.",
        "stats.of": "of",
        "stats.cores": "cores",
        "modal.logs.loading": "Waiting for logs...",
        "modal.logs.lines": "{n} lines",
        "modal.logs.error": "Failed to load logs: {err}",
        "modal.scan.add": "Add",
        "modal.scan.error": "Scan failed: {err}",
        "modal.add.desc_ph": "Short description of what it does",
        "modal.add.type.daemon": "daemon (background process)",
        "modal.add.type.systemd": "systemd unit",
        "modal.add.type.cli": "cli tool",
        "modal.add.type.docker": "docker container",
        "toast.starting": "Starting {id}...",
        "toast.stopping": "Stopping {id}...",
        "toast.restarting": "Restarting {id}...",
        "toast.batch_running": "Running batch action...",
        "toast.batch_done": "Batch action completed!",
        "toast.added": "Added: {name}",
        "toast.error": "Error: {err}",

        # CLI Messages
        "cli.header": "Agent Dispatcher",
        "cli.active_agents": "active",
        "cli.cli_tools": "CLI",
        "cli.total": "total",
        "cli.col.status": "STATE",
        "cli.col.id": "ID",
        "cli.col.name": "NAME",
        "cli.col.type": "TYPE",
        "cli.col.port": "PORT",
        "cli.col.pid": "PID",
        "cli.col.res": "RESOURCES",
        "cli.commands_hint": "Commands: `agents start <id>`, `agents stop <id>`, `agents logs <id>`, `agents open <id>`",
        "cli.status_agent": "Agent Status",
        "cli.description": "Description",
        "cli.category": "Category",
        "cli.port": "Port",
        "cli.urls": "Web URLs",
        "cli.dir": "Directory",
        "cli.log_file": "Log file",
        "cli.recent_logs": "Recent log lines",
        "cli.stopped_state": "STOPPED",
        "cli.running_state": "RUNNING",
        "cli.failed_state": "FAILED",
        "cli.ready_state": "CLI READY",

        # CLI messages, help and web server console output
        "cli.empty_registry": "The registry is empty. Run `agents scan` to discover applications.",
        "cli.agent_not_found": "Agent '{id}' was not found in the registry.",
        "cli.start_all": "Starting all background services...",
        "cli.start_failed": "Start failed: {msg}",
        "cli.stop_all": "Stopping all running services...",
        "cli.stop_failed": "Stop failed: {msg}",
        "cli.restarting": "Restarting {id}...",
        "cli.logs_title": "Logs: {name} (last {n} lines)",
        "cli.logs_follow_title": "Log stream: {name} (Ctrl+C to exit)",
        "cli.logs_waiting": "The log file has not been created yet. Waiting...",
        "cli.logs_follow_done": "Streaming finished.",
        "cli.scanning": "Scanning the system for micro-apps and agents...",
        "cli.scan_found": "New micro-apps found ({n}):",
        "cli.col.dir": "DIRECTORY",
        "cli.scan_add_hint": "To add a discovered app to the dispatcher, run:",
        "cli.scan_all_registered": "All discovered micro-apps are already registered!",
        "cli.scan_already_count": "Already registered: {n} apps.",
        "cli.already_registered_as": "'{id}' is already registered as '{existing}'.",
        "cli.prompt_id": "Enter the agent ID (e.g. my-bot): ",
        "cli.id_empty": "The ID cannot be empty.",
        "cli.prompt_name": "Enter a name (e.g. My Bot Service): ",
        "cli.prompt_dir": "Project directory: ",
        "cli.default_desc": "Micro-app {name}",
        "cli.health_title": "System resources ({host})",
        "cli.health_cpu": "CPU load",
        "cli.health_ram": "Memory",
        "cli.health_gpu": "GPU ({name})",
        "cli.health_gpu_load": "GPU load",
        "cli.health_vram": "VRAM",
        "cli.health_temp": "Temperature",
        "cli.health_power": "Power",
        "cli.health_disks": "Disk space",
        "cli.health_disk_line": "{free} GB free of {total} GB ({percent}% used)",
        "cli.health_net": "Network interfaces",
        "cli.lang_current": "Current language",
        "cli.lang_supported": "Supported",
        "cli.lang_switch": "Switch",
        "cli.lang_unsupported": "Unsupported language: {code}. Available: {available}",
        "cli.lang_changed": "Interface language changed to {code}!",
        "cli.help.description": "⬡ Agent Dispatcher — start, control and monitor your local apps and services",
        "cli.help.lang": "Interface language for this command (uk, en, ru)",
        "cli.help.command": "Dispatcher command",
        "cli.help.lang_cmd": "Show or change the interface language (uk, en, ru)",
        "cli.help.lang_code": "Language code",
        "cli.help.list": "List all agents and their state",
        "cli.help.status": "Show detailed status of one agent",
        "cli.help.agent_id": "Agent ID",
        "cli.help.agent_id_or_all": "Agent ID or 'all'",
        "cli.help.start": "Start an agent or service (or 'all')",
        "cli.help.stop": "Stop an agent or service (or 'all')",
        "cli.help.restart": "Restart an agent",
        "cli.help.logs": "Show agent logs",
        "cli.help.lines": "Number of lines",
        "cli.help.follow": "Follow new lines as they are written",
        "cli.help.open": "Open the agent's web interface in a browser",
        "cli.help.run": "Run a CLI agent with arguments",
        "cli.help.extra_args": "Arguments for the agent's command",
        "cli.help.scan": "Discover new micro-apps on this system",
        "cli.help.add": "Register a new application",
        "cli.help.name": "Name",
        "cli.help.dir": "Project directory",
        "cli.help.port": "Port",
        "cli.help.type": "Type",
        "cli.help.start_cmd": "Start command",
        "cli.help.desc": "Description",
        "cli.help.remove": "Remove an application from the registry",
        "cli.help.health": "Show system resources (CPU, RAM, disks, network)",
        "cli.help.web": "Start the web dashboard",
        "cli.help.web_port": "Web server port (default: web_port from settings, otherwise 8800)",
        "cli.help.web_host": "Address to listen on (default: web_host from settings, otherwise 127.0.0.1). 0.0.0.0 exposes the dashboard, which has no authentication, to your whole network",
        "web.started": "Agent Dispatcher — web dashboard started!",
        "web.local": "Local",
        "web.lan": "LAN",
        "web.local_only": "Reachable from this computer only. For remote access, use an SSH tunnel (see the README).",
        "web.exposed_warning": "WARNING: the dashboard listens on {host} and has no authentication. Anyone who can reach this address can run commands as your user.",
        "web.stop_hint": "Press CTRL+C to stop the server.",

        # Agent names and descriptions come from user registrations.
    },
    "ru": {
        # General / App
        "app.title": "Agent Dispatcher",
        "app.subtitle": "Запуск и мониторинг локальных приложений, сервисов и контейнеров",
        "app.version": "v0.1.0",
        
        # Header & Stats
        "stats.cpu": "CPU",
        "stats.ram": "RAM",
        "stats.host": "Хост",
        "stats.gpu": "GPU",
        "stats.vram": "VRAM",
        "stats.temp": "Temp",
        "stats.gpu_tooltip": "Загрузка GPU ядра",
        "stats.vram_tooltip": "Видеопамять (VRAM)",
        "stats.temp_tooltip": "Температура GPU",

        # Header Buttons
        "btn.scan": "Сканировать",
        "btn.add": "Добавить",
        "btn.refresh": "Обновить",
        "btn.start_all": "Старт все",
        "btn.stop_all": "Стоп все",
        "btn.theme": "Переключить тему (светлая/темная)",

        # Tabs & Filters
        "tab.all": "Все",
        "tab.running": "Активные",
        "tab.web": "Веб-приложения",
        "tab.cli": "CLI Агенты",
        "search.placeholder": "Поиск агента...",

        # Card status
        "status.running": "Работает",
        "status.stopped": "Остановлен",
        "status.ready": "CLI Ready",
        "status.failed": "Ошибка",
        "status.missing": "Отсутствует",
        
        # Card metrics
        "card.memory": "Память",
        "card.cpu": "CPU",
        "card.uptime": "Аптайм",
        
        # Card buttons
        "btn.start": "Запустить",
        "btn.stop": "Стоп",
        "btn.restart": "Перезапуск",
        "btn.logs": "Логи",
        "btn.open_ui": "Открыть интерфейс",

        # Modals
        "modal.logs.title": "Логи агента",
        "modal.logs.refresh": "Обновить",
        "modal.logs.empty": "Логи пусты.",
        "modal.scan.title": "Сканирование системы на наличие микроприложений",
        "modal.scan.loading": "Поиск микроприложений в системных папках...",
        "modal.scan.empty": "Микроприложений не найдено.",
        "modal.scan.registered": "Уже в реестре",
        "modal.scan.registered_as": "Уже в реестре как {id}",
        "modal.add.title": "Добавить новое микроприложение",
        "modal.add.id": "ID агента (slug)*",
        "modal.add.name": "Название*",
        "modal.add.desc": "Описание",
        "modal.add.type": "Тип запуска",
        "modal.add.port": "Порт (если веб)",
        "modal.add.dir": "Рабочая папка (working dir)",
        "modal.add.cmd": "Команда запуска (start_cmd)",
        "modal.add.cancel": "Отмена",
        "modal.add.save": "Сохранить",

        # Misc UI strings
        "state.loading": "Загрузка состояния агентов...",
        "state.empty": "Ни одного агента не найдено по заданным критериям.",
        "stats.of": "из",
        "stats.cores": "ядер",
        "modal.logs.loading": "Ожидание логов...",
        "modal.logs.lines": "{n} строк",
        "modal.logs.error": "Ошибка загрузки логов: {err}",
        "modal.scan.add": "Добавить",
        "modal.scan.error": "Ошибка сканирования: {err}",
        "modal.add.desc_ph": "Краткое описание функционала",
        "modal.add.type.daemon": "daemon (фоновый процесс)",
        "modal.add.type.systemd": "systemd юнит",
        "modal.add.type.cli": "cli инструмент",
        "modal.add.type.docker": "docker контейнер",
        "toast.starting": "Запуск {id}...",
        "toast.stopping": "Остановка {id}...",
        "toast.restarting": "Перезапуск {id}...",
        "toast.batch_running": "Выполняется групповое действие...",
        "toast.batch_done": "Групповое действие выполнено!",
        "toast.added": "Добавлено: {name}",
        "toast.error": "Ошибка: {err}",

        # CLI Messages
        "cli.header": "Диспетчер Агентов",
        "cli.active_agents": "активных",
        "cli.cli_tools": "CLI",
        "cli.total": "всего",
        "cli.col.status": "СТАТУС",
        "cli.col.id": "ID",
        "cli.col.name": "НАЗВАНИЕ",
        "cli.col.type": "ТИП",
        "cli.col.port": "ПОРТ",
        "cli.col.pid": "PID",
        "cli.col.res": "РЕСУРСЫ",
        "cli.commands_hint": "Команды: `agents start <id>`, `agents stop <id>`, `agents logs <id>`, `agents open <id>`",
        "cli.status_agent": "Статус агента",
        "cli.description": "Описание",
        "cli.category": "Категория",
        "cli.port": "Порт",
        "cli.urls": "Веб-адреса",
        "cli.dir": "Каталог",
        "cli.log_file": "Файл логов",
        "cli.recent_logs": "Последние строки лога",
        "cli.stopped_state": "ОСТАНОВЛЕНО",
        "cli.running_state": "РАБОТАЕТ",
        "cli.failed_state": "ОШИБКА",
        "cli.ready_state": "ГОТОВ К ЗАПУСКУ",

        # CLI messages, help and web server console output
        "cli.empty_registry": "Реестр пуст. Выполните `agents scan` для поиска приложений.",
        "cli.agent_not_found": "Агент '{id}' не найден в реестре.",
        "cli.start_all": "Запуск всех фоновых сервисов...",
        "cli.start_failed": "Ошибка запуска: {msg}",
        "cli.stop_all": "Остановка всех активных сервисов...",
        "cli.stop_failed": "Ошибка остановки: {msg}",
        "cli.restarting": "Перезапуск {id}...",
        "cli.logs_title": "Логи: {name} (последние {n} строк)",
        "cli.logs_follow_title": "Поток логов: {name} (Ctrl+C для выхода)",
        "cli.logs_waiting": "Файл логов ещё не создан. Ожидание...",
        "cli.logs_follow_done": "Поток завершён.",
        "cli.scanning": "Сканирование системы на наличие микроприложений и агентов...",
        "cli.scan_found": "Найдены новые микроприложения ({n}):",
        "cli.col.dir": "КАТАЛОГ",
        "cli.scan_add_hint": "Чтобы добавить найденное приложение в диспетчер, выполните:",
        "cli.scan_all_registered": "Все найденные микроприложения уже зарегистрированы в диспетчере!",
        "cli.scan_already_count": "Уже зарегистрировано: {n} приложений.",
        "cli.already_registered_as": "'{id}' уже зарегистрирован как '{existing}'.",
        "cli.prompt_id": "Введите ID агента (например: my-bot): ",
        "cli.id_empty": "ID не может быть пустым.",
        "cli.prompt_name": "Введите название (например: My Bot Service): ",
        "cli.prompt_dir": "Путь к каталогу: ",
        "cli.default_desc": "Микроприложение {name}",
        "cli.health_title": "Системные ресурсы ({host})",
        "cli.health_cpu": "Загрузка CPU",
        "cli.health_ram": "Оперативная память",
        "cli.health_gpu": "Видеокарта ({name})",
        "cli.health_gpu_load": "Загрузка GPU",
        "cli.health_vram": "Видеопамять VRAM",
        "cli.health_temp": "Температура",
        "cli.health_power": "Мощность",
        "cli.health_disks": "Дисковое пространство",
        "cli.health_disk_line": "Свободно: {free} GB из {total} GB ({percent}% занято)",
        "cli.health_net": "Сетевые интерфейсы",
        "cli.lang_current": "Текущий язык",
        "cli.lang_supported": "Поддерживаются",
        "cli.lang_switch": "Сменить",
        "cli.lang_unsupported": "Неподдерживаемый язык: {code}. Доступны: {available}",
        "cli.lang_changed": "Язык интерфейса изменён на {code}!",
        "cli.help.description": "⬡ Диспетчер агентов и микроприложений — запуск, контроль и мониторинг",
        "cli.help.lang": "Язык интерфейса для этой команды (uk, en, ru)",
        "cli.help.command": "Команда диспетчера",
        "cli.help.lang_cmd": "Показать или сменить язык интерфейса (uk, en, ru)",
        "cli.help.lang_code": "Код языка",
        "cli.help.list": "Список всех агентов и их состояние",
        "cli.help.status": "Подробный статус агента",
        "cli.help.agent_id": "ID агента",
        "cli.help.agent_id_or_all": "ID агента или 'all'",
        "cli.help.start": "Запустить агента или сервис (или 'all')",
        "cli.help.stop": "Остановить агента или сервис (или 'all')",
        "cli.help.restart": "Перезапустить агента",
        "cli.help.logs": "Показать логи агента",
        "cli.help.lines": "Количество строк",
        "cli.help.follow": "Следить за новыми строками (live follow)",
        "cli.help.open": "Открыть веб-интерфейс в браузере",
        "cli.help.run": "Запустить CLI-агента с параметрами",
        "cli.help.extra_args": "Аргументы для команды агента",
        "cli.help.scan": "Поиск новых микроприложений в системе",
        "cli.help.add": "Зарегистрировать новое приложение в диспетчере",
        "cli.help.name": "Название",
        "cli.help.dir": "Каталог проекта",
        "cli.help.port": "Порт",
        "cli.help.type": "Тип",
        "cli.help.start_cmd": "Команда запуска",
        "cli.help.desc": "Описание",
        "cli.help.remove": "Удалить приложение из реестра",
        "cli.help.health": "Состояние системных ресурсов (CPU, RAM, диски, сеть)",
        "cli.help.web": "Запустить веб-интерфейс диспетчера",
        "cli.help.web_port": "Порт веб-сервера (по умолчанию: web_port из настроек, иначе 8800)",
        "cli.help.web_host": "Адрес для прослушивания (по умолчанию: web_host из настроек, иначе 127.0.0.1). 0.0.0.0 открывает дашборд без авторизации для всей сети",
        "web.started": "Диспетчер агентов — веб-панель запущена!",
        "web.local": "Локально",
        "web.lan": "В сети LAN",
        "web.local_only": "Доступен только с этого компьютера. Для удалённого доступа используйте SSH-туннель (см. README).",
        "web.exposed_warning": "ВНИМАНИЕ: дашборд слушает {host} и не имеет авторизации. Любой, кто может достучаться до этого адреса, может выполнять команды от имени вашего пользователя.",
        "web.stop_hint": "Нажмите CTRL+C для остановки сервера.",

        # Agent names and descriptions come from user registrations.
    }
}


def get_system_lang() -> Optional[str]:
    """Interface language from the system locale, if it is a supported one."""
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if value:
            code = value[:2].lower()
            return code if code in SUPPORTED_LANGUAGES else None
    return None


def get_current_lang() -> str:
    """Determine active language from env, settings, system locale, or fallback."""
    env_lang = os.environ.get("AGENTS_LANG", "").lower()
    if env_lang in SUPPORTED_LANGUAGES:
        return env_lang

    try:
        from .config import load_settings
        settings = load_settings()
        cfg_lang = settings.get("lang", "").lower()
        if cfg_lang in SUPPORTED_LANGUAGES:
            return cfg_lang
    except Exception:
        pass

    return get_system_lang() or DEFAULT_LANGUAGE


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """Translate key for language with fallback."""
    target_lang = lang or get_current_lang()
    if target_lang not in SUPPORTED_LANGUAGES:
        target_lang = DEFAULT_LANGUAGE

    val = TRANSLATIONS.get(target_lang, {}).get(key)
    if val is None:
        val = TRANSLATIONS.get(DEFAULT_LANGUAGE, {}).get(key, key)

    if kwargs:
        try:
            return val.format(**kwargs)
        except Exception:
            return val
    return val


def get_all_translations() -> Dict[str, Dict[str, str]]:
    """Return complete translation dictionaries for frontend JSON delivery."""
    return TRANSLATIONS


def get_agent_name(agent: Any, lang: Optional[str] = None) -> str:
    """Get localized agent name from i18n dict, agent model, or fallback."""
    agent_id = getattr(agent, "id", None) or (agent.get("id") if isinstance(agent, dict) else "")
    default_name = getattr(agent, "name", None) or (agent.get("name") if isinstance(agent, dict) else agent_id)
    target_lang = lang or get_current_lang()

    # 1. Check i18n translation key
    key = f"agent.{agent_id}.name"
    val = t(key, lang=target_lang)
    if val != key:
        return val

    # 2. Check agent's name_i18n dictionary if present
    name_i18n = getattr(agent, "name_i18n", None) or (agent.get("name_i18n") if isinstance(agent, dict) else None)
    if isinstance(name_i18n, dict) and target_lang in name_i18n:
        return name_i18n[target_lang]

    return default_name or agent_id


def get_agent_description(agent: Any, lang: Optional[str] = None) -> str:
    """Get localized agent description from i18n dict, agent model, or fallback."""
    agent_id = getattr(agent, "id", None) or (agent.get("id") if isinstance(agent, dict) else "")
    default_desc = getattr(agent, "description", None) or (agent.get("description") if isinstance(agent, dict) else "")
    target_lang = lang or get_current_lang()

    # 1. Check i18n translation key
    key = f"agent.{agent_id}.desc"
    val = t(key, lang=target_lang)
    if val != key:
        return val

    # 2. Check agent's description_i18n dictionary if present
    desc_i18n = getattr(agent, "description_i18n", None) or (agent.get("description_i18n") if isinstance(agent, dict) else None)
    if isinstance(desc_i18n, dict) and target_lang in desc_i18n:
        return desc_i18n[target_lang]

    return default_desc or ""
