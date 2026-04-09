# Tools

Эти скрипты превращают markdown-процесс в более жесткий workflow.

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

### bootstrap.py

Разворачивает mandatory core в новый проект.

```powershell
python tools/bootstrap.py --target ..\my-project
```

С перезаписью существующих workflow-файлов:

```powershell
python tools/bootstrap.py --target ..\my-project --force
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

## Notes

- Скрипты специально простые и предсказуемые.
- Они не пытаются анализировать архитектуру за тебя.
- Их цель: сделать нарушение процесса более заметным и дорогим.
- `bootstrap.py` копирует только mandatory core, а не весь kit целиком.
