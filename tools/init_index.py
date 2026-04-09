from __future__ import annotations

import argparse
from pathlib import Path

from common import configure_stdout, emit_json, emit_output
from scan_project import build_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate a draft CODEBASE_INDEX.md from a structural project scan")
    parser.add_argument("--target", default=".", help="Target project directory")
    parser.add_argument(
        "--output",
        default="CODEBASE_INDEX.generated.md",
        help="Output file path for the generated index draft",
    )
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    return parser


def bullet_lines(items: list[str], placeholder: str) -> str:
    if not items:
        return f"- {placeholder}"
    return "\n".join(f"- {item}" for item in items)


def render_commands(commands: list[dict[str, str]]) -> str:
    if not commands:
        return "# No commands detected automatically"
    lines = []
    for item in commands[:12]:
        lines.append(f"# {item['name']}")
        lines.append(item["command"])
        lines.append("")
    return "\n".join(lines).rstrip()


def render_directories(entries: list[dict[str, str]]) -> str:
    if not entries:
        return "- No top-level directories detected"
    lines: list[str] = []
    for item in entries:
        lines.append(f"- `{item['path']}/`")
        lines.append(f"  - {item['description']}")
    return "\n".join(lines)


def render_entrypoints(entries: list[dict[str, object]]) -> str:
    if not entries:
        return "- No entrypoint candidates detected"
    lines: list[str] = []
    for item in entries[:8]:
        reasons = ", ".join(item.get("reasons", [])) or "needs review"
        lines.append(f"- {item['path']}  ({reasons})")
    return "\n".join(lines)


def render_area_hints(entries: list[dict[str, object]]) -> str:
    if not entries:
        return "- No area hints detected automatically"
    lines: list[str] = []
    for item in entries:
        matches = ", ".join(item.get("matches", []))
        lines.append(f"- {item['area']}: {matches}")
    return "\n".join(lines)


def render(summary: dict[str, object]) -> str:
    languages = summary.get("languages", [])
    frameworks = summary.get("frameworks", [])
    important_files = summary.get("important_files", [])
    ci_files = summary.get("ci_files", [])
    tests = summary.get("tests", {})
    commands = summary.get("commands", [])
    confidence_notes = summary.get("confidence_notes", {})

    primary_language = summary.get("primary_language") or "Needs review"
    frameworks_text = ", ".join(frameworks) if frameworks else "Needs review"
    package_manager = summary.get("package_manager") or "Needs review"
    test_dirs = tests.get("directories", []) if isinstance(tests, dict) else []
    test_samples = tests.get("sample_files", []) if isinstance(tests, dict) else []
    test_count = tests.get("count", 0) if isinstance(tests, dict) else 0

    return f"""# CODEBASE_INDEX.md

Generated draft. Review and refine before treating it as canonical.

## Project Summary

- Project name: {summary.get("project_name", "Needs review")}
- Main purpose: Needs review
- Primary language: {primary_language}
- Frameworks: {frameworks_text}
- Package manager: {package_manager}
- Test runner: Needs review

## Entry Points

{render_entrypoints(summary.get("entrypoints", []))}

## Main Directories

{render_directories(summary.get("main_directories", []))}

## Important Files

{bullet_lines(important_files[:20], "No important config or manifest files detected")}

## CI Files

{bullet_lines(ci_files[:10], "No CI files detected")}

## Area Hints

{render_area_hints(summary.get("area_hints", []))}

## Test Map

- Test directories: {", ".join(test_dirs) if test_dirs else "Needs review"}
- Detected test files: {test_count}
- Sample test files:
{bullet_lines(test_samples[:10], "No test files detected automatically")}

## Common Commands

```text
{render_commands(commands)}
```

## Notes For Codex

- Confidence notes:
- Primary language: {confidence_notes.get('primary_language', {}).get('confidence', 'unknown')} ({confidence_notes.get('primary_language', {}).get('reason', 'Needs review')})
- Entry points: {confidence_notes.get('entrypoints', {}).get('confidence', 'unknown')} ({confidence_notes.get('entrypoints', {}).get('reason', 'Needs review')})
- Tests: {confidence_notes.get('tests', {}).get('confidence', 'unknown')} ({confidence_notes.get('tests', {}).get('reason', 'Needs review')})
- Commands: {confidence_notes.get('commands', {}).get('confidence', 'unknown')} ({confidence_notes.get('commands', {}).get('reason', 'Needs review')})
- Areas: {confidence_notes.get('areas', {}).get('confidence', 'unknown')} ({confidence_notes.get('areas', {}).get('reason', 'Needs review')})
- This file was generated from structural scanning and heuristics.
- Verify entry points, test runner, and business-purpose descriptions manually.
- Update this file when architecture or repository structure changes.
"""


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    target = Path(args.target).resolve()
    summary = build_summary(target)
    output = args.output
    if output != "-":
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = target / output_path
        output = str(output_path)
    if args.format == "json":
        emit_json(output, summary)
    else:
        emit_output(output, render(summary))
    if output != "-":
        print(f"Generated {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
