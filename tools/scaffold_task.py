from __future__ import annotations

import argparse
from textwrap import dedent

from common import workflow_paths, write_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create or replace .codex/memory/current-task.md")
    parser.add_argument("--memory-dir", default=None, help="Relative memory directory, default: .codex/memory")
    parser.add_argument("--goal", required=True, help="Primary task goal")
    parser.add_argument("--done-criteria", default="", help="Definition of done")
    parser.add_argument("--constraints", default="", help="Constraints or non-goals")
    parser.add_argument("--scope", default="", help="Files, modules, or areas in scope")
    parser.add_argument("--tests", default="", help="Relevant tests or verification targets")
    parser.add_argument("--next-step", default="", help="Immediate next local step")
    parser.add_argument("--delegate", default="", help="Delegable side work")
    return parser


def render(args: argparse.Namespace) -> str:
    return dedent(
        f"""\
        # current-task.md

        ## Goal

        - Что нужно сделать: {args.goal}
        - Критерий готовности: {args.done_criteria or 'Уточнить и заполнить'}

        ## Constraints

        - Ограничения: {args.constraints or 'Уточнить и заполнить'}
        - Что нельзя ломать: Уточнить и заполнить

        ## Scope

        - Файлы в работе: {args.scope or 'Уточнить и заполнить'}
        - Подозреваемые файлы: Уточнить по поиску
        - Тесты в зоне риска: {args.tests or 'Уточнить и заполнить'}

        ## Current Understanding

        - Что уже подтверждено: Стартовая заготовка создана
        - Что еще не подтверждено: Нужен первый проход по коду

        ## Next Steps

        - Следующий локальный шаг: {args.next_step or 'Построить короткий план и уточнить рабочую зону'}
        - Что можно делегировать: {args.delegate or 'Пока не определено'}

        ## Notes To Keep

        - Короткие выводы, не сырые логи.
        - Держать файл в пределах 30 строк, если нет особой причины расширять.
        """
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    paths = workflow_paths(memory_dir_rel=args.memory_dir)
    write_text(paths.current_task, render(args))
    print(f"Updated {paths.current_task}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
