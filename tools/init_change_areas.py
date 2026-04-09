from __future__ import annotations

import argparse
from pathlib import Path

from common import configure_stdout, write_text
from scan_project import build_change_area_summary, build_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a draft CHANGE_AREAS.md from repository structure")
    parser.add_argument("--target", default=".", help="Target project directory")
    parser.add_argument("--output", default="CHANGE_AREAS.generated.md", help="Output file path")
    return parser


def render_area(area: dict[str, object]) -> str:
    directories = ", ".join(area.get("directories", [])) or "Needs review"
    entrypoints = ", ".join(area.get("entrypoints", [])) or "Needs review"
    tests = ", ".join(area.get("tests", [])) or "Needs review"
    return f"""- {area['area']}
  - Основные директории: {directories}
  - Главные entrypoints: {entrypoints}
  - Основные риски: Needs review
  - Типичные тесты: {tests}"""


def render(summary: dict[str, object]) -> str:
    areas = build_change_area_summary(summary)
    area_text = "\n\n".join(render_area(area) for area in areas) if areas else "- No change areas detected automatically"
    return f"""# CHANGE_AREAS.md

Generated draft. Review and refine before using it for strict delegation.

## Areas

{area_text}

## Delegation Rule

- Один агент должен владеть одной зоной записи.
- Если задача затрагивает две зоны, критический путь лучше держать локально.
- Если зона не определена, сначала отправляй `explorer`.
"""


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    target = Path(args.target).resolve()
    output = Path(args.output)
    if not output.is_absolute():
        output = target / output
    summary = build_summary(target)
    write_text(output, render(summary))
    print(f"Generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

