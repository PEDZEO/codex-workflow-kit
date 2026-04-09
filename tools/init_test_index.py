from __future__ import annotations

import argparse
from pathlib import Path

from common import configure_stdout, write_text
from scan_project import build_summary, classify_test_commands, map_tests_to_areas


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a draft TEST_INDEX.md from repository scan heuristics")
    parser.add_argument("--target", default=".", help="Target project directory")
    parser.add_argument("--output", default="TEST_INDEX.generated.md", help="Output file path")
    return parser


def format_command_block(commands: list[dict[str, str]], placeholder: str) -> str:
    if not commands:
        return f"- {placeholder}"
    lines: list[str] = []
    for item in commands[:6]:
        lines.append(f"- Команда: `{item['command']}`")
        lines.append("  - Что покрывает: Needs review")
        lines.append("  - Когда запускать: Needs review")
    return "\n".join(lines)


def format_feature_map(area_tests: dict[str, list[str]]) -> str:
    lines: list[str] = []
    for area, tests in area_tests.items():
        lines.append(f"- {area}:")
        if tests:
            lines.append(f"  - Тесты: {', '.join(tests)}")
        else:
            lines.append("  - Тесты: Needs review")
    return "\n".join(lines)


def render(summary: dict[str, object]) -> str:
    commands = summary.get("commands", [])
    grouped = classify_test_commands(commands)
    tests = summary.get("tests", {})
    test_dirs = tests.get("directories", []) if isinstance(tests, dict) else []
    area_map = map_tests_to_areas(summary)

    all_commands_block = []
    for item in commands[:12]:
        all_commands_block.append(f"# {item['name']} ({item['category']})")
        all_commands_block.append(item["command"])
        all_commands_block.append("")
    commands_text = "\n".join(all_commands_block).rstrip() or "# No commands detected automatically"

    return f"""# TEST_INDEX.md

Generated draft. Review and refine before relying on it.

## Test Commands

```text
{commands_text}
```

## Fast Tests

{format_command_block(grouped.get('smoke', []) + grouped.get('unit', []), 'No fast test commands detected automatically')}

## Medium Tests

{format_command_block(grouped.get('test', []), 'No medium test commands detected automatically')}

## Expensive Tests

{format_command_block(grouped.get('integration', []), 'No expensive test commands detected automatically')}

## Feature Map

{format_feature_map(area_map)}

## Notes For Codex

- Detected test directories: {", ".join(test_dirs) if test_dirs else "Needs review"}
- If no commands were detected, inspect package scripts, Makefile, or project config manually.
- Keep this file aligned with real verification practice.
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

