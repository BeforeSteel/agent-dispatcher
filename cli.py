#!/usr/bin/env python3
"""
Agent Dispatcher CLI - Керування агентами та мікрододатками з командного рядка
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Ensure dispatcher package can be imported
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from dispatcher.manager import AgentManager
from dispatcher.system_info import get_system_stats, get_network_ips

# Terminal Colors
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_GREEN = "\033[1;32m"
C_BLUE = "\033[1;34m"
C_CYAN = "\033[1;36m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_PURPLE = "\033[1;35m"


def print_header(title: str):
    print(f"\n{C_BOLD}{C_CYAN}⬡ {title}{C_RESET}")
    print(f"{C_DIM}{'─' * 84}{C_RESET}")


def cmd_list(manager: AgentManager, args):
    """Display table of all agents and their live status."""
    statuses = manager.list_all_status()
    if not statuses:
        print(f"\n{C_YELLOW}Реєстр порожній. Виконайте `agents scan` для пошуку додатків.{C_RESET}\n")
        return

    # Count stats
    running_count = sum(1 for s in statuses if s.is_running)
    ready_count = sum(1 for s in statuses if s.status == "READY")
    total_count = len(statuses)

    print(f"\n{C_BOLD}⬡ Диспетчер Агентів{C_RESET} {C_DIM}({running_count} активних · {ready_count} CLI · всього {total_count}){C_RESET}")
    print(f"{C_DIM}{'═' * 84}{C_RESET}")
    print(f"{C_BOLD}{C_BLUE}{'СТАН':<4} {'ID':<16} {'НАЗВА':<22} {'ТИП':<10} {'ПОРТ':<8} {'PID':<8} {'РЕСУРСИ':<14}{C_RESET}")
    print(f"{C_DIM}{'─' * 84}{C_RESET}")

    for s in sorted(statuses, key=lambda x: (not x.is_running, x.status != "READY", x.id)):
        icon_str = "🟢" if s.status == "RUNNING" else ("⚡" if s.status == "READY" else ("🔴" if s.status == "FAILED" else "⚪"))
        id_fmt = f"{C_BOLD}{s.id:<16}{C_RESET}" if s.is_running else f"{s.id:<16}"
        name_fmt = f"{s.name[:21]:<22}"

        type_color = C_YELLOW if s.type == "systemd" else (C_PURPLE if s.type == "docker" else C_BLUE)
        type_fmt = f"{type_color}{s.type:<10}{C_RESET}"

        port_str = str(s.port) if s.port else "—"
        port_fmt = f"{port_str:<8}"

        pid_str = str(s.pid) if s.pid else "—"
        pid_fmt = f"{pid_str:<8}"

        if s.is_running:
            if s.memory_mb is not None:
                res_str = f"{s.memory_mb:.0f}MB/{s.cpu_percent:.0f}%"
            else:
                res_str = "active"
            res_fmt = f"{C_GREEN}{res_str:<14}{C_RESET}"
        elif s.status == "READY":
            res_fmt = f"{C_CYAN}{'CLI Tool':<14}{C_RESET}"
        else:
            res_fmt = f"{C_DIM}{'offline':<14}{C_RESET}"

        print(f" {icon_str}  {id_fmt} {name_fmt} {type_fmt} {port_fmt} {pid_fmt} {res_fmt}")

    print(f"{C_DIM}{'─' * 84}{C_RESET}")
    print(f"{C_DIM}Команди: `agents start <id>`, `agents stop <id>`, `agents logs <id>`, `agents open <id>`{C_RESET}\n")


def cmd_status(manager: AgentManager, args):
    """Detailed status inspection of an agent."""
    if not args.agent_id:
        cmd_list(manager, args)
        return

    st = manager.get_status(args.agent_id)
    agent = manager.get_agent(args.agent_id)
    if not agent:
        print(f"{C_RED}❌ Агента '{args.agent_id}' не знайдено в реєстрі.{C_RESET}")
        return

    print_header(f"Статус агента: {agent.name} ({agent.id})")
    print(f"  {C_BOLD}Опис:{C_RESET}        {agent.description or '—'}")
    print(f"  {C_BOLD}Категорія:{C_RESET}   {agent.category}  |  {C_BOLD}Тип:{C_RESET} {agent.type}")

    if st.status == "RUNNING":
        status_line = f"{C_GREEN}🟢 ПРАЦЮЄ (RUNNING){C_RESET}"
    elif st.status == "READY":
        status_line = f"{C_CYAN}⚡ ГОТОВИЙ ДО ЗАПУСКУ (CLI READY){C_RESET}"
    elif st.status == "FAILED":
        status_line = f"{C_RED}🔴 ПОМИЛКА (FAILED){C_RESET}"
    else:
        status_line = f"{C_YELLOW}⚪ ЗУПИНЕНО (STOPPED){C_RESET}"
    print(f"  {C_BOLD}Статус:{C_RESET}      {status_line}")

    if st.pid:
        print(f"  {C_BOLD}PID:{C_RESET}         {st.pid}")
    if st.uptime:
        print(f"  {C_BOLD}Аптайм:{C_RESET}      {st.uptime}")
    if st.memory_mb is not None:
        print(f"  {C_BOLD}Пам'ять:{C_RESET}     {st.memory_mb:.1f} MB (RSS)")
    if st.cpu_percent is not None:
        print(f"  {C_BOLD}CPU:{C_RESET}         {st.cpu_percent:.1f}%")

    if agent.port:
        port_state = f"{C_GREEN}Слухає з'єднання{C_RESET}" if st.port_listening else f"{C_DIM}Неактивний{C_RESET}"
        print(f"  {C_BOLD}Порт:{C_RESET}        {agent.port} ({port_state})")

    if st.urls:
        print(f"  {C_BOLD}Веб-адреси:{C_RESET}")
        for u in st.urls:
            print(f"               • {u['label']:<16} {C_CYAN}{u['url']}{C_RESET}")

    if agent.working_dir:
        print(f"  {C_BOLD}Каталог:{C_RESET}     {agent.working_dir}")
    if agent.venv_path:
        print(f"  {C_BOLD}Virtualenv:{C_RESET}  {agent.venv_path}")

    log_path = manager.get_log_file(agent)
    if log_path.exists():
        print(f"  {C_BOLD}Файл логів:{C_RESET}  {log_path}")
        print(f"\n  {C_BOLD}{C_BLUE}Останні рядки логу:{C_RESET}")
        print(f"  {C_DIM}{'┄' * 70}{C_RESET}")
        recent_logs = manager.get_logs(args.agent_id, lines=8)
        for line in recent_logs:
            print(f"    {C_DIM}{line}{C_RESET}")
        print(f"  {C_DIM}{'┄' * 70}{C_RESET}")

    print()


def cmd_start(manager: AgentManager, args):
    """Start an agent or all agents."""
    if args.agent_id.lower() == "all":
        print(f"\n{C_BOLD}🚀 Масовий запуск усіх фонових сервісів...{C_RESET}")
        for agent in manager.list_agents():
            if agent.type in ("daemon", "systemd", "docker"):
                ok, msg = manager.start(agent.id)
                prefix = f"{C_GREEN}✅" if ok else f"{C_RED}❌"
                print(f"  {prefix} {agent.name:<22}: {msg}{C_RESET}")
        print()
        return

    ok, msg = manager.start(args.agent_id)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}")
        st = manager.get_status(args.agent_id)
        if st.urls:
            for u in st.urls:
                print(f"   🌐 {u['label']}: {C_CYAN}{u['url']}{C_RESET}")
        print()
    else:
        print(f"\n{C_RED}❌ Помилка запуску: {msg}{C_RESET}\n")
        sys.exit(1)


def cmd_stop(manager: AgentManager, args):
    """Stop an agent or all agents."""
    if args.agent_id.lower() == "all":
        print(f"\n{C_BOLD}⏹ Зупинка всіх активних сервісів...{C_RESET}")
        for agent in manager.list_agents():
            st = manager.get_status(agent.id)
            if st.is_running:
                ok, msg = manager.stop(agent.id)
                prefix = f"{C_GREEN}✅" if ok else f"{C_RED}❌"
                print(f"  {prefix} {agent.name:<22}: {msg}{C_RESET}")
        print()
        return

    ok, msg = manager.stop(args.agent_id)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"\n{C_RED}❌ Помилка зупинки: {msg}{C_RESET}\n")
        sys.exit(1)


def cmd_restart(manager: AgentManager, args):
    """Restart an agent."""
    print(f"\n{C_YELLOW}🔄 Перезапуск {args.agent_id}...{C_RESET}")
    ok, msg = manager.restart(args.agent_id)
    if ok:
        print(f"{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"{C_RED}❌ {msg}{C_RESET}\n")
        sys.exit(1)


def cmd_logs(manager: AgentManager, args):
    """Display logs or follow stream."""
    agent = manager.get_agent(args.agent_id)
    if not agent:
        print(f"{C_RED}❌ Агента '{args.agent_id}' не знайдено.{C_RESET}")
        return

    lines = args.lines or 50
    if not args.follow:
        log_lines = manager.get_logs(args.agent_id, lines=lines)
        print_header(f"Логи: {agent.name} (останні {len(log_lines)} рядків)")
        for l in log_lines:
            print(l)
        print()
    else:
        print_header(f"Стрім логів: {agent.name} (Ctrl+C для виходу)")
        # Show initial chunk
        initial = manager.get_logs(args.agent_id, lines=20)
        for l in initial:
            print(l)

        log_path = manager.get_log_file(agent)
        if not log_path.exists():
            print(f"{C_YELLOW}Файл логів поки що не створено. Очікування...{C_RESET}")

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if line:
                        print(line, end="")
                    else:
                        time.sleep(0.3)
        except KeyboardInterrupt:
            print(f"\n{C_DIM}Стрімінг завершено.{C_RESET}\n")


def cmd_open(manager: AgentManager, args):
    """Open web interface in browser."""
    ok, msg = manager.open_browser(args.agent_id)
    if ok:
        print(f"{C_GREEN}🌐 {msg}{C_RESET}")
    else:
        print(f"{C_RED}❌ {msg}{C_RESET}")


def cmd_run(manager: AgentManager, args):
    """Run CLI tool or agent."""
    code = manager.run_cli(args.agent_id, args.extra_args)
    sys.exit(code)


def cmd_scan(manager: AgentManager, args):
    """Scan filesystem for micro-applications and agents."""
    print(f"\n{C_BOLD}🔍 Сканування системи на наявність мікрододатків та агентів...{C_RESET}")
    candidates = manager.scan_for_microapps()

    new_found = [c for c in candidates if not c.get("is_registered")]
    already_reg = [c for c in candidates if c.get("is_registered")]

    print(f"{C_DIM}{'─' * 84}{C_RESET}")
    if new_found:
        print(f"\n{C_BOLD}{C_GREEN}✨ Знайдено нові мікрододатки ({len(new_found)}):{C_RESET}")
        print(f"{C_BOLD}{C_BLUE}{'ID':<16} {'НАЗВА':<24} {'ТИП':<10} {'ПОРТ':<8} КАТАЛОГ{C_RESET}")
        print(f"{C_DIM}{'─' * 84}{C_RESET}")
        for c in new_found:
            port_s = str(c.get("port") or "—")
            print(f" {C_YELLOW}{c['id']:<16}{C_RESET} {c['name'][:23]:<24} {c['type']:<10} {port_s:<8} {C_DIM}{c.get('working_dir') or '—'}{C_RESET}")

        print(f"\n{C_BOLD}Щоб додати знайдений додаток у диспетчер, виконайте:{C_RESET}")
        print(f"  {C_CYAN}agents add --id {new_found[0]['id']}{C_RESET}")
    else:
        print(f"\n{C_GREEN}Всі знайдені мікрододатки вже зареєстровані в диспетчері!{C_RESET}")

    if already_reg:
        print(f"\n{C_DIM}Вже зареєстровано в системі: {len(already_reg)} додатків.{C_RESET}\n")


def cmd_add(manager: AgentManager, args):
    """Register a new agent."""
    # Check if candidate exists from scan
    if args.id:
        candidates = manager.scan_for_microapps()
        match = next((c for c in candidates if c["id"] == args.id), None)
        if match:
            ok, msg = manager.add_agent(match)
            if ok:
                print(f"{C_GREEN}✅ {msg}{C_RESET}")
            else:
                print(f"{C_RED}❌ {msg}{C_RESET}")
            return

    # Interactive or flags
    agent_id = args.id or input("Введіть ID агента (наприклад: my-bot): ").strip()
    if not agent_id:
        print(f"{C_RED}ID не може бути порожнім.{C_RESET}")
        return

    name = args.name or input("Введіть назву (наприклад: My Bot Service): ").strip() or agent_id
    work_dir = args.dir or input("Шлях до каталогу: ").strip() or None
    port = int(args.port) if args.port else None
    app_type = args.type or ("web_app" if port else "daemon")

    data = {
        "id": agent_id,
        "name": name,
        "type": app_type,
        "working_dir": work_dir,
        "port": port,
        "url": f"http://localhost:{port}" if port else None,
        "start_cmd": args.start_cmd or None,
        "description": args.desc or f"Мікрододаток {name}"
    }

    ok, msg = manager.add_agent(data)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"\n{C_RED}❌ {msg}{C_RESET}\n")


def cmd_remove(manager: AgentManager, args):
    """Remove agent from registry."""
    ok, msg = manager.remove_agent(args.agent_id)
    if ok:
        print(f"\n{C_GREEN}✅ {msg}{C_RESET}\n")
    else:
        print(f"\n{C_RED}❌ {msg}{C_RESET}\n")


def cmd_health(manager: AgentManager, args):
    """Check host system health and resources."""
    stats = get_system_stats()
    print_header(f"Системні ресурси ({stats.get('hostname')})")
    print(f"  {C_BOLD}Завантаження CPU:{C_RESET} {stats.get('cpu_percent')}% ({stats.get('cpu_count')} ядер)")
    if "memory_total_gb" in stats:
        print(f"  {C_BOLD}Оперативна пам'ять:{C_RESET} {stats.get('memory_used_gb')} GB / {stats.get('memory_total_gb')} GB ({stats.get('memory_percent')}%)")

    gpu = stats.get("gpu")
    if gpu:
        print(f"\n  {C_BOLD}Відеокарта ({gpu.get('name')}):{C_RESET}")
        print(f"    • Завантаження GPU:  {C_GREEN}{gpu.get('gpu_util_percent')}%{C_RESET}")
        print(f"    • Відеопам'ять VRAM: {C_CYAN}{gpu.get('mem_used_gb')} GB{C_RESET} / {gpu.get('mem_total_gb')} GB ({gpu.get('mem_percent')}%)")
        print(f"    • Температура:       {C_YELLOW}{gpu.get('temperature_c')}°C{C_RESET} (Потужність: {gpu.get('power_w')}W / {gpu.get('power_limit_w')}W)")

    disks = stats.get("disks", {})
    if disks:
        print(f"\n  {C_BOLD}Дисковий простір:{C_RESET}")
        for path, du in disks.items():
            print(f"    • {path:<20} Вільних: {du['free_gb']} GB із {du['total_gb']} GB ({du['percent']}% зайнято)")

    ips = stats.get("ips", {})
    print(f"\n  {C_BOLD}Мережеві інтерфейси:{C_RESET}")
    for k, v in ips.items():
        print(f"    • {k.upper():<12} {C_CYAN}{v}{C_RESET}")
    print()


def cmd_web(manager: AgentManager, args):
    """Start the Web Dashboard interface."""
    from dispatcher.web_server import run_web_dashboard
    port = args.port or manager.settings.get("web_port", 8800)
    host = args.host or manager.settings.get("web_host", "0.0.0.0")
    run_web_dashboard(manager, host=host, port=port)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agents",
        description="⬡ Диспетчер Агентів та Мікрододатків — запуск, контроль та моніторинг"
    )
    sub = parser.add_subparsers(dest="command", help="Команда диспетчера")

    # list
    p_list = sub.add_parser("list", aliases=["ls", "ps"], help="Список усіх агентів та їх стан")

    # status
    p_status = sub.add_parser("status", help="Детальний статус конкретного агента")
    p_status.add_argument("agent_id", nargs="?", default=None, help="ID агента")

    # start
    p_start = sub.add_parser("start", help="Запустити агента або сервіс (або 'all')")
    p_start.add_argument("agent_id", help="ID агента або 'all'")

    # stop
    p_stop = sub.add_parser("stop", help="Зупинити агента або сервіс (або 'all')")
    p_stop.add_argument("agent_id", help="ID агента або 'all'")

    # restart
    p_restart = sub.add_parser("restart", help="Перезапустити агента")
    p_restart.add_argument("agent_id", help="ID агента")

    # logs
    p_logs = sub.add_parser("logs", help="Переглянути логи агента")
    p_logs.add_argument("agent_id", help="ID агента")
    p_logs.add_argument("-n", "--lines", type=int, default=50, help="Кількість рядків")
    p_logs.add_argument("-f", "--follow", action="store_true", help="Стрімінг нових рядків (live follow)")

    # open
    p_open = sub.add_parser("open", help="Відкрити веб-інтерфейс у браузері")
    p_open.add_argument("agent_id", help="ID агента")

    # run
    p_run = sub.add_parser("run", help="Запустити CLI агента з параметрами")
    p_run.add_argument("agent_id", help="ID агента")
    p_run.add_argument("extra_args", nargs="*", help="Аргументи для команди агента")

    # scan
    sub.add_parser("scan", aliases=["discover"], help="Пошук нових мікрододатків у системі")

    # add
    p_add = sub.add_parser("add", help="Зареєструвати новий додаток у диспетчер")
    p_add.add_argument("--id", help="ID агента")
    p_add.add_argument("--name", help="Назва")
    p_add.add_argument("--dir", help="Каталог проєкту")
    p_add.add_argument("--port", type=int, help="Порт")
    p_add.add_argument("--type", choices=["daemon", "systemd", "cli", "docker"], help="Тип")
    p_add.add_argument("--start-cmd", help="Команда запуску")
    p_add.add_argument("--desc", help="Опис")

    # remove
    p_rm = sub.add_parser("remove", aliases=["rm", "delete"], help="Видалити додаток із реєстру")
    p_rm.add_argument("agent_id", help="ID агента")

    # health
    sub.add_parser("health", help="Стан системних ресурсів (CPU, RAM, Disks, Network)")

    # web
    p_web = sub.add_parser("web", aliases=["gui", "dashboard"], help="Запустити Web-інтерфейс диспетчера")
    p_web.add_argument("-p", "--port", type=int, default=8800, help="Порт веб-сервера (за замовчуванням 8800)")
    p_web.add_argument("--host", default="0.0.0.0", help="Хост веб-сервера (за замовчуванням 0.0.0.0)")

    return parser


def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        # Default to list if no arguments passed
        manager = AgentManager()
        cmd_list(manager, None)
        return

    args = parser.parse_args()
    manager = AgentManager()

    cmd = args.command
    if cmd in ("list", "ls", "ps"):
        cmd_list(manager, args)
    elif cmd == "status":
        cmd_status(manager, args)
    elif cmd == "start":
        cmd_start(manager, args)
    elif cmd == "stop":
        cmd_stop(manager, args)
    elif cmd == "restart":
        cmd_restart(manager, args)
    elif cmd == "logs":
        cmd_logs(manager, args)
    elif cmd == "open":
        cmd_open(manager, args)
    elif cmd == "run":
        cmd_run(manager, args)
    elif cmd in ("scan", "discover"):
        cmd_scan(manager, args)
    elif cmd == "add":
        cmd_add(manager, args)
    elif cmd in ("remove", "rm", "delete"):
        cmd_remove(manager, args)
    elif cmd == "health":
        cmd_health(manager, args)
    elif cmd in ("web", "gui", "dashboard"):
        cmd_web(manager, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
