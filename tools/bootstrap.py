from __future__ import annotations

import argparse
import shutil
from pathlib import Path

try:
    from .common import detect_root
except ImportError:  # pragma: no cover - direct script execution
    from common import detect_root


CORE_ROOT_FILES = [
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

SUPPORT_ROOT_FILES = [
    "TEST_INDEX.md",
    "CHANGE_AREAS.md",
    "FINAL_REPORT.md",
    "NOISE_FILTER.md",
    "RISK_PATTERNS.md",
    "TASK_SIZE_RULES.md",
]

CORE_MEMORY_FILES = [
    "current-task.md",
    "handoffs.md",
    "done.md",
]

SUPPORT_MEMORY_FILES = [
    "decisions.md",
]

COPY_DIRS = [
    "tools",
    "templates",
    "examples",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap the full Codex workflow kit into a target project")
    parser.add_argument("--target", required=True, help="Target project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    parser.add_argument("--dry-run", action="store_true", help="Show planned changes without writing files")
    parser.add_argument("--skip-memory", action="store_true", help="Do not copy memory template files")
    parser.add_argument(
        "--memory-dir",
        default=".codex/memory",
        help="Relative memory directory to create in target project, default: .codex/memory",
    )
    parser.add_argument(
        "--profile",
        choices=["full", "core"],
        default="full",
        help="Install profile. Default is full.",
    )
    return parser


def copy_file(src: Path, dst: Path, force: bool, dry_run: bool = False) -> str:
    if dry_run:
        if dst.exists() and not force:
            return f"would skip {dst}"
        return f"would copy {dst}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        return f"skip {dst}"
    shutil.copy2(src, dst)
    return f"copy {dst}"


def copy_tree(src: Path, dst: Path, force: bool, dry_run: bool = False) -> list[str]:
    results: list[str] = []
    if not src.exists():
        return results
    for path in src.rglob("*"):
        if path.is_dir():
            continue
        if "__pycache__" in path.parts:
            continue
        rel = path.relative_to(src)
        results.append(copy_file(path, dst / rel, force, dry_run=dry_run))
    return results


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    kit_root = detect_root(Path(__file__).resolve().parent.parent)
    target_root = Path(args.target).resolve()
    if not args.dry_run:
        target_root.mkdir(parents=True, exist_ok=True)

    results: list[str] = []
    root_files = list(CORE_ROOT_FILES)
    memory_files = list(CORE_MEMORY_FILES)
    if args.profile == "full":
        root_files.extend(SUPPORT_ROOT_FILES)
        memory_files.extend(SUPPORT_MEMORY_FILES)

    for rel in root_files:
        results.append(copy_file(kit_root / rel, target_root / rel, args.force, dry_run=args.dry_run))

    if not args.skip_memory:
        source_memory_dir = kit_root / "memory"
        target_memory_dir = target_root / args.memory_dir
        for filename in memory_files:
            results.append(
                copy_file(source_memory_dir / filename, target_memory_dir / filename, args.force, dry_run=args.dry_run)
            )

    if args.profile == "full":
        for directory in COPY_DIRS:
            results.extend(copy_tree(kit_root / directory, target_root / directory, args.force, dry_run=args.dry_run))

    print("Bootstrap dry run:" if args.dry_run else "Bootstrap completed:")
    for line in results:
        print(f"- {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
