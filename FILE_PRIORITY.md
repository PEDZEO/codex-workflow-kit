# FILE_PRIORITY.md

Используй этот порядок, чтобы быстрее выходить на рабочую область.

## Read Order

1. `CODEBASE_INDEX.md`
2. `TASK_INTAKE.md`
3. entrypoints
4. routing, handlers, callbacks
5. main services or business logic
6. schemas, types, contracts
7. repositories or persistence layer
8. related tests
9. shared helpers
10. secondary utilities

## Why

- Entry points показывают, где начинается реальный поток.
- Handlers и routes показывают, где поведение ветвится.
- Services показывают основную бизнес-логику.
- Types и contracts показывают реальные ограничения.
- Tests подтверждают ожидаемое поведение.

## Large Repo Rule

Если репозиторий большой:

- не начинай с shared utils;
- не начинай с случайного search hit;
- не уходи в helpers до тех пор, пока не найден основной flow.

## Test Position

Тесты читать после того, как понятна рабочая зона, но до широкой реализации.
