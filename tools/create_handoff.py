from __future__ import annotations

import argparse
from textwrap import dedent

from common import append_section, workflow_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Append a delegated task to .codex/memory/handoffs.md")
    parser.add_argument("--memory-dir", default=None, help="Relative memory directory, default: .codex/memory")
    parser.add_argument("--role", required=True, choices=["explorer", "worker", "reviewer", "tester"])
    parser.add_argument("--objective", required=True)
    parser.add_argument("--owned-files", required=True, help="Comma-separated file or directory list")
    parser.add_argument("--out-of-scope", default="Не указано")
    parser.add_argument("--expected-output", default="changed files, summary, risks, verification")
    parser.add_argument("--status", default="planned")
    return parser


def render(args: argparse.Namespace) -> str:
    return dedent(
        f"""\
        - Agent role:
          - Objective: {args.objective}
          - Role: {args.role}
          - Owned files: {args.owned_files}
          - Out of scope: {args.out_of_scope}
          - Expected output: {args.expected_output}
          - Status: {args.status}
          - Result summary: pending
        """
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    paths = workflow_paths(memory_dir_rel=args.memory_dir)
    append_section(paths.handoffs, render(args))
    print(f"Updated {paths.handoffs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
