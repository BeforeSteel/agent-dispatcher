# Security Policy

## Supported versions

Agent Dispatcher has no tagged releases yet. Security fixes are made on the `master` branch only, so please make sure you can reproduce the problem on the latest `master` before reporting it.

## Reporting a vulnerability

**Please do not report security vulnerabilities in public issues, pull requests, or discussions.**

Report them privately through GitHub instead:

1. Open the [Security tab](https://github.com/BeforeSteel/agent-dispatcher/security) of this repository.
2. Click **Report a vulnerability** ([direct link](https://github.com/BeforeSteel/agent-dispatcher/security/advisories/new)).
3. Describe the problem and submit the form. Only the maintainers can see the report.

Please include:

- the affected component (web dashboard, HTTP API, CLI, discovery, systemd or Docker integration);
- the commit you tested (`git rev-parse --short HEAD`);
- steps to reproduce, or a minimal proof of concept;
- the impact you expect, for example who can trigger it and what they gain.

Remove personal data such as real paths, IP addresses, host names, and tokens from logs and screenshots before attaching them.

This is a personal project maintained on a best-effort basis. You will get a reply in the private report, and a fix will be coordinated with you before any public disclosure.

## Security model

Agent Dispatcher is designed to run on a single computer for one user. Keep these properties in mind when assessing an issue:

- The dashboard has **no built-in authentication**. Its HTTP API can register applications and run commands with the permissions of the user who started it.
- The dashboard is meant to listen on `127.0.0.1` and be reached locally or through an SSH tunnel. The current default host is `0.0.0.0`; always pass `--host 127.0.0.1` unless you understand the risk. See [Network access](README.md#6-start-the-dashboard).
- Registered applications, systemd units, and Docker containers are run as configured by the user. The dispatcher does not sandbox them.

Examples of issues that are **in scope**:

- cross-site scripting in the dashboard, for example through application names, descriptions, commands, or log output;
- a web page in the user's browser being able to call the local dashboard API (CSRF, DNS rebinding, missing origin checks);
- command or path injection through discovered project files, registry fields, or API parameters;
- reading or writing files outside the paths the user configured;
- the dashboard listening on an interface other than the one requested.

Examples of issues that are **out of scope**:

- command execution by someone who can already reach an unauthenticated dashboard that the user deliberately exposed to a network;
- vulnerabilities in the applications, services, or containers that the user registers;
- problems that require an attacker who already controls the user's account or configuration files.
