# Agent Dispatcher

A lightweight Linux dashboard and command-line tool for discovering, monitoring, and controlling your local applications, scripts, systemd services, and Docker containers.

Use one place to see what is running, start or stop services, inspect logs, and open application web interfaces. Agent Dispatcher manages application processes; it does not schedule AI tasks or coordinate conversations between agents.

[Installation](#installation) · [First application](#try-your-first-application) · [CLI reference](#cli-reference) · [Configuration](#configuration) · [Troubleshooting](#troubleshooting) · [License](#license)

## Features

- A web dashboard with application cards, filters, search, and light/dark themes.
- A CLI available as `agents` and `agent-dispatch`.
- Start, stop, and restart background processes, existing systemd units, and existing Docker containers.
- Discover projects in selected directories and user systemd units, with registered applications marked in the results.
- View recent application logs, process memory and uptime where available, and listening-port status.
- Monitor host CPU and RAM; NVIDIA GPU, VRAM, temperature, and power are shown when `nvidia-smi` is available. The CLI also reports disk usage.
- English, Ukrainian, and Russian interface translations. Some installer messages, CLI help, and prompts are still in Ukrainian.

## Requirements

| Requirement | Details |
| --- | --- |
| Operating system | Linux. Native Windows and macOS installations are not supported. |
| Python | Python 3.10 or newer is recommended. Installation and the demo were checked on Linux with Python 3.12. |
| Tools | Bash, Git, and Python's `venv` and `pip`. |
| Browser | A modern browser for the dashboard. |
| Internet | Required to clone the repository and install dependencies. The dashboard currently loads Tailwind CSS and Lucide from external CDNs. |

Optional tools are needed only for their corresponding integrations: `systemctl` and `journalctl` for systemd, the Docker CLI and daemon for containers, and `xdg-open` for opening a browser from the CLI.

Agent Dispatcher does not install the applications it manages. Set up those applications, containers, or service units separately.

## Installation

Run the commands below in a Bash terminal as your normal user. Use `sudo` only for installing operating-system packages.

### 1. Install prerequisites

On Ubuntu or Debian:

```bash
sudo apt update
sudo apt install git python3 python3-venv python3-pip
```

On another Linux distribution, install the equivalent packages with its package manager. Check your Python version:

```bash
python3 --version
```

### 2. Download the project

Choose a location where you will keep the repository:

```bash
mkdir -p "$HOME/Projects"
cd "$HOME/Projects"
git clone https://github.com/BeforeSteel/agent-dispatcher.git
cd agent-dispatcher
```

If the repository is private, your GitHub account must have access. With an SSH key already configured for GitHub, use this clone command instead:

```bash
git clone git@github.com:BeforeSteel/agent-dispatcher.git
```

See [GitHub's cloning guide](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) for authentication help.

### 3. Install Python dependencies

From the repository directory:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

This installs Flask and psutil inside the project's virtual environment. You do not need to activate the environment or install packages globally. See the [Python virtual-environment guide](https://docs.python.org/3/library/venv.html) for details.

### 4. Review configuration defaults

A fresh installation starts with an empty application registry. Discovery searches your own `~/Projects` and `~/Downloads` folders by default. Existing registrations and settings are preserved.

To choose different discovery folders, edit `scan_dirs` in `~/.config/agent_dispatcher/settings.json` using absolute paths. See [Configuration](#configuration) for the file locations and examples.

### 5. Install the CLI shortcuts

Still in the repository directory:

```bash
bash install_cli.sh
export PATH="$HOME/.local/bin:$PATH"
agents lang en
agents list
```

The installer creates `~/.local/bin/agents` and the `agent-dispatch` alias. The shortcuts use this checkout's `.venv` automatically.

An empty registry is expected on a fresh installation. To make the shortcuts available in future Bash terminals, add the following line to `~/.bashrc` if it is not already present:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then open a new terminal or run `source ~/.bashrc`. For another shell, add the equivalent setting to its startup file.

### 6. Start the dashboard

```bash
agents web --host 127.0.0.1 --port 8800
```

Open **[http://localhost:8800/](http://localhost:8800/)** on the same computer. If needed, select **English** in the language menu. Press `Ctrl+C` in the terminal to stop the dashboard; managed background services can continue running.

You can also launch it directly from the repository without the CLI shortcuts:

```bash
bash run.sh web --host 127.0.0.1 --port 8800
```

`run.sh` can create the virtual environment and install missing dependencies, using `uv` when available or Python/pip otherwise. Review the configuration defaults above before using it for the first time.

**Network access:** the dashboard has no built-in authentication, and its API can register and execute commands with your user account's permissions. Always pass `--host 127.0.0.1` for local use; the current default is `0.0.0.0`, which listens on all interfaces. Host and port should be set with the command-line flags. Do not expose port 8800 directly to the internet. For access from another computer, keep the local binding and use an SSH tunnel:

```bash
# Run on the client computer; replace user and server with your SSH destination.
ssh -N -L 18800:127.0.0.1:8800 user@server
```

Then open `http://localhost:18800/` on the client. The SSH server must already be configured.

## Try your first application

This example registers a small HTTP server using Python's standard library. It requires no additional application dependencies. Use an unused port; the example uses `8091`.

```bash
mkdir -p "$HOME/Projects/dispatcher-demo"
agents add \
  --id dispatcher-demo \
  --name "Demo HTTP server" \
  --type daemon \
  --dir "$HOME/Projects/dispatcher-demo" \
  --port 8091 \
  --start-cmd "python3 -u -m http.server 8091 --bind 127.0.0.1" \
  --desc "A local HTTP server managed by Agent Dispatcher"

agents start dispatcher-demo
agents status dispatcher-demo
```

Visit **http://localhost:8091/**. You should see a directory listing, and the dashboard should show the application as running.

```bash
agents logs dispatcher-demo
agents restart dispatcher-demo
agents stop dispatcher-demo
```

To unregister the demo:

```bash
agents remove dispatcher-demo
```

Removing an application attempts to stop it first and removes its registry entry. It does not delete the application's source directory.

## Add your own applications

### Discover existing projects

Add your project directories to `scan_dirs` in `~/.config/agent_dispatcher/settings.json`, using absolute paths. Click **Scan** in the dashboard, or run:

```bash
agents scan
agents add --id discovered-project-id
```

Replace `discovered-project-id` with an ID returned by the scan. Discovery recognizes common Python entry points, shell launchers, some project manifests, and user service units in `~/.config/systemd/user/`.

Discovery is heuristic: it can find non-service projects or guess an unsuitable command or port. Review the saved registration before starting an imported application. Registered applications are marked to help avoid duplicates.

### Register a background application manually

Use the dashboard's **Add** form, or the same `agents add` flags shown in the demo. Supply `--type daemon` explicitly. Use absolute paths for your working directory and application-specific Python interpreter, and verify that the command works in a terminal first.

For applications with their own virtual environment, put that environment's Python executable in `start_cmd`, for example `/home/your-user/Projects/my-app/.venv/bin/python -u app.py`.

### Register systemd, Docker, or CLI applications

Edit `~/.config/agent_dispatcher/agents.json` while the dashboard is stopped. It is a JSON **array** of registrations. Add the objects below to that array, preserving existing entries and using a unique `id` for each application:

```json
[
  {
    "id": "my-service",
    "name": "My user service",
    "category": "system_service",
    "type": "systemd",
    "systemd_unit": "my-service.service",
    "systemd_user": true
  },
  {
    "id": "my-container",
    "name": "My Docker container",
    "category": "docker",
    "type": "docker",
    "container_name": "my-existing-container"
  },
  {
    "id": "my-tool",
    "name": "My command-line tool",
    "category": "cli_tool",
    "type": "cli",
    "working_dir": "/home/your-user/Projects/my-tool",
    "run_cmd": "/home/your-user/Projects/my-tool/.venv/bin/python main.py"
  }
]
```

Replace the sample names and paths with real ones. For a system-level systemd unit, use `"systemd_user": false`. Your account must already be allowed to manage that unit. For Docker, verify that `docker ps` works as your normal user; the dispatcher controls existing containers and does not create them.

The current Add form and manual CLI flags do not expose `systemd_unit`, `systemd_user`, `container_name`, or `run_cmd`; use JSON for these fields. User systemd units can also be imported through discovery.

Run a registered CLI tool in the foreground:

```bash
agents run my-tool input.txt
```

The dashboard displays a CLI tool's launch command; it does not provide an interactive terminal. General-purpose AI coding CLI IDs `claude`, `codex`, `agy`, and `grok` are excluded from registration.

## CLI reference

Replace `app-id` with the ID of a registered application.

| Command | Purpose |
| --- | --- |
| `agents` or `agents list` | List registered applications and their status. |
| `agents status app-id` | Inspect one application. |
| `agents start app-id` | Start a background application, unit, or container. |
| `agents stop app-id` | Stop an application. |
| `agents restart app-id` | Stop and start an application. |
| `agents logs app-id -n 100` | Read recent logs. |
| `agents logs app-id -f` | Follow an existing application log file. |
| `agents open app-id` | Open its web interface on the dispatcher's computer via `xdg-open`. |
| `agents run app-id input.txt` | Run a CLI tool with arguments. |
| `agents scan` | Discover candidate applications. |
| `agents add --id discovered-project-id` | Import a discovered candidate. |
| `agents remove app-id` | Attempt to stop the application and unregister it. |
| `agents health` | Inspect host resources and network addresses. |
| `agents lang en` | Save English as the interface language. |
| `agents web --host 127.0.0.1 --port 8800` | Start the local dashboard. |
| `agents --help` | Show available commands and options. |

`agents start all` and `agents stop all` operate on multiple registered applications. Use them only after reviewing your registry.

For one command, `agents --lang en list` overrides the display language. `AGENTS_LANG=en` overrides the saved language for the process. The supported language codes are `en`, `uk`, and `ru`.

For live systemd or Docker logs, use their native commands:

```bash
journalctl --user -u my-service.service -f
docker logs -f my-existing-container
```

## Configuration

| Location | Contents |
| --- | --- |
| `~/.config/agent_dispatcher/agents.json` | Application registry. |
| `~/.config/agent_dispatcher/settings.json` | Settings, including language and discovery directories. |
| `~/.local/state/agent_dispatcher/pids/` | PID files for managed processes. |
| `~/.local/state/agent_dispatcher/logs/` | Default logs for background applications. |

An example settings file:

```json
{
  "lang": "en",
  "scan_dirs": [
    "/home/your-user/Projects",
    "/home/your-user/apps"
  ]
}
```

Replace `your-user` and the directories with your actual paths. Paths in JSON must be absolute; `~` and `$HOME` are not expanded. Restart the dashboard after editing configuration files.

Background applications can additionally define `port`, `url`, `pid_file`, `log_file`, `stop_cmd`, and `venv_path`. See [the Agent model](dispatcher/models.py) for all fields. The `auto_start`, `health_endpoint`, and `restart_cmd` fields are currently reserved and do not implement automatic startup, HTTP health checks, or a custom restart action.

Daemon output is appended to its log file; log rotation is not implemented. Status is based on processes, service/container state, and ports rather than an application-level health check.

## Update

Stop the dashboard with `Ctrl+C`, then run these commands from the repository directory:

```bash
git pull --ff-only
.venv/bin/python -m pip install -r requirements.txt
agents web --host 127.0.0.1 --port 8800
```

Your registrations and settings are stored outside the checkout. Keep the checkout in its installation location. If you move it, recreate `.venv` at the new location and rerun `bash install_cli.sh` there.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Clone reports “Repository not found” or authentication fails | Verify the URL and your access to a private repository. For SSH, check your GitHub SSH-key setup. |
| `python3 -m venv` fails or reports missing `ensurepip` | On Ubuntu/Debian, install `python3-venv`. A separately installed Python may need its matching version-specific venv package. |
| `.venv/bin/python -m pip` reports no module named pip | Run `.venv/bin/python -m ensurepip --upgrade`. If the environment was created with `uv`, you can instead use `uv pip install --python .venv/bin/python -r requirements.txt`. |
| `agents: command not found` | Run `bash install_cli.sh` from the checkout and add `~/.local/bin` to `PATH`. You can use `.venv/bin/python cli.py` directly. |
| Flask or psutil cannot be imported | Install `requirements.txt` with the Python interpreter from this checkout's `.venv`. |
| The application list is empty | Register an application with `agents add`, or review the results of `agents scan`. |
| Dashboard reports “Address already in use” | Choose another port, for example `agents web --host 127.0.0.1 --port 8801`. |
| Scan finds no projects | Check `scan_dirs`, directory permissions, and the actual project layout. Discovery is limited; register the application manually when needed. |
| An application exits immediately | Check its log, working directory, Python environment, and start command. Its dependencies are separate from the dispatcher's dependencies. |
| systemd or Docker control fails | Verify the unit/container name and your permissions using `systemctl --user status my-service.service` or `docker ps`. |
| GPU statistics are missing | GPU reporting currently requires a supported NVIDIA driver and a working `nvidia-smi`. |
| The page has missing styles or icons | Check browser access to `cdn.tailwindcss.com` and `unpkg.com`; assets are not yet bundled locally. |

## Uninstall

Stop any applications you want to stop, then stop the dashboard. Remove the CLI shortcuts:

```bash
rm -- "$HOME/.local/bin/agents" "$HOME/.local/bin/agent-dispatch"
```

You can then delete the checkout. Configuration and logs remain in the locations listed above; back them up before removing them if you need a complete cleanup.

## License

[MIT](LICENSE) — Copyright (c) 2026 BeforeSteel.
