# NOISE_FILTER.md

Этот файл нужен, чтобы Codex не тратил время и токены на шум.

## Usually Exclude From Search

- `node_modules/`
- `.venv/`, `venv/`
- `.git/`
- `dist/`, `build/`, `out/`
- `.next/`, `.nuxt/`, `.cache/`
- coverage output
- generated client code
- lockfiles, если задача не про зависимости
- large fixtures
- logs
- binary assets
- vendor directories

## Usually Exclude From Context

- длинные логи команд;
- большие diff generated-файлов;
- snapshot-файлы без прямой необходимости;
- minified bundles;
- build artifacts;
- временные дампы и экспортированные данные.

## Exceptions

Не исключай эти файлы автоматически, если задача явно про:

- сборку;
- CI;
- зависимости;
- generated code;
- snapshots;
- production artifact mismatch.

## Search Rule

Перед широким поиском сначала реши, какие шумные директории и типы файлов не относятся к задаче.

Если есть сомнение, сначала ищи по целевым директориям, а не по всему репозиторию.
