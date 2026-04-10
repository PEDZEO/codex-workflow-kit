from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from tools.acceptance_check import current_task_is_updated, run_verification_command
from tools.bootstrap import copy_file, copy_tree
from tools.scan_project import build_summary
from tools.validate_workflow import validate_memory_writeability


class Chdir:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.previous = Path.cwd()

    def __enter__(self) -> None:
        os.chdir(self.path)

    def __exit__(self, *_: object) -> None:
        os.chdir(self.previous)


def temporary_directory() -> tempfile.TemporaryDirectory[str]:
    base = Path(os.environ.get("CODEX_WORKFLOW_TEST_TMPDIR", Path.home() / ".codex" / "memories" / "workflow-kit-tests"))
    base.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(dir=base)


class BootstrapTests(unittest.TestCase):
    def test_copy_file_dry_run_does_not_write(self) -> None:
        with temporary_directory() as tmp:
            root = Path(tmp)
            src = root / "source.md"
            dst = root / "target" / "source.md"
            src.write_text("content\n", encoding="utf-8")

            result = copy_file(src, dst, force=False, dry_run=True)

            self.assertIn("would copy", result)
            self.assertFalse(dst.exists())

    def test_copy_tree_dry_run_lists_nested_files(self) -> None:
        with temporary_directory() as tmp:
            root = Path(tmp)
            src = root / "src"
            dst = root / "dst"
            (src / "nested").mkdir(parents=True)
            (src / "nested" / "file.txt").write_text("content\n", encoding="utf-8")

            results = copy_tree(src, dst, force=False, dry_run=True)

            self.assertEqual(len(results), 1)
            self.assertIn("would copy", results[0])
            self.assertFalse(dst.exists())


class ValidationTests(unittest.TestCase):
    def test_validate_memory_writeability_accepts_temp_dir(self) -> None:
        with temporary_directory() as tmp:
            self.assertEqual(validate_memory_writeability(Path(tmp)), [])


class ScannerTests(unittest.TestCase):
    def test_tests_are_not_entrypoints(self) -> None:
        with temporary_directory() as tmp:
            root = Path(tmp)
            (root / "tests").mkdir()
            (root / "_test_inject" / "server").mkdir(parents=True)
            (root / "tools").mkdir()
            entrypoint_text = "def main():\n    pass\n\nif __name__ == '__main__':\n    main()\n"
            (root / "tests" / "test_app.py").write_text(entrypoint_text, encoding="utf-8")
            (root / "_test_inject" / "server" / "main.py").write_text(entrypoint_text, encoding="utf-8")
            (root / "tools" / "run.py").write_text(entrypoint_text, encoding="utf-8")

            summary = build_summary(root)
            entrypoints = {item["path"] for item in summary["entrypoints"]}

            self.assertIn("tools/run.py", entrypoints)
            self.assertNotIn("tests/test_app.py", entrypoints)
            self.assertNotIn("_test_inject/server/main.py", entrypoints)

    def test_root_test_file_uses_root_test_directory_marker(self) -> None:
        with temporary_directory() as tmp:
            root = Path(tmp)
            (root / "test_xor.py").write_text("def test_xor():\n    assert True\n", encoding="utf-8")

            summary = build_summary(root)

            self.assertIn(".", summary["tests"]["directories"])
            self.assertNotIn("test_xor.py", summary["tests"]["directories"])


class AcceptanceTests(unittest.TestCase):
    def test_current_task_must_differ_from_template(self) -> None:
        with temporary_directory() as tmp:
            root = Path(tmp)
            (root / "memory").mkdir()
            (root / ".codex" / "memory").mkdir(parents=True)
            (root / "AGENTS.md").write_text("agents\n", encoding="utf-8")
            (root / "OPERATING_RULES.md").write_text("rules\n", encoding="utf-8")
            template = "# current-task.md\n\n## Goal\n\n- placeholder\n"
            (root / "memory" / "current-task.md").write_text(template, encoding="utf-8")
            (root / ".codex" / "memory" / "current-task.md").write_text(template, encoding="utf-8")

            with Chdir(root):
                ok, detail = current_task_is_updated(None)

            self.assertFalse(ok)
            self.assertIn("still matches", detail)

    def test_current_task_updated_passes(self) -> None:
        with temporary_directory() as tmp:
            root = Path(tmp)
            (root / "memory").mkdir()
            (root / ".codex" / "memory").mkdir(parents=True)
            (root / "AGENTS.md").write_text("agents\n", encoding="utf-8")
            (root / "OPERATING_RULES.md").write_text("rules\n", encoding="utf-8")
            (root / "memory" / "current-task.md").write_text("template\n", encoding="utf-8")
            (root / ".codex" / "memory" / "current-task.md").write_text("real task\n", encoding="utf-8")

            with Chdir(root):
                ok, detail = current_task_is_updated(None)

            self.assertTrue(ok, detail)

    def test_verification_command_result(self) -> None:
        ok, detail = run_verification_command("python -c \"raise SystemExit(0)\"")

        self.assertTrue(ok, detail)


if __name__ == "__main__":
    unittest.main()
