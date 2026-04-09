from __future__ import annotations

import argparse


GATES = {
    "scope": "Изменены только нужные зоны и нет случайных правок вне задачи",
    "behavior": "Изменение закрывает исходную задачу и не ломает соседний сценарий",
    "verification": "Запущена минимальная достаточная проверка или непроверенное явно отмечено",
    "regression": "Проверены релевантные риски и нет явного contract drift",
    "memory": "Память обновлена кратко и без логов",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check mandatory acceptance gates before closing a task")
    parser.add_argument("--scope", action="store_true")
    parser.add_argument("--behavior", action="store_true")
    parser.add_argument("--verification", action="store_true")
    parser.add_argument("--regression", action="store_true")
    parser.add_argument("--memory", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    missing = [name for name in GATES if not getattr(args, name)]
    if missing:
        print("Acceptance check failed. Missing gates:")
        for key in missing:
            print(f"- {key}: {GATES[key]}")
        return 1

    print("Acceptance check passed.")
    for key, text in GATES.items():
        print(f"- {key}: {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

