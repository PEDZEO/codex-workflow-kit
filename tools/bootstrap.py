from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from common import detect_root


MANDATORY_ROOT_FILES = [
    "AGENTS.md",
    "OPERATING_RULES.md",
    "CODEBASE_INDEX.md",
    "TASK_INTAKE.md",
    "SEARCH_PLAYBOOK.md",
    "FILE_PRIORITY.md",
    "ACCEPTANCE_GATES.md",
    ".editorconfig",
    ".gitattributes",
]

MANDATORY_MEMORY_FILES = [
    "current-task.md",
    "handoffs.md",
    "done.md",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap mandatory workflow core into a target project")
    parser.add_argument("--target", required=True, help="Target project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument(
        "--memory-dir",
        default=".codex/memory",
        help="Relative memory directory to create in target project, default: .codex/memory",
    )
    return parser


def copy_file(src: Path, dst: Path, force: bool) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        return f"skip {dst}"
    shutil.copy2(src, dst)
    return f"copy {dst}"


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    kit_root = detect_root(Path(__file__).resolve().parent.parent)
    target_root = Path(args.target).resolve()
    target_root.mkdir(parents=True, exist_ok=True)

    results: list[str] = []
    for rel in MANDATORY_ROOT_FILES:
        results.append(copy_file(kit_root / rel, target_root / rel, args.force))

    source_memory_dir = kit_root / "memory"
    target_memory_dir = target_root / args.memory_dir
    for filename in MANDATORY_MEMORY_FILES:
        results.append(copy_file(source_memory_dir / filename, target_memory_dir / filename, args.force))

    print("Bootstrap completed:")
    for line in results:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

