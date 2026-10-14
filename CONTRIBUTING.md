# Contributing to Agent Dispatcher

Thank you for your interest in improving Agent Dispatcher. Bug reports, ideas, documentation fixes, and pull requests are all welcome.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Please report security vulnerabilities privately as described in the [Security Policy](SECURITY.md), not in public issues.

## Before you start

- **Bugs and ideas:** open an [issue](https://github.com/BeforeSteel/agent-dispatcher/issues/new/choose) using one of the templates.
- **Small fixes** such as typos or documentation corrections can go straight to a pull request.
- **Larger changes** such as a new integration, a new dependency, or a change to the registry format: please open an issue first, so the approach can be agreed before you spend time on it.

Agent Dispatcher manages application processes. It does not schedule AI tasks or coordinate agents, and general-purpose AI coding CLIs (`claude`, `codex`, `agy`, `grok`) are intentionally excluded from registration.

## Development setup

Requirements are listed in the [README](README.md#requirements). Then:

```bash
git clone https://github.com/BeforeSteel/agent-dispatcher.git
cd agent-dispatcher
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

### Run with an isolated home directory

The dispatcher stores its registry and settings in `~/.config/agent_dispatcher/` and its PID files and logs in `~/.local/state/agent_dispatcher/`. To avoid changing your real configuration while developing, run it with a temporary `HOME` and a port that your own dashboard does not use:

```bash
export DEV_HOME="$(mktemp -d)"
HOME="$DEV_HOME" .venv/bin/python cli.py web --host 127.0.0.1 --port 8801
HOME="$DEV_HOME" .venv/bin/python cli.py list
```

Then open `http://localhost:8801/`. Delete `$DEV_HOME` when you are done.

## Checks before a pull request

There is no automated test suite yet, so please check your change by hand:

1. Make sure all Python files still compile:

   ```bash
   .venv/bin/python -m py_compile cli.py dispatcher/*.py
   ```

2. Run the CLI commands your change affects, using an isolated `HOME` as shown above.
3. For dashboard changes, check both the light and the dark theme, and a narrow browser window.
4. Switch between English, Ukrainian, and Russian to make sure no text is missing.

## Guidelines

- **Translations.** Every user-visible string goes through `dispatcher/i18n.py` and needs an entry in all three languages: `uk`, `en`, and `ru`. If you do not speak one of them, add your best attempt and mention it in the pull request.
- **Untrusted text in the dashboard.** Application names, descriptions, commands, paths, and log output come from user configuration and discovered files. Insert them into HTML only through the `esc()` helper in `static/js/app.js`.
- **Dependencies.** The runtime depends only on Flask and psutil. Please explain in the pull request why any new dependency is needed.
- **No personal data.** Do not commit real paths, IP addresses, host names, tokens, your `agents.json` or `settings.json`, or logs. Use placeholders such as `/home/your-user/...` and documentation addresses such as `192.0.2.10`.
- **Documentation.** Update `README.md` when you change CLI commands, options, configuration fields, or user-visible behavior.
- **Commit messages** follow [Conventional Commits](https://www.conventionalcommits.org/), as in the existing history: `feat(ui): ...`, `fix: ...`, `docs: ...`, `chore: ...`.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE) that covers this project.
