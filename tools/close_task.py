from __future__ import annotations

import argparse
from datetime import date
from textwrap import dedent

try:
    from .common import read_text, workflow_paths, write_text
except ImportError:  # pragma: no cover - direct script execution
    from common import read_text, workflow_paths, write_text


RESET_TEMPLATE = dedent(
    """\
    # current-task.md

    ## Goal

    - Что нужно сделать:
    - Критерий готовности:

    ## Constraints

    - Ограничения:
    - Что нельзя ломать:

    ## Scope

    - Файлы в работе:
    - Подозреваемые файлы:
    - Тесты в зоне риска:

    ## Current Understanding

    - Что уже подтверждено:
    - Что еще не подтверждено:

    ## Next Steps

    - Следующий локальный шаг:
    - Что можно делегировать:

    ## Notes To Keep

    - Короткие выводы, не сырые логи.
    - Держать файл в пределах 30 строк, если нет особой причины расширять.
    """
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Archive current task into .codex/memory/done.md and reset current-task.md")
    parser.add_argument("--memory-dir", default=None, help="Relative memory directory, default: .codex/memory")
    parser.add_argument("--task", required=True, help="Short task title")
    parser.add_argument("--files", default="Не указано", help="Changed files or affected area")
    parser.add_argument("--verification", default="Не указано")
    parser.add_argument("--risk", default="Нет явных рисков")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    paths = workflow_paths(memory_dir_rel=args.memory_dir)

    done_existing = read_text(paths.done) if paths.done.exists() else "# done.md\n\n## Completed\n"
    entry = dedent(
        f"""\
        - Date:
          - Task: {args.task}
          - Files changed: {args.files}
          - Verification: {args.verification}
          - Remaining risk: {args.risk}
          - Closed on: {date.today().isoformat()}
        """
    )
    write_text(paths.done, done_existing.rstrip() + "\n\n" + entry)
    write_text(paths.current_task, RESET_TEMPLATE)
    print(f"Archived task into {paths.done}")
    print(f"Reset {paths.current_task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
