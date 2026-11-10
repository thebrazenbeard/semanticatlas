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


def task_variants(task):
    yield task
    for platform in ("windows", "linux", "osx"):
        override = task.get(platform)
        if isinstance(override, dict):
            yield override


class WorkspaceStartupSafetyTests(unittest.TestCase):
    def test_no_automatic_task_or_unreviewed_node_font_command(self):
        tasks = load_jsonc(ROOT / ".vscode" / "tasks.json")
        for task in tasks.get("tasks", ()):
            for variant in task_variants(task):
                self.assertNotEqual(
                    variant.get("runOptions", {}).get("runOn"), "folderOpen",
                    "a VS Code folder-open task must not run implicitly",
                )
                command = str(variant.get("command", ""))
                args = variant.get("args", [])
                combined = " ".join([command, *map(str, args if isinstance(args, list) else [args])])
                if re.search(r"(?i)\b(node|python|pwsh|powershell|cmd)\b", combined):
                    self.assertNotRegex(combined, r"(?i)\.(ttf|otf|woff2?)\b")

    def test_settings_deny_automatic_tasks(self):
        settings = load_jsonc(ROOT / ".vscode" / "settings.json")
        self.assertEqual(
            settings.get("task.allowAutomaticTasks"), "off",
            "workspace settings must explicitly disable auto tasks",
        )
        self.assertNotIn(
            "tasks", settings,
            "editor settings must not embed another folder-open task",
        )


    def test_disguised_executable_asset_not_in_proposed_checkout(self):
        self.assertFalse(
            (ROOT / "public" / "fonts" / "fa-solid-600.ttf").exists(),
            "obfuscated executable payload must be absent from the working tree",
        )
        signatures = {
            ".ttf": (b"\x00\x01\x00\x00", b"true", b"ttcf"),
            ".otf": (b"OTTO",), ".woff": (b"wOFF",), ".woff2": (b"wOF2",),
        }
        for asset in (ROOT / "public" / "fonts").rglob("*"):
            if asset.is_file() and asset.suffix.lower() in signatures:
                self.assertIn(asset.read_bytes()[:4], signatures[asset.suffix.lower()], str(asset))

    def test_platform_override_and_bom_examples(self):
        sample = {"command": "echo safe", "windows": {"runOptions": {"runOn": "folderOpen"}}}
        self.assertTrue(any(x.get("runOptions", {}).get("runOn") == "folderOpen"
                            for x in task_variants(sample)))
        self.assertEqual(json.loads(b'\xef\xbb\xbf{"tasks":[]}'.decode("utf-8-sig")), {"tasks": []})

if __name__ == "__main__":
    unittest.main()
