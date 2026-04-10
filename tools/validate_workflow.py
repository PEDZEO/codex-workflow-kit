from __future__ import annotations

import argparse
from pathlib import Path
import tempfile

try:
    from .common import MEMORY_FILES, ROOT_FILES, count_nonempty_lines, read_text, workflow_paths
except ImportError:  # pragma: no cover - direct script execution
    from common import MEMORY_FILES, ROOT_FILES, count_nonempty_lines, read_text, workflow_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate mandatory workflow files and basic discipline rules")
    parser.add_argument("--memory-dir", default=None, help="Relative memory directory, default: .codex/memory")
    parser.add_argument("--max-current-lines", type=int, default=30, help="Maximum non-empty lines allowed in current-task.md")
    parser.add_argument("--skip-write-check", action="store_true", help="Skip checking whether the memory directory is writeable")
    return parser


def validate_root_files(root: Path) -> list[str]:
    errors: list[str] = []
    for rel in ROOT_FILES:
        path = root / rel
        if not path.exists():
            errors.append(f"Missing mandatory file: {rel}")
        elif not read_text(path).strip():
            errors.append(f"Mandatory file is empty: {rel}")
    return errors


def validate_memory_writeability(memory_dir: Path) -> list[str]:
    try:
        memory_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=memory_dir,
            prefix=".workflow-write-check-",
            delete=True,
        ) as handle:
            handle.write("ok\n")
            handle.flush()
    except OSError as exc:
        return [f"Memory directory is not writeable: {memory_dir} ({exc})"]
    return []


def validate_memory_files(
    root: Path,
    max_current_lines: int,
    memory_dir_rel: str | None,
    skip_write_check: bool,
) -> list[str]:
    errors: list[str] = []
    memory_dir = memory_dir_rel or ".codex/memory"
    for rel in MEMORY_FILES:
        filename = Path(rel).name
        path = root / memory_dir / filename
        if not path.exists():
            errors.append(f"Missing memory file: {memory_dir}/{filename}")
        elif not read_text(path).strip():
            errors.append(f"Memory file is empty: {memory_dir}/{filename}")

    paths = workflow_paths(root, memory_dir_rel=memory_dir_rel)
    if paths.current_task.exists():
        current_lines = count_nonempty_lines(read_text(paths.current_task))
        if current_lines > max_current_lines:
            errors.append(
                f"current-task.md is too long: {current_lines} non-empty lines, max allowed is {max_current_lines}"
            )
    if not skip_write_check:
        errors.extend(validate_memory_writeability(paths.memory_dir))
    return errors


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    paths = workflow_paths(memory_dir_rel=args.memory_dir)
    errors = [
        *validate_root_files(paths.root),
        *validate_memory_files(paths.root, args.max_current_lines, args.memory_dir, args.skip_write_check),
    ]

    if errors:
        print("Workflow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Workflow validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
