# CODEBASE_INDEX.md

Заполняется один раз и поддерживается в коротком актуальном виде.

## Project Summary

- Project name: codex-workflow-kit
- Main purpose: Needs review
- Primary language: Python
- Frameworks: Needs review
- Package manager: pip/pyproject
- Test runner: Needs review

## Entry Points

- tools/acceptance_check.py  (runtime entrypoint pattern, main function pattern)
- tools/bootstrap.py  (runtime entrypoint pattern, main function pattern)
- tools/close_task.py  (runtime entrypoint pattern, main function pattern)
- tools/create_handoff.py  (runtime entrypoint pattern, main function pattern)
- tools/explain_scan.py  (runtime entrypoint pattern, main function pattern)
- tools/init_change_areas.py  (runtime entrypoint pattern, main function pattern)
- tools/init_index.py  (runtime entrypoint pattern, main function pattern)
- tools/refresh_index.py  (runtime entrypoint pattern, main function pattern)

## Main Directories

- `.github/`
  - Needs review
- `examples/`
  - Needs review
- `memory/`
  - Needs review
- `templates/`
  - Needs review
- `tests/`
  - Tests
- `tools/`
  - Automation and utility scripts

## Important Files

- .github/workflows/ci.yml
- pyproject.toml

## Key Flows

- Auth flow:
- Request flow:
- Background jobs:
- Notification flow:
- Data persistence:

## Search Shortcuts

Указывать только реально полезные точки входа:

- Routing files:
- Shared types:
- Main services:
- Repositories or data layer:
- UI state or handlers:
- Alerting or logging:

## Test Map

- Test directories: tests
- Detected test files: 1
- Sample test files:
- tests/test_workflow_tools.py

## Common Commands

```text
# codex-workflow-bootstrap
tools.bootstrap:main

# codex-workflow-scan
tools.scan_project:main

# codex-workflow-validate
tools.validate_workflow:main

# codex-workflow-acceptance
tools.acceptance_check:main
```

## Notes For Codex

- Сначала смотри сюда, потом ищи по дереву.
- Если структура проекта изменилась, обнови этот файл.
- Не превращай индекс в длиннюю документацию.

## CI Files

- .github/workflows/ci.yml

## Area Hints

- No area hints detected automatically
