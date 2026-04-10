from __future__ import annotations

import argparse
import subprocess

try:
    from .common import configure_stdout, read_text, workflow_paths
except ImportError:  # pragma: no cover - direct script execution
    from common import configure_stdout, read_text, workflow_paths


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
    parser.add_argument("--memory-dir", default=None, help="Relative memory directory, default: .codex/memory")
    parser.add_argument("--require-clean-git", action="store_true", help="Fail if git status has tracked changes")
    parser.add_argument(
        "--require-current-task-updated",
        action="store_true",
        help="Fail if current-task.md still matches the distributed template",
    )
    parser.add_argument("--verification-command", default="", help="Optional verification command to execute")
    return parser


def git_status_is_clean() -> tuple[bool, str]:
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, check=False)
    output = result.stdout.strip()
    if result.returncode != 0:
        return False, result.stderr.strip() or "git status failed"
    tracked_changes = [line for line in output.splitlines() if line and not line.startswith("??")]
    if tracked_changes:
        return False, "\n".join(tracked_changes)
    return True, ""


def current_task_is_updated(memory_dir_rel: str | None) -> tuple[bool, str]:
    paths = workflow_paths(memory_dir_rel=memory_dir_rel)
    template_path = paths.root / "memory" / "current-task.md"
    if not paths.current_task.exists():
        return False, f"Missing {paths.current_task}"
    current = read_text(paths.current_task).strip()
    if not current:
        return False, f"{paths.current_task} is empty"
    if template_path.exists() and current == read_text(template_path).strip():
        return False, f"{paths.current_task} still matches {template_path}"
    return True, ""


def run_verification_command(command: str) -> tuple[bool, str]:
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    output = "\n".join(part for part in (result.stdout.strip(), result.stderr.strip()) if part)
    return result.returncode == 0, output


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    missing = [name for name in GATES if not getattr(args, name)]
    if missing:
        print("Acceptance check failed. Missing gates:")
        for key in missing:
            print(f"- {key}: {GATES[key]}")
        return 1

    errors: list[str] = []
    if args.require_clean_git:
        ok, detail = git_status_is_clean()
        if not ok:
            errors.append(f"git status is not clean:\n{detail}")
    if args.require_current_task_updated:
        ok, detail = current_task_is_updated(args.memory_dir)
        if not ok:
            errors.append(detail)
    if args.verification_command:
        ok, detail = run_verification_command(args.verification_command)
        if not ok:
            errors.append(f"verification command failed: {args.verification_command}\n{detail}")

    if errors:
        print("Acceptance check failed. Failed concrete checks:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Acceptance check passed.")
    for key, text in GATES.items():
        print(f"- {key}: {text}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
