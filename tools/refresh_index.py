from __future__ import annotations

import argparse
from pathlib import Path

from common import configure_stdout, read_text, write_text
from init_index import render as render_index
from scan_project import build_summary


SECTION_HEADERS = [
    "## Project Summary",
    "## Entry Points",
    "## Main Directories",
    "## Important Files",
    "## CI Files",
    "## Area Hints",
    "## Test Map",
    "## Common Commands",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Refresh machine-generated sections in an existing CODEBASE_INDEX.md")
    parser.add_argument("--target", default=".", help="Target project directory")
    parser.add_argument("--index", default="CODEBASE_INDEX.md", help="Existing index file path")
    return parser


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current_header: str | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current_header is not None:
                sections[current_header] = "\n".join(buffer).rstrip() + "\n"
            current_header = line.strip()
            buffer = [line]
        else:
            buffer.append(line)
    if current_header is not None:
        sections[current_header] = "\n".join(buffer).rstrip() + "\n"
    return sections


def refresh(existing: str, generated: str) -> str:
    existing_sections = split_sections(existing)
    generated_sections = split_sections(generated)
    for header in SECTION_HEADERS:
        if header in generated_sections:
            existing_sections[header] = generated_sections[header]

    ordered_headers: list[str] = []
    for line in existing.splitlines():
        if line.startswith("## "):
            header = line.strip()
            if header not in ordered_headers:
                ordered_headers.append(header)
    for header in SECTION_HEADERS:
        if header not in ordered_headers and header in existing_sections:
            ordered_headers.append(header)

    prefix = existing.split("## ", 1)[0].rstrip() + "\n\n"
    body = "\n\n".join(existing_sections[header].rstrip() for header in ordered_headers if header in existing_sections)
    return prefix + body.rstrip() + "\n"


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    target = Path(args.target).resolve()
    index_path = Path(args.index)
    if not index_path.is_absolute():
        index_path = target / index_path
    summary = build_summary(target)
    generated = render_index(summary)
    existing = read_text(index_path)
    refreshed = refresh(existing, generated)
    write_text(index_path, refreshed)
    print(f"Refreshed {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
