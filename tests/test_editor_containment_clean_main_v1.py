"""Read-only source regressions for Semantic Atlas editor startup containment.

Never launch VS Code, Node, workspace tasks, or purported font assets.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SemanticAtlasEditorContainment(unittest.TestCase):
    def test_no_folder_open_tasks(self):
        tasks = json.loads((ROOT / ".vscode/tasks.json").read_text(encoding="utf-8-sig"))
        self.assertEqual(tasks, {"version": "2.0.0", "tasks": []})

    def test_settings_cannot_enable_hidden_startup(self):
        settings = json.loads((ROOT / ".vscode/settings.json").read_text(encoding="utf-8-sig"))
        for key in ("task.allowAutomaticTasks", "tasks", "terminal.integrated.hideOnStartup", "debug.openDebug"):
            with self.subTest(key=key):
                self.assertNotIn(key, settings)

    def test_loader_and_counterfeit_font_absent(self):
        self.assertFalse((ROOT / ".vscode/ini").exists())
        self.assertFalse((ROOT / "public/fonts/fa-solid-600.ttf").exists())

    def test_ignore_does_not_hide_config_script(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8-sig")
        patterns = [line.strip().lower() for line in text.splitlines()
                    if line.strip() and not line.lstrip().startswith("#")]
        self.assertNotIn("config.bat", patterns)

    def test_no_extra_nested_editor_config(self):
        # This test inspects tracked source paths only. The candidate's
        # source Git tree is reviewed separately; runtime filesystem trust
        # cannot be inferred from this check.
        vscode = ROOT / ".vscode"
        for path in vscode.rglob("tasks.json"):
            with self.subTest(path=path.name):
                tasks = json.loads(path.read_text(encoding="utf-8-sig"))
                self.assertEqual(tasks.get("tasks"), [])


if __name__ == "__main__":
    unittest.main()
