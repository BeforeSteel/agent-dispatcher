"""Flask Web Dashboard for Agent Dispatcher."""

import os
import sys
import json
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory

from .manager import AgentManager
from .system_info import get_system_stats, get_network_urls, get_network_ips

# Silence Werkzeug access logs in production mode
log = logging.getLogger('werkzeug')
log.setLevel(logging.WARNING)


def create_app(manager: AgentManager = None) -> Flask:
    if manager is None:
        manager = AgentManager()

    base_dir = Path(__file__).resolve().parent.parent
    templates_dir = base_dir / "templates"
    static_dir = base_dir / "static"

    app = Flask(
        __name__,
        template_folder=str(templates_dir),
        static_folder=str(static_dir)
    )

    @app.route("/")
    def index():
        return render_template("index.html")

    # API Endpoints
    @app.route("/api/status")
    def api_status():
        manager.reload()
        from .i18n import get_current_lang
        lang = request.args.get("lang") or get_current_lang()
        statuses = [s.to_dict() for s in manager.list_all_status(lang=lang)]
        system_stats = get_system_stats()
        return jsonify({
            "ok": True,
            "agents": statuses,
            "system": system_stats,
            "lang": lang
        })

    @app.route("/api/agents/<agent_id>/start", methods=["POST"])
    def api_start(agent_id):
        from .i18n import get_current_lang
        lang = request.args.get("lang") or get_current_lang()
        ok, msg = manager.start(agent_id)
        st = manager.get_status(agent_id, lang=lang).to_dict()
        return jsonify({"ok": ok, "message": msg, "status": st}), (200 if ok else 400)

    @app.route("/api/agents/<agent_id>/stop", methods=["POST"])
    def api_stop(agent_id):
        from .i18n import get_current_lang
        lang = request.args.get("lang") or get_current_lang()
        ok, msg = manager.stop(agent_id)
        st = manager.get_status(agent_id, lang=lang).to_dict()
        return jsonify({"ok": ok, "message": msg, "status": st}), (200 if ok else 400)

    @app.route("/api/agents/<agent_id>/restart", methods=["POST"])
    def api_restart(agent_id):
        from .i18n import get_current_lang
        lang = request.args.get("lang") or get_current_lang()
        ok, msg = manager.restart(agent_id)
        st = manager.get_status(agent_id, lang=lang).to_dict()
        return jsonify({"ok": ok, "message": msg, "status": st}), (200 if ok else 400)

    @app.route("/api/agents/<agent_id>/logs")
    def api_logs(agent_id):
        lines = int(request.args.get("lines", 60))
        log_lines = manager.get_logs(agent_id, lines=lines)
        return jsonify({"ok": True, "agent_id": agent_id, "lines": log_lines})

    @app.route("/api/agents/<agent_id>/open", methods=["POST"])
    def api_open(agent_id):
        ok, msg = manager.open_browser(agent_id)
        return jsonify({"ok": ok, "message": msg})

    @app.route("/api/scan")
    def api_scan():
        candidates = manager.scan_for_microapps()
        return jsonify({"ok": True, "candidates": candidates})

    @app.route("/api/agents/add", methods=["POST"])
    def api_add():
        data = request.json or {}
        ok, msg = manager.add_agent(data)
        return jsonify({"ok": ok, "message": msg}), (200 if ok else 400)

    @app.route("/api/agents/<agent_id>", methods=["DELETE"])
    def api_delete(agent_id):
        ok, msg = manager.remove_agent(agent_id)
        return jsonify({"ok": ok, "message": msg}), (200 if ok else 400)

    @app.route("/api/system")
    def api_system():
        return jsonify(get_system_stats())

    @app.route("/api/i18n")
    def api_i18n():
        from .i18n import get_all_translations, get_current_lang
        return jsonify({
            "current": get_current_lang(),
            "translations": get_all_translations()
        })

    @app.route("/api/lang", methods=["POST"])
    def api_lang():
        from .config import save_settings
        lang = (request.json or {}).get("lang", "uk")
        settings = manager.settings
        settings["lang"] = lang
        save_settings(settings)
        return jsonify({"ok": True, "lang": lang})

    @app.route("/api/batch/<action>", methods=["POST"])
    def api_batch(action):
        results = []
        if action == "start_all":
            for ag in manager.list_agents():
                if ag.type in ("daemon", "systemd", "docker"):
                    ok, msg = manager.start(ag.id)
                    results.append({"id": ag.id, "ok": ok, "message": msg})
        elif action == "stop_all":
            for ag in manager.list_agents():
                st = manager.get_status(ag.id)
                if st.is_running:
                    ok, msg = manager.stop(ag.id)
                    results.append({"id": ag.id, "ok": ok, "message": msg})
        return jsonify({"ok": True, "results": results})

    return app


def run_web_dashboard(manager: AgentManager, host: str = "0.0.0.0", port: int = 8800):
    """Run Flask development server with network summary output."""
    app = create_app(manager)

    ips = get_network_ips()
    lan_ip = ips.get("lan", "127.0.0.1")
    tailscale_ip = ips.get("tailscale")

    print("\n" + "═" * 70)
    print(" 🚀 Диспетчер Агентів — Web Dashboard запущено!")
    print("═" * 70)
    print(f" 🌐 Локально:      http://localhost:{port}")
    if lan_ip != "127.0.0.1":
        print(f" 🌐 У мережі LAN:  http://{lan_ip}:{port}")
    if tailscale_ip:
        print(f" 🌐 Tailscale:     http://{tailscale_ip}:{port}")
    print("═" * 70)
    print(" Натисніть CTRL+C для зупинки сервера.\n")

    app.run(host=host, port=port, debug=False)
