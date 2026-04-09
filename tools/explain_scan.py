from __future__ import annotations

import argparse
from pathlib import Path

from common import configure_stdout, emit_json, emit_output
from scan_project import build_summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Explain what the repository scanner detected and why")
    parser.add_argument("--target", default=".", help="Target project directory")
    parser.add_argument("--output", default="-", help="Output path, or - for stdout")
    parser.add_argument("--format", choices=["text", "markdown", "json"], default="text", help="Output format")
    return parser


def build_payload(summary: dict[str, object]) -> dict[str, object]:
    confidence = summary.get("confidence_notes", {})
    return {
        "project_name": summary.get("project_name"),
        "primary_language": {
            "value": summary.get("primary_language"),
            **confidence.get("primary_language", {}),
        },
        "entrypoints": summary.get("entrypoints", []),
        "tests": {
            **summary.get("tests", {}),
            **({"confidence": confidence.get("tests", {}).get("confidence"), "reason": confidence.get("tests", {}).get("reason")} if confidence.get("tests") else {}),
        },
        "commands": {
            "items": summary.get("commands", []),
            **({"confidence": confidence.get("commands", {}).get("confidence"), "reason": confidence.get("commands", {}).get("reason")} if confidence.get("commands") else {}),
        },
        "areas": {
            "items": summary.get("area_hints", []),
            **({"confidence": confidence.get("areas", {}).get("confidence"), "reason": confidence.get("areas", {}).get("reason")} if confidence.get("areas") else {}),
        },
    }


def render_text(summary: dict[str, object]) -> str:
    confidence = summary.get("confidence_notes", {})
    entrypoints = summary.get("entrypoints", [])
    commands = summary.get("commands", [])
    area_hints = summary.get("area_hints", [])
    tests = summary.get("tests", {})

    lines = [
        f"Project: {summary.get('project_name')}",
        f"Primary language: {summary.get('primary_language') or 'unknown'}",
        f"  Confidence: {confidence.get('primary_language', {}).get('confidence', 'unknown')}",
        f"  Reason: {confidence.get('primary_language', {}).get('reason', 'Needs review')}",
        "",
        "Entrypoints:",
    ]
    if entrypoints:
        for item in entrypoints[:8]:
            reasons = ", ".join(item.get("reasons", [])) or "Needs review"
            lines.append(f"- {item['path']} [{item.get('confidence', 'unknown')}]")
            lines.append(f"  Reasons: {reasons}")
    else:
        lines.append("- none detected")

    lines.extend(
        [
            "",
            f"Tests: {tests.get('count', 0) if isinstance(tests, dict) else 0} detected",
            f"  Confidence: {confidence.get('tests', {}).get('confidence', 'unknown')}",
            f"  Reason: {confidence.get('tests', {}).get('reason', 'Needs review')}",
            "",
            f"Commands: {len(commands)} detected",
            f"  Confidence: {confidence.get('commands', {}).get('confidence', 'unknown')}",
            f"  Reason: {confidence.get('commands', {}).get('reason', 'Needs review')}",
            "",
            "Area hints:",
        ]
    )
    if area_hints:
        for item in area_hints:
            lines.append(f"- {item['area']} [{item.get('confidence', 'unknown')}] -> {', '.join(item.get('matches', []))}")
    else:
        lines.append("- none detected")
    return "\n".join(lines)


def render_markdown(summary: dict[str, object]) -> str:
    payload = build_payload(summary)
    entrypoints = payload["entrypoints"]
    tests = payload["tests"]
    commands = payload["commands"]
    areas = payload["areas"]

    lines = [
        "# Scan Explanation",
        "",
        f"- Project: {payload['project_name']}",
        f"- Primary language: {payload['primary_language'].get('value') or 'unknown'}",
        f"- Language confidence: {payload['primary_language'].get('confidence', 'unknown')}",
        f"- Language reason: {payload['primary_language'].get('reason', 'Needs review')}",
        "",
        "## Entrypoints",
    ]
    if entrypoints:
        for item in entrypoints[:8]:
            lines.append(f"- `{item['path']}`")
            lines.append(f"  - confidence: {item.get('confidence', 'unknown')}")
            lines.append(f"  - reasons: {', '.join(item.get('reasons', [])) or 'Needs review'}")
    else:
        lines.append("- none detected")

    lines.extend(
        [
            "",
            "## Tests",
            f"- count: {tests.get('count', 0)}",
            f"- confidence: {tests.get('confidence', 'unknown')}",
            f"- reason: {tests.get('reason', 'Needs review')}",
            "",
            "## Commands",
            f"- count: {len(commands.get('items', []))}",
            f"- confidence: {commands.get('confidence', 'unknown')}",
            f"- reason: {commands.get('reason', 'Needs review')}",
            "",
            "## Areas",
            f"- confidence: {areas.get('confidence', 'unknown')}",
            f"- reason: {areas.get('reason', 'Needs review')}",
        ]
    )
    if areas.get("items"):
        for item in areas["items"]:
            lines.append(f"- {item['area']}: {', '.join(item.get('matches', []))}")
    else:
        lines.append("- none detected")
    return "\n".join(lines)


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    summary = build_summary(Path(args.target).resolve())
    output = args.output
    if args.format == "json":
        emit_json(output, build_payload(summary))
    elif args.format == "markdown":
        emit_output(output, render_markdown(summary))
    else:
        emit_output(output, render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
