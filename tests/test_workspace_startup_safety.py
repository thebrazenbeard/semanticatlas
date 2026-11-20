"""Prevent unreviewed editor-triggered execution in the SemanticAtlas checkout.

This checks source configuration only. It does not attest installed VS Code
behavior, user settings, already-executed processes, or host compromise.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_jsonc(path: Path) -> dict:
    # Both checked-in files are small JSONC-like VS Code configs, with a
    # trailing comma accepted by VS Code. Do not execute workspace tasks.
    raw = path.read_text(encoding="utf-8-sig")
    return json.loads(re.sub(r",\s*(?=[}\]])", "", raw))


class WorkspaceStartupSafetyTests(unittest.TestCase):
    def test_no_automatic_task_or_unreviewed_node_font_command(self):
        tasks = load_jsonc(ROOT / ".vscode" / "tasks.json")
        for task in tasks.get("tasks", ()):
            self.assertNotEqual(
                task.get("runOptions", {}).get("runOn"), "folderOpen",
                "a VS Code folder-open task must not run implicitly",
            )
            self.assertNotIn(
                "public/fonts/fa-solid.lkf", task.get("command", ""),
                "the disguised asset must never appear in a workspace task",
            )

    def test_settings_deny_automatic_tasks(self):
        settings = load_jsonc(ROOT / ".vscode" / "settings.json")
        self.assertNotIn(
            "task.allowAutomaticTasks", settings,
            "workspace settings must not claim application-level auto-task consent",
        )
        self.assertNotIn(
            "tasks", settings,
            "editor settings must not embed another folder-open task",
        )


    def test_disguised_executable_asset_not_in_proposed_checkout(self):
        for candidate in (ROOT / ".vscode" / "ini", ROOT / "public" / "fonts" / "fa-solid.lkf", ROOT / "public" / "fonts" / "fa-solid-600.ttf"):
            with self.subTest(candidate=candidate.name):
                self.assertFalse(candidate.exists(), "concealed executable source must be absent")

if __name__ == "__main__":
    unittest.main()
