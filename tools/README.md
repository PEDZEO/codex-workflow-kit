# Tools

Эти скрипты превращают markdown-процесс в более жесткий workflow.

CI smoke-check for the CLI lives in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

## Requirements

- Python 3.10+
- запуск из корня `codex-workflow-kit` или из проекта, где уже лежат `AGENTS.md` и `OPERATING_RULES.md`
- по умолчанию скрипты пишут в `.codex/memory/`
- если среда запрещает запись в скрытую `.codex/`, используй `--memory-dir memory`

## Linux Quick Start

```bash
python3 tools/bootstrap.py --target ../my-project
python3 tools/validate_workflow.py
```

Это стандартный режим для реального проекта с `.codex/memory`.

## Windows Quick Start

```powershell
python tools/bootstrap.py --target ..\my-project
python tools\validate_workflow.py
```

Если среда блокирует запись в скрытую `.codex/`, используй `--memory-dir memory` как fallback для template или sandbox режима.

## Commands

### scan_project.py

Сканирует репозиторий и выводит структурированный JSON summary.

```powershell
python tools/scan_project.py --target .
```

Можно писать в файл:

```powershell
python tools/scan_project.py --target . --output scan-summary.json
```

### init_index.py

Генерирует черновик `CODEBASE_INDEX` на основе structural scan.

```powershell
python tools/init_index.py --target . --output CODEBASE_INDEX.generated.md
```

JSON-режим в stdout:

```powershell
python tools/init_index.py --target . --format json --output -
```

### init_test_index.py

Генерирует черновик `TEST_INDEX` на основе scan summary и команд проекта.

```powershell
python tools/init_test_index.py --target . --output TEST_INDEX.generated.md
```

Markdown в stdout:

```powershell
python tools/init_test_index.py --target . --output -
```

### init_change_areas.py

Генерирует черновик `CHANGE_AREAS` на основе directory и entrypoint heuristics.

```powershell
python tools/init_change_areas.py --target . --output CHANGE_AREAS.generated.md
```

JSON-режим:

```powershell
python tools/init_change_areas.py --target . --format json --output -
```

### refresh_index.py

Обновляет машинные секции существующего `CODEBASE_INDEX.md` без полного перетирания файла.

```powershell
python tools/refresh_index.py --target . --index CODEBASE_INDEX.md
```

### explain_scan.py

Кратко объясняет, что scanner обнаружил и почему.

```powershell
python tools/explain_scan.py --target .
```

Markdown-режим:

```powershell
python tools/explain_scan.py --target . --format markdown
```

### bootstrap.py

Разворачивает mandatory core в новый проект.

```powershell
python tools/bootstrap.py --target ..\my-project
```

С перезаписью существующих workflow-файлов:

```powershell
python tools/bootstrap.py --target ..\my-project --force
```

Только core-профиль:

```powershell
python tools/bootstrap.py --target ..\my-project --profile core
```

Preview what bootstrap would do without writing files:

```powershell
python tools/bootstrap.py --target ..\my-project --dry-run
```

Update an existing local install without resetting live memory:

```powershell
python tools/bootstrap.py --target ..\my-project --force --skip-memory
```

### scaffold_task.py

Создает или полностью обновляет `.codex/memory/current-task.md`.

```powershell
python tools/scaffold_task.py --goal "Fix session pagination" --scope "bot/sessions, handlers" --tests "tests/test_sessions.py"
```

Пример для template/sandbox режима:

```powershell
python tools/scaffold_task.py --memory-dir memory --goal "Fix session pagination"
```

### create_handoff.py

Добавляет новую запись в `.codex/memory/handoffs.md`.

```powershell
python tools/create_handoff.py --role worker --objective "Update session keyboard callbacks" --owned-files "bot/keyboards/sessions.py" --out-of-scope "handlers, server"
```

### close_task.py

Архивирует задачу в `.codex/memory/done.md` и сбрасывает `current-task.md`.

```powershell
python tools/close_task.py --task "Fix session pagination" --files "bot/keyboards/sessions.py, tests/test_sessions.py" --verification "pytest tests/test_sessions.py"
```

### validate_workflow.py

Проверяет наличие mandatory core-файлов и базовую дисциплину памяти.

```powershell
python tools/validate_workflow.py
```

Для template/sandbox режима:

```powershell
python tools/validate_workflow.py --memory-dir memory
```

### acceptance_check.py

Требует явно отметить обязательные ворота приемки.

```powershell
python tools/acceptance_check.py --scope --behavior --verification --regression --memory
```

With concrete checks:

```powershell
python tools/acceptance_check.py --scope --behavior --verification --regression --memory --require-current-task-updated --verification-command "python -B -m unittest discover -s tests -v"
```

### Local test command

```powershell
python -B -m unittest discover -s tests -v
```

## Notes

- Скрипты специально простые и предсказуемые.
- Они не пытаются анализировать архитектуру за тебя.
- Их цель: сделать нарушение процесса более заметным и дорогим.
- `bootstrap.py` по умолчанию копирует весь workflow kit; `--profile core` оставляет только уменьшенный набор.
- `scan_project.py` и `init_index.py` строят черновик архитектурной карты, но не заменяют ручной review.
- `init_test_index.py` и `init_change_areas.py` дают черновики для test map и change areas, а не финальную архитектурную истину.
- `refresh_index.py` обновляет только машинные секции и должен использоваться поверх уже просмотренного человеком индекса.
- Генераторы поддерживают `--output -` для stdout и `--format json` там, где это имеет смысл.
