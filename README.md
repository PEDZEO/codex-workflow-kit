# Codex Workflow Kit

[English](README.en.md) | Русский

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](tools/README.md)
[![Repository](https://img.shields.io/badge/GitHub-PEDZEO%2Fcodex--workflow--kit-black.svg)](https://github.com/PEDZEO/codex-workflow-kit)
[![CI](https://github.com/PEDZEO/codex-workflow-kit/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/PEDZEO/codex-workflow-kit/actions/workflows/ci.yml)

Строгий workflow-kit для Codex: быстрый поиск по репозиторию, короткая рабочая память, контролируемое делегирование агентам и жесткая приемка результата.

Этот набор нужен, если ты хочешь, чтобы Codex:
- не терял контекст между шагами;
- не тратил время на хаотичный поиск файлов;
- не раздувал токены длинным контекстом;
- делегировал работу агентам по правилам, а не случайно;
- не завершал задачу без явной проверки.

Repository: `https://github.com/PEDZEO/codex-workflow-kit`

## Что это дает

Система строится на четырех вещах:

1. Один источник правды по текущей задаче  
   `current-task.md` держит живое состояние работы и не дает контексту расползтись по чату и случайным заметкам.

2. Жесткий порядок старта и поиска  
   Codex сначала читает индекс и task intake, затем идет в узкий поиск, а не сканирует репозиторий вслепую.

3. Контролируемое делегирование  
   У агента всегда есть ownership, out-of-scope и критерий готовности.

4. Явная приемка  
   Задача не считается завершенной, пока не пройдены acceptance gates.

## Для кого это

Подходит, если ты работаешь с Codex:
- в длинных инженерных сессиях;
- в больших или средних репозиториях;
- в проектах, где важны точечные изменения и низкий риск регрессий;
- в командах, где хочется повторяемого процесса, а не “каждый раз по-разному”.

## Требования

- Git
- Python 3.10+
- `rg` (`ripgrep`) рекомендуется для быстрого поиска

## Установка

### Linux

```bash
git clone https://github.com/PEDZEO/codex-workflow-kit.git
cd codex-workflow-kit
python3 --version
python3 tools/bootstrap.py --target ../my-project
```

Если `ripgrep` еще не установлен:

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

## Installation Mode

Bootstrap now installs the full workflow kit by default.

That includes:
- core workflow documents
- support workflow documents
- memory templates
- CLI tools
- examples and templates

If you only want the old reduced install, use:

```powershell
python tools/bootstrap.py --target ..\my-project --profile core
```

## Mandatory Core

Если нужна именно жесткая система, а не просто набор подсказок, обязательны эти файлы:

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

Без этого ядра набор заметно слабее и легко превращается в декоративную документацию.

## Optional Support Files

Эти файлы усиливают workflow, но не являются минимальным ядром:

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

Это развернет весь workflow kit в целевой проект, не затирая существующие файлы без `--force`.

### Ручное внедрение

1. Скопируй `AGENTS.md` и `OPERATING_RULES.md` в корень проекта.
2. Скопируй `CODEBASE_INDEX.md`, `TASK_INTAKE.md`, `SEARCH_PLAYBOOK.md`, `FILE_PRIORITY.md`, `ACCEPTANCE_GATES.md` в корень проекта.
3. Создай `.codex/memory/` и положи туда:
   - `current-task.md`
   - `handoffs.md`
   - `done.md`
4. Добавь `.editorconfig` и `.gitattributes`.
5. Заполни `CODEBASE_INDEX.md` и `TASK_INTAKE.md` под свой проект.

## Базовый рабочий цикл

На практике Codex должен работать так:

1. Прочитать `CODEBASE_INDEX.md`, `TASK_INTAKE.md`, `current-task.md`.
2. Сделать короткий план.
3. Искать только узко: `rg --files` -> `rg` -> точечное чтение.
4. Вести живое состояние только в `current-task.md`.
5. Делегировать только задачи с ownership.
6. После изменений пройти `ACCEPTANCE_GATES.md`.
7. Перенести завершенное в `done.md`.

## Python Tools

В `tools/` уже есть CLI для принуждения к процессу:

- `scan_project.py` — собрать структурированный JSON summary проекта
- `init_index.py` — сгенерировать черновик `CODEBASE_INDEX.md`
- `init_test_index.py` — сгенерировать черновик `TEST_INDEX.md`
- `init_change_areas.py` — сгенерировать черновик `CHANGE_AREAS.md`
- `refresh_index.py` — обновить машинные секции существующего `CODEBASE_INDEX.md`
- `explain_scan.py` — объяснить, что именно сканер нашел и почему
- `bootstrap.py` — развернуть mandatory core в новый проект
- `scaffold_task.py` — создать или обновить `current-task.md`
- `create_handoff.py` — добавить structured handoff
- `close_task.py` — закрыть задачу и перенести итог в `done.md`
- `validate_workflow.py` — проверить наличие mandatory core и дисциплину памяти
- `acceptance_check.py` — явно пройти acceptance gates

Подробности и примеры запуска: [tools/README.md](tools/README.md)

## Структура после bootstrap

После разворачивания mandatory core проект будет выглядеть примерно так:

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

## Правила, которые нельзя размывать

Если хочешь, чтобы система реально держала контекст, эти правила должны соблюдаться всегда:

1. У текущей задачи один источник правды: `.codex/memory/current-task.md`.
2. Нельзя начинать с хаотичного чтения дерева, если индекс и intake уже существуют.
3. После исследования всегда нужен короткий summary.
4. Нельзя делегировать без ownership и out-of-scope.
5. Нельзя завершать задачу без acceptance check.

## Репозиторные файлы

- `.editorconfig` — единые правила кодировки и переводов строк
- `.gitattributes` — нормализация текстовых файлов для Git
- `.gitignore` — исключение локального runtime-мусора
- `LICENSE` — MIT
- `CHANGELOG.md` — история заметных изменений
- `CONTRIBUTING.md` — правила и ожидания для внешних вкладов

## Ограничения

Этот kit не пытается:
- автоматически понять архитектуру проекта;
- сам заполнять индекс проекта качественно;
- заменить инженерное мышление;
- магически решить плохую декомпозицию задач.

Его задача другая: сделать хороший workflow обязательным и дешевым в использовании.

## Рекомендованный порядок внедрения

1. Сначала внедрить mandatory core.
2. Потом заполнить `CODEBASE_INDEX.md`.
3. Потом добавить optional support files по мере необходимости.
4. Потом подключить Python tools в ежедневный процесс.
5. Только после этого расширять kit дальше.

## License

MIT. См. [LICENSE](LICENSE).

## Дополнительно

- [English README](README.en.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
