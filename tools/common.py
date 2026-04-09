from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


ROOT_FILES = [
    "AGENTS.md",
    "OPERATING_RULES.md",
    "CODEBASE_INDEX.md",
    "TASK_INTAKE.md",
    "SEARCH_PLAYBOOK.md",
    "FILE_PRIORITY.md",
    "ACCEPTANCE_GATES.md",
]

MEMORY_FILES = [
    ".codex/memory/current-task.md",
    ".codex/memory/handoffs.md",
    ".codex/memory/done.md",
]


@dataclass(frozen=True)
class WorkflowPaths:
    root: Path
    memory_dir: Path
    current_task: Path
    handoffs: Path
    done: Path
    decisions: Path


def detect_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "AGENTS.md").exists() and (candidate / "OPERATING_RULES.md").exists():
            return candidate
    return current


def workflow_paths(root: Path | None = None, memory_dir_rel: str | None = None) -> WorkflowPaths:
    base = detect_root(root)
    configured_memory_dir = memory_dir_rel or os.environ.get("CODEX_WORKFLOW_MEMORY_DIR", ".codex/memory")
    memory_dir = base / configured_memory_dir
    return WorkflowPaths(
        root=base,
        memory_dir=memory_dir,
        current_task=memory_dir / "current-task.md",
        handoffs=memory_dir / "handoffs.md",
        done=memory_dir / "done.md",
        decisions=memory_dir / "decisions.md",
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalize_newlines(text), encoding="utf-8", newline="\n")


def normalize_newlines(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if not normalized.endswith("\n"):
        normalized += "\n"
    return normalized


def file_exists_and_has_content(path: Path) -> bool:
    return path.exists() and bool(read_text(path).strip())


def count_nonempty_lines(text: str) -> int:
    return sum(1 for line in text.splitlines() if line.strip())


def append_section(path: Path, section: str) -> None:
    existing = read_text(path) if path.exists() else ""
    combined = existing.rstrip() + "\n\n" + section.strip() + "\n"
    write_text(path, combined)
