# Codex Workflow Kit

English | [Русский](README.md)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](tools/README.md)
[![Repository](https://img.shields.io/badge/GitHub-PEDZEO%2Fcodex--workflow--kit-black.svg)](https://github.com/PEDZEO/codex-workflow-kit)
[![CI](https://github.com/PEDZEO/codex-workflow-kit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/PEDZEO/codex-workflow-kit/actions/workflows/ci.yml)

Strict workflow kit for Codex: narrow repository search, short working memory, controlled agent delegation, and explicit acceptance before closing work.

Use this repository when you want Codex to:
- keep context between steps;
- avoid wandering through files;
- spend fewer tokens on repeated context;
- delegate with explicit ownership;
- avoid closing tasks without verification.

Repository: `https://github.com/PEDZEO/codex-workflow-kit`

## What It Provides

The system is built around four ideas:

1. One source of truth for the active task  
   `current-task.md` holds the live state of work and prevents the task from spreading across chat messages and temporary notes.

2. A strict start and search sequence  
   Codex reads the index and task intake first, then performs narrow search instead of broad repository wandering.

3. Controlled delegation  
   Each agent gets ownership, out-of-scope boundaries, and a done condition.

4. Explicit acceptance  
   Work is not considered finished until acceptance gates are passed.

## Requirements

- Git
- Python 3.10+
- `rg` (`ripgrep`) is recommended for fast search

## Installation

### Linux

```bash
git clone https://github.com/PEDZEO/codex-workflow-kit.git
cd codex-workflow-kit
python3 --version
python3 tools/bootstrap.py --target ../my-project
```

If `ripgrep` is not installed yet:

```bash
# Ubuntu / Debian
sudo apt-get update && sudo apt-get install -y ripgrep

# Fedora
sudo dnf install -y ripgrep

# Arch
sudo pacman -S ripgrep
```

### Windows

```powershell
git clone https://github.com/PEDZEO/codex-workflow-kit.git
cd codex-workflow-kit
python --version
python tools/bootstrap.py --target ..\my-project
```

## Mandatory Core

These files are the minimum required set for the workflow to stay strict:

- `AGENTS.md`
- `OPERATING_RULES.md`
- `CODEBASE_INDEX.md`
- `TASK_INTAKE.md`
- `SEARCH_PLAYBOOK.md`
- `FILE_PRIORITY.md`
- `.codex/memory/current-task.md`
- `.codex/memory/handoffs.md`
- `.codex/memory/done.md`
- `ACCEPTANCE_GATES.md`

Without this core, the kit becomes documentation instead of an operating workflow.

## Optional Support Files

These files improve the workflow, but are not part of the absolute minimum:

- `TEST_INDEX.md`
- `CHANGE_AREAS.md`
- `FINAL_REPORT.md`
- `NOISE_FILTER.md`
- `RISK_PATTERNS.md`
- `TASK_SIZE_RULES.md`
- `.codex/memory/decisions.md`
- `templates/`
- `examples/`

## Quick Start

### Linux

```bash
python3 tools/bootstrap.py --target ../my-project
```

### Windows

```powershell
python tools/bootstrap.py --target ..\my-project
```

This bootstraps the mandatory core into the target project without overwriting existing files unless `--force` is used.

### Manual Setup

1. Copy `AGENTS.md` and `OPERATING_RULES.md` into the project root.
2. Copy `CODEBASE_INDEX.md`, `TASK_INTAKE.md`, `SEARCH_PLAYBOOK.md`, `FILE_PRIORITY.md`, and `ACCEPTANCE_GATES.md` into the project root.
3. Create `.codex/memory/` and add:
   - `current-task.md`
   - `handoffs.md`
   - `done.md`
4. Add `.editorconfig` and `.gitattributes`.
5. Fill in `CODEBASE_INDEX.md` and `TASK_INTAKE.md` for the real project.

## Basic Working Loop

Codex should operate like this:

1. Read `CODEBASE_INDEX.md`, `TASK_INTAKE.md`, and `current-task.md`.
2. Build a short plan.
3. Search narrowly: `rg --files` -> `rg` -> targeted reads.
4. Keep live task state only in `current-task.md`.
5. Delegate only tasks with explicit ownership.
6. Pass `ACCEPTANCE_GATES.md` before closing work.
7. Move completed work into `done.md`.

## Python Tools

`tools/` already includes CLI commands that enforce the workflow:

- `bootstrap.py` — bootstrap the mandatory core into a new project
- `scaffold_task.py` — create or replace `current-task.md`
- `create_handoff.py` — append a structured handoff
- `close_task.py` — archive a completed task into `done.md`
- `validate_workflow.py` — validate the mandatory core and memory discipline
- `acceptance_check.py` — explicitly pass acceptance gates

More details and command examples: [tools/README.md](tools/README.md)

## Structure After Bootstrap

```text
my-project/
|-- .codex/
|   `-- memory/
|       |-- current-task.md
|       |-- handoffs.md
|       `-- done.md
|-- .editorconfig
|-- .gitattributes
|-- ACCEPTANCE_GATES.md
|-- AGENTS.md
|-- CODEBASE_INDEX.md
|-- FILE_PRIORITY.md
|-- OPERATING_RULES.md
|-- SEARCH_PLAYBOOK.md
`-- TASK_INTAKE.md
```

## Rules That Should Not Drift

1. The active task has one source of truth: `.codex/memory/current-task.md`.
2. Do not start with broad file browsing if the index and intake already exist.
3. Research must collapse into a short summary.
4. Delegation requires ownership and out-of-scope boundaries.
5. Do not close work without an acceptance check.

## Repo Files

- `.editorconfig` — consistent encoding and line endings
- `.gitattributes` — text normalization for Git
- `.gitignore` — local runtime and editor noise
- `LICENSE` — MIT

## Limits

This kit does not try to:
- understand your architecture automatically;
- fill project maps perfectly on its own;
- replace engineering judgment;
- fix poor task decomposition by magic.

Its goal is different: make a good workflow cheap to follow and expensive to ignore.

## Recommended Adoption Order

1. Adopt the mandatory core first.
2. Fill `CODEBASE_INDEX.md`.
3. Add optional support files as needed.
4. Use the Python tools in day-to-day work.
5. Expand the kit only after the core process is stable.

## License

MIT. See [LICENSE](LICENSE).
