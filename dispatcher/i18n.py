"""Internationalization (i18n) engine for Agent Dispatcher (CLI & Web)."""

import os
from typing import Dict, Any, Optional
from pathlib import Path

# Supported languages
SUPPORTED_LANGUAGES = ["uk", "en", "ru"]
DEFAULT_LANGUAGE = "uk"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "uk": {
        # General / App
        "app.title": "Agent Dispatcher",
        "app.subtitle": "Централізований диспетчер мікрододатків та ШІ-агентів",
        "app.version": "v1.0",
        
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

        # Tabs & Filters
        "tab.all": "Всі",
        "tab.running": "🟢 Активні",
        "tab.web": "🌐 Веб-додатки",
        "tab.cli": "⚡ CLI Агенти",
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

        # Agent names and descriptions come from user registrations.
    },
    "en": {
        # General / App
        "app.title": "Agent Dispatcher",
        "app.subtitle": "Centralized micro-app & AI agent orchestrator",
        "app.version": "v1.0",
        
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

        # Tabs & Filters
        "tab.all": "All",
        "tab.running": "🟢 Running",
        "tab.web": "🌐 Web Apps",
        "tab.cli": "⚡ CLI Agents",
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

        # Agent names and descriptions come from user registrations.
    },
    "ru": {
        # General / App
        "app.title": "Agent Dispatcher",
        "app.subtitle": "Централизованный диспетчер микроприложений и ИИ-агентов",
        "app.version": "v1.0",
        
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

        # Tabs & Filters
        "tab.all": "Все",
        "tab.running": "🟢 Активные",
        "tab.web": "🌐 Веб-приложения",
        "tab.cli": "⚡ CLI Агенты",
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

        # Agent names and descriptions come from user registrations.
    }
}


def get_current_lang() -> str:
    """Determine active language from env, settings, or fallback."""
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

    return DEFAULT_LANGUAGE


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
