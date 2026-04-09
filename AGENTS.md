# AGENTS.md

## Purpose

This file defines a fast, low-noise workflow for Codex.

Goals:
- reduce repeated file discovery;
- reduce token usage;
- keep short task memory between steps;
- delegate work to agents with explicit roles;
- require final validation after delegated work.

This file is not optional guidance. It defines the default operating mode for the repository.

## Startup Order

At the start of each task, do this in order:

1. Read `CODEBASE_INDEX.md`.
2. Read `TASK_INTAKE.md`.
3. Read `.codex/memory/current-task.md`.
4. Read `OPERATING_RULES.md` if strict mode is enabled for the repo.
5. Read `.codex/memory/decisions.md` only if the task depends on prior decisions.
6. Build a short plan.
7. Decide what stays on the critical path locally.
8. Decide what can be delegated in parallel.

When these files are missing or stale, prefer generating drafts with the local tools before writing them manually:

- `tools/scan_project.py`
- `tools/init_index.py`
- `tools/init_test_index.py`
- `tools/init_change_areas.py`
- `tools/refresh_index.py`
- `tools/explain_scan.py`

Do not begin with broad recursive browsing unless the index is missing or stale.

Do not keep multiple competing summaries of the current task. The canonical live state is `.codex/memory/current-task.md`.

## File Search Rules

Default search order:

1. Use `rg --files` with a narrow glob to locate candidate files.
2. Use `rg` for symbol names, routes, config keys, error strings, and test names.
3. Read only the files that are directly relevant.
4. Prefer targeted ranges over full-file reads for large files.

If the repository has no useful index or test map yet, generate drafts first and then refine:

1. `python tools/scan_project.py --target .`
2. `python tools/init_index.py --target . --output CODEBASE_INDEX.generated.md`
3. `python tools/init_test_index.py --target . --output TEST_INDEX.generated.md`
4. `python tools/init_change_areas.py --target . --output CHANGE_AREAS.generated.md`

Avoid:
- opening large files end to end without evidence they matter;
- repeatedly re-reading files already summarized in memory;
- scanning unrelated directories "just in case".

## Context Rules

Keep context tight.

Always prefer:
- short summaries over raw logs;
- file paths and conclusions over pasted code dumps;
- local verification of changed areas over broad re-analysis.

When research is complete, write a short summary into `.codex/memory/current-task.md` or `.codex/memory/handoffs.md` and continue from that summary.

## Working Memory

Use the memory files as follows:

- `.codex/memory/current-task.md`
  - current goal, constraints, next steps, files in scope
- `.codex/memory/decisions.md`
  - decisions that affect future implementation
- `.codex/memory/handoffs.md`
  - what was delegated, to whom, and expected return format
- `.codex/memory/done.md`
  - completed work and verification that already passed

Rules:
- keep each file short;
- prefer bullets;
- remove stale notes instead of endlessly appending;
- never treat memory as a dump for command output.
- treat `.codex/memory/current-task.md` as the single source of truth for live task state.

## Agent Roles

Use explicit roles.

### explorer

Use for:
- locating files;
- tracing flows;
- identifying entrypoints;
- listing candidate tests.

Explorer must not make code changes unless explicitly asked.

### worker

Use for:
- bounded implementation;
- test updates in a narrow slice;
- isolated refactors in an explicit file set.

Every worker task must define:
- owned files or directories;
- files that must not be touched;
- done criteria;
- expected return format.

### reviewer

Use for:
- risk review;
- regression review;
- test gap review;
- API and behavior consistency review.

Reviewer output must prioritize findings, not summaries.

### tester

Use for:
- targeted verification;
- selecting the smallest relevant test command;
- checking whether changed behavior is actually covered.

## Delegation Protocol

Before spawning agents:

1. Keep the immediate blocking task local.
2. Delegate only side tasks that can run in parallel.
3. Avoid overlapping write ownership.
4. Avoid sending the full conversation when a compact task brief is enough.
5. Record the delegation in `.codex/memory/handoffs.md`.

Every delegated task must include:
- objective;
- scope;
- out-of-scope items;
- done criteria;
- return format.

Preferred return format:
- changed files;
- what changed;
- risks or open questions;
- verification run or not run.

## Review Protocol

After delegated work returns, the main Codex must:

1. inspect the diff;
2. compare output against the original task;
3. check for obvious regressions;
4. run the smallest relevant verification;
5. update memory with concise results.

Do not re-read the whole codebase after a narrow delegated change.

## Token Discipline

To reduce token use:

- never paste large logs into memory;
- never keep duplicate summaries in multiple files;
- reuse `CODEBASE_INDEX.md` for architecture facts;
- reuse `done.md` for already-verified work;
- prefer exact file references over narrative repetition;
- compress findings into 5-10 lines before moving on.

## Recommended Session Pattern

1. Index and memory.
2. Narrow search.
3. Short plan.
4. Local critical-path work.
5. Parallel delegation for side tasks.
6. Diff review.
7. Targeted tests.
8. Memory update.

## Failure Mode Rules

If the index is stale, update it before broad exploration.

If memory conflicts with code, trust the code and refresh memory.

If two agents would touch the same file, keep the work local or split it again.

If verification is not run, state that explicitly in final output and in `done.md`.
