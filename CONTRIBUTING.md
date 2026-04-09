# Contributing

Thanks for contributing to `codex-workflow-kit`.

## Scope

This repository is intentionally focused. Good contributions usually improve one of these areas:

- Codex workflow clarity
- task memory discipline
- agent delegation discipline
- repository search discipline
- bootstrap and CLI ergonomics
- documentation quality
- cross-platform behavior

Avoid contributions that turn the project into:

- a generic AI framework
- a large orchestration platform
- a vague prompt collection
- a heavy abstraction over normal repository work

## Before You Change Anything

1. Read `README.md`
2. Read `AGENTS.md`
3. Read `OPERATING_RULES.md`
4. Keep the repository philosophy intact: strict, practical, low-noise

## Contribution Rules

- Keep changes narrow and explicit.
- Prefer small pull requests.
- Do not add complexity without clear workflow benefit.
- Keep the docs and the CLI aligned.
- Keep Windows and Linux behavior in mind.
- Avoid introducing unnecessary dependencies.

## For Documentation Changes

- Keep wording direct and practical.
- Avoid fluffy product language.
- Prefer examples that map to real repository work.
- Update both `README.md` and `README.en.md` when the change affects the public description of the project.

## For CLI Changes

- Prefer predictable CLI behavior over cleverness.
- Keep error messages actionable.
- Preserve cross-platform compatibility.
- Do not break the mandatory core assumptions without updating docs.

## Validation

Before submitting a change, run the smallest relevant checks.

Typical examples:

```powershell
python tools/validate_workflow.py --memory-dir memory
python tools/acceptance_check.py --scope --behavior --verification --regression --memory
```

If the change affects CLI behavior, verify the relevant command path directly.

## Pull Request Guidance

Good pull requests usually contain:

- a small, clear scope
- a short reason for the change
- verification notes
- any residual risk or follow-up item

## Discussions and Issues

If the change is large or changes repository philosophy, open an issue first.
