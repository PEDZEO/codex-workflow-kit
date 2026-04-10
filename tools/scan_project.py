from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

try:
    from .common import configure_stdout
except ImportError:  # pragma: no cover - direct script execution
    from common import configure_stdout

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover - Python 3.10 fallback
    tomllib = None


IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    ".next",
    ".nuxt",
    ".cache",
    ".mypy_cache",
    ".pytest_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "out",
    "coverage",
    "__pycache__",
}

LANGUAGE_BY_SUFFIX = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".cjs": "JavaScript",
    ".mjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".cs": "C#",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C/C++",
    ".swift": "Swift",
    ".scala": "Scala",
    ".sh": "Shell",
}

ENTRYPOINT_NAMES = {
    "main.py",
    "app.py",
    "server.py",
    "manage.py",
    "wsgi.py",
    "asgi.py",
    "index.js",
    "server.js",
    "app.js",
    "main.js",
    "index.ts",
    "server.ts",
    "app.ts",
    "main.ts",
    "main.go",
    "main.rs",
}

CONFIG_NAMES = {
    "package.json",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "poetry.lock",
    "requirements.txt",
    "requirements-dev.txt",
    "Pipfile",
    "Pipfile.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
    "Makefile",
    ".env.example",
    ".env.sample",
    "tsconfig.json",
    "jsconfig.json",
    ".eslintrc",
    ".eslintrc.json",
    ".eslintrc.js",
    ".prettierrc",
    "pytest.ini",
    "tox.ini",
    "mypy.ini",
}

CI_NAMES = {
    ".github/workflows",
    ".gitlab-ci.yml",
    ".circleci/config.yml",
    "azure-pipelines.yml",
}

AREA_HINTS = {
    "API": ["api", "server", "routes", "route", "endpoint", "controller"],
    "UI": ["ui", "frontend", "web", "pages", "components"],
    "Bot or handlers": ["bot", "handler", "handlers", "callback"],
    "Data layer": ["db", "database", "repo", "repository", "storage", "models"],
    "Auth": ["auth", "login", "session", "token", "oauth"],
    "Notifications": ["notify", "notification", "webhook", "email", "telegram"],
}


def score_to_confidence(score: int) -> str:
    if score >= 4:
        return "high"
    if score >= 2:
        return "medium"
    return "low"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scan a repository and emit a structured project summary")
    parser.add_argument("--target", default=".", help="Target project directory")
    parser.add_argument("--output", default="-", help="Output file path, or - for stdout")
    parser.add_argument("--format", choices=["json"], default="json", help="Output format")
    return parser


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(root)
        if should_skip(rel):
            continue
        files.append(path)
    return files


def detect_languages(files: list[Path]) -> list[dict[str, Any]]:
    counts: Counter[str] = Counter()
    for path in files:
        language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
        if language:
            counts[language] += 1
    return [{"language": name, "files": counts[name]} for name, _ in counts.most_common()]


def load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_toml(path: Path) -> dict[str, Any] | None:
    if tomllib is None:
        return None
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_text_safe(path: Path) -> str:
    for encoding in ("utf-8", "utf-8-sig", "cp1251", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except Exception:
            continue
    return ""


def scan_package_json(root: Path) -> dict[str, Any]:
    package_path = root / "package.json"
    if not package_path.exists():
        return {}
    data = load_json(package_path) or {}
    scripts = data.get("scripts", {})
    return {
        "package_manager": detect_node_package_manager(root),
        "name": data.get("name"),
        "framework_hints": extract_framework_hints_from_package(data),
        "commands": [{"name": name, "command": value} for name, value in scripts.items()],
    }


def detect_node_package_manager(root: Path) -> str | None:
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "package-lock.json").exists():
        return "npm"
    if (root / "package.json").exists():
        return "npm"
    return None


def extract_framework_hints_from_package(data: dict[str, Any]) -> list[str]:
    dependencies = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        dependencies.update(data.get(key, {}))
    frameworks: list[str] = []
    mapping = {
        "react": "React",
        "next": "Next.js",
        "vue": "Vue",
        "nuxt": "Nuxt",
        "svelte": "Svelte",
        "express": "Express",
        "fastify": "Fastify",
        "nestjs": "NestJS",
        "vite": "Vite",
    }
    for dep, name in mapping.items():
        if dep in dependencies:
            frameworks.append(name)
    return frameworks


def scan_pyproject(root: Path) -> dict[str, Any]:
    path = root / "pyproject.toml"
    if not path.exists():
        return {}
    data = load_toml(path) or {}
    project = data.get("project", {})
    tool = data.get("tool", {})
    commands: list[dict[str, str]] = []
    frameworks: list[str] = []

    if "scripts" in project:
        for name, value in project["scripts"].items():
            commands.append({"name": name, "command": value})

    poetry = tool.get("poetry", {})
    for name, value in poetry.get("scripts", {}).items():
        commands.append({"name": name, "command": str(value)})

    dependencies = []
    if isinstance(project.get("dependencies"), list):
        dependencies.extend(project["dependencies"])
    dependencies.extend((tool.get("poetry", {}) or {}).get("dependencies", {}).keys())
    dep_text = " ".join(map(str, dependencies)).lower()
    if "fastapi" in dep_text:
        frameworks.append("FastAPI")
    if "django" in dep_text:
        frameworks.append("Django")
    if "flask" in dep_text:
        frameworks.append("Flask")
    if "pytest" in dep_text:
        frameworks.append("Pytest")

    return {
        "name": project.get("name") or poetry.get("name"),
        "package_manager": "poetry" if poetry else "pip/pyproject",
        "framework_hints": frameworks,
        "commands": commands,
    }


def scan_makefile(root: Path) -> list[dict[str, str]]:
    path = root / "Makefile"
    if not path.exists():
        return []
    commands: list[dict[str, str]] = []
    for line in read_text_safe(path).splitlines():
        if not line or line.startswith("\t") or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        target = line.split(":", 1)[0].strip()
        if target and " " not in target and not target.startswith("."):
            commands.append({"name": f"make {target}", "command": f"make {target}"})
    return commands[:30]


def infer_command_category(name: str, command: str) -> str:
    text = f"{name} {command}".lower()
    if any(token in text for token in ("lint", "eslint", "ruff", "flake8")):
        return "lint"
    if any(token in text for token in ("typecheck", "mypy", "pyright", "tsc")):
        return "typecheck"
    if any(token in text for token in ("test", "pytest", "vitest", "jest", "go test", "cargo test")):
        if any(token in text for token in ("integration", "e2e", "end-to-end")):
            return "integration"
        if any(token in text for token in ("smoke", "quick")):
            return "smoke"
        if any(token in text for token in ("unit",)):
            return "unit"
        return "test"
    if any(token in text for token in ("run", "start", "dev", "serve", "uvicorn")):
        return "run"
    return "other"


def find_entrypoints(root: Path, files: list[Path]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for path in files:
        rel = path.relative_to(root)
        parts_lower = {part.lower() for part in rel.parts}
        if parts_lower & {"test", "tests", "spec", "specs", "__tests__"}:
            continue
        if any("test" in part for part in parts_lower):
            continue
        if path.stem.lower().startswith("test_") or path.stem.lower().endswith("_test"):
            continue
        score = 0
        reason: list[str] = []

        if path.name in ENTRYPOINT_NAMES:
            score += 3
            reason.append("well-known entrypoint filename")

        rel_lower = str(rel).replace("\\", "/").lower()
        if rel_lower.startswith(("src/", "app/", "server/", "cmd/", "bin/")):
            score += 1
            reason.append("entry-like top-level directory")

        if path.suffix.lower() in {".py", ".js", ".ts", ".go", ".rs"}:
            content = read_text_safe(path)
            if "__main__" in content or "uvicorn" in content or "FastAPI(" in content:
                score += 2
                reason.append("runtime entrypoint pattern")
            if re.search(r"\bmain\s*\(", content):
                score += 1
                reason.append("main function pattern")

        if score > 0:
            candidates.append(
                {
                    "path": rel.as_posix(),
                    "score": score,
                    "confidence": score_to_confidence(score),
                    "reasons": reason,
                }
            )

    return sorted(candidates, key=lambda item: (-item["score"], item["path"]))[:20]


def find_main_directories(root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        if child.name in IGNORED_DIRS or (child.name.startswith(".") and child.name != ".github"):
            continue
        description = infer_directory_role(child.name)
        entries.append({"path": child.name, "description": description})
    return entries


def infer_directory_role(name: str) -> str:
    lower = name.lower()
    if lower in {"src", "app", "lib"}:
        return "Main application code"
    if lower in {"server", "api"}:
        return "Backend or API layer"
    if lower in {"web", "frontend", "ui"}:
        return "User interface or frontend"
    if lower in {"bot", "handlers"}:
        return "Bot handlers or event-driven logic"
    if "test" in lower:
        return "Tests"
    if lower in {"scripts", "tools"}:
        return "Automation and utility scripts"
    if lower in {"docs", "doc"}:
        return "Documentation"
    if lower in {"db", "database", "migrations"}:
        return "Persistence or schema-related files"
    return "Needs review"


def find_configs(root: Path, files: list[Path]) -> list[str]:
    configs: list[str] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if path.name in CONFIG_NAMES:
            configs.append(rel)
        elif rel in CI_NAMES:
            configs.append(rel)
        elif rel.startswith(".github/workflows/"):
            configs.append(rel)
    return sorted(dict.fromkeys(configs))


def find_tests(root: Path, files: list[Path]) -> dict[str, Any]:
    test_files: list[str] = []
    test_dirs: Counter[str] = Counter()
    for path in files:
        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        lower = rel_posix.lower()
        if path.suffix.lower() not in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".kt", ".rb", ".php"}:
            continue
        parts_lower = [part.lower() for part in rel.parts]
        file_stem = path.stem.lower()
        is_test = (
            any(part in {"test", "tests", "spec", "specs", "__tests__"} for part in parts_lower)
            or file_stem.startswith("test_")
            or file_stem.endswith("_test")
            or file_stem.endswith(".test")
            or file_stem.endswith(".spec")
        )
        if is_test:
            test_files.append(rel_posix)
            if len(rel.parts) > 1:
                test_dirs[rel.parts[0]] += 1
            else:
                test_dirs["."] += 1
    return {
        "directories": [name for name, _ in test_dirs.most_common(10)],
        "sample_files": sorted(test_files)[:30],
        "count": len(test_files),
    }


def detect_ci(files: list[Path], root: Path) -> list[str]:
    found: list[str] = []
    for path in files:
        rel = path.relative_to(root).as_posix()
        if rel.startswith(".github/workflows/"):
            found.append(rel)
        elif rel in CI_NAMES:
            found.append(rel)
    return sorted(found)


def detect_area_hints(root: Path) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    top_level = [child.name for child in root.iterdir() if child.is_dir() and child.name not in IGNORED_DIRS]
    for area, hints in AREA_HINTS.items():
        matches = [name for name in top_level if any(hint in name.lower() for hint in hints)]
        if matches:
            confidence = "high" if len(matches) >= 2 else "medium"
            found.append({"area": area, "matches": matches, "confidence": confidence})
    return found


def choose_primary_language(languages: list[dict[str, Any]]) -> str | None:
    return languages[0]["language"] if languages else None


def collect_commands(root: Path) -> list[dict[str, str]]:
    commands: list[dict[str, str]] = []
    package = scan_package_json(root)
    pyproject = scan_pyproject(root)

    commands.extend(package.get("commands", []))
    commands.extend(pyproject.get("commands", []))
    commands.extend(scan_makefile(root))

    # Dedupe by command name + command string while preserving order.
    seen: set[tuple[str, str]] = set()
    deduped: list[dict[str, str]] = []
    for item in commands:
        key = (item["name"], item["command"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    enriched: list[dict[str, str]] = []
    for item in deduped[:50]:
        enriched.append(
            {
                "name": item["name"],
                "command": item["command"],
                "category": infer_command_category(item["name"], item["command"]),
            }
        )
    return enriched


def detect_frameworks(root: Path) -> list[str]:
    frameworks: list[str] = []
    package = scan_package_json(root)
    pyproject = scan_pyproject(root)
    frameworks.extend(package.get("framework_hints", []))
    frameworks.extend(pyproject.get("framework_hints", []))
    return sorted(dict.fromkeys(frameworks))


def detect_package_manager(root: Path) -> str | None:
    package = scan_package_json(root)
    pyproject = scan_pyproject(root)
    return package.get("package_manager") or pyproject.get("package_manager")


def build_summary(root: Path) -> dict[str, Any]:
    files = iter_files(root)
    languages = detect_languages(files)
    commands = collect_commands(root)
    tests = find_tests(root, files)
    entrypoints = find_entrypoints(root, files)
    area_hints = detect_area_hints(root)
    return {
        "project_root": str(root),
        "project_name": root.name,
        "primary_language": choose_primary_language(languages),
        "languages": languages,
        "frameworks": detect_frameworks(root),
        "package_manager": detect_package_manager(root),
        "entrypoints": entrypoints,
        "main_directories": find_main_directories(root),
        "important_files": find_configs(root, files),
        "ci_files": detect_ci(files, root),
        "tests": tests,
        "commands": commands,
        "area_hints": area_hints,
        "confidence_notes": build_confidence_notes(languages, entrypoints, tests, commands, area_hints),
    }


def classify_test_commands(commands: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = {
        "unit": [],
        "smoke": [],
        "integration": [],
        "test": [],
        "lint": [],
        "typecheck": [],
    }
    for item in commands:
        category = item.get("category", "other")
        if category in grouped:
            grouped[category].append(item)
        elif category == "other":
            continue
        else:
            grouped["test"].append(item)
    return grouped


def map_tests_to_areas(summary: dict[str, Any]) -> dict[str, list[str]]:
    tests = summary.get("tests", {})
    sample_files = tests.get("sample_files", []) if isinstance(tests, dict) else []
    result: dict[str, list[str]] = {
        "Auth": [],
        "API": [],
        "UI or bot": [],
        "Notifications": [],
        "Data layer": [],
    }
    for sample in sample_files:
        lower = sample.lower()
        if any(token in lower for token in ("auth", "login", "session", "token")):
            result["Auth"].append(sample)
        if any(token in lower for token in ("api", "route", "server", "endpoint")):
            result["API"].append(sample)
        if any(token in lower for token in ("ui", "frontend", "web", "bot", "handler", "callback")):
            result["UI or bot"].append(sample)
        if any(token in lower for token in ("notify", "notification", "webhook", "telegram", "email")):
            result["Notifications"].append(sample)
        if any(token in lower for token in ("db", "repo", "repository", "storage", "model")):
            result["Data layer"].append(sample)
    return {key: values[:8] for key, values in result.items()}


def build_change_area_summary(summary: dict[str, Any]) -> list[dict[str, Any]]:
    directories = summary.get("main_directories", [])
    entrypoints = summary.get("entrypoints", [])
    tests = summary.get("tests", {})
    sample_tests = tests.get("sample_files", []) if isinstance(tests, dict) else []
    areas: list[dict[str, Any]] = []
    for area_name, hints in AREA_HINTS.items():
        area_dirs = [item["path"] for item in directories if any(h in item["path"].lower() for h in hints)]
        area_entries = [item["path"] for item in entrypoints if any(h in item["path"].lower() for h in hints)]
        area_tests = [path for path in sample_tests if any(h in path.lower() for h in hints)]
        if area_dirs or area_entries or area_tests:
            areas.append(
                {
                    "area": area_name,
                    "directories": area_dirs[:8],
                    "entrypoints": area_entries[:8],
                    "tests": area_tests[:8],
                    "confidence": "high" if area_dirs and area_entries else "medium",
                }
            )
    return areas


def build_confidence_notes(
    languages: list[dict[str, Any]],
    entrypoints: list[dict[str, Any]],
    tests: dict[str, Any],
    commands: list[dict[str, str]],
    area_hints: list[dict[str, Any]],
) -> dict[str, Any]:
    notes: dict[str, Any] = {}
    notes["primary_language"] = {
        "confidence": "high" if languages else "low",
        "reason": "Detected from file extensions" if languages else "No language-bearing source files detected",
    }
    notes["entrypoints"] = {
        "confidence": entrypoints[0]["confidence"] if entrypoints else "low",
        "reason": "Based on filename and runtime patterns" if entrypoints else "No strong entrypoint candidates detected",
    }
    notes["tests"] = {
        "confidence": "medium" if tests.get("count", 0) else "low",
        "reason": "Based on filename and directory heuristics" if tests.get("count", 0) else "No test files matched test heuristics",
    }
    notes["commands"] = {
        "confidence": "medium" if commands else "low",
        "reason": "Extracted from project manifests and Makefile" if commands else "No runnable commands detected automatically",
    }
    notes["areas"] = {
        "confidence": "medium" if area_hints else "low",
        "reason": "Derived from top-level directory names" if area_hints else "No strong area hints found from directory names",
    }
    return notes


def main() -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.target).resolve()
    summary = build_summary(root)
    payload = json.dumps(summary, ensure_ascii=False, indent=2)

    if args.output == "-":
        print(payload)
    else:
        Path(args.output).write_text(payload + "\n", encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
