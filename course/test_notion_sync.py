"""Offline note-sync regressions; no OAuth, network, or live Notion writes."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("notion_sync", Path(__file__).with_name("notion_sync.py"))
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class FakeNotion:
    def __init__(self, source):
        self.title, self.body = SYNC.render(source, "notes/test.md")
        self.writes = []
        self.fetches = 0
        self.on_fetch = None

    def page(self):
        return {
            "title": self.title,
            "text": f"<page><content>\n{self.body}</content></page>",
        }

    def call(self, tool, arguments):
        if tool == "notion-fetch":
            self.fetches += 1
            if self.on_fetch:
                self.on_fetch(self)
            return self.page()
        self.writes.append((tool, copy.deepcopy(arguments)))
        if arguments["command"] == "update_properties":
            self.title = arguments["properties"]["title"]
        else:
            for change in arguments["content_updates"]:
                assert self.body.count(change["old_str"]) == 1
                self.body = self.body.replace(change["old_str"], change["new_str"], 1)
        return {}


class NoteSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.note = self.root / "notes/test.md"
        self.note.parent.mkdir()
        self.source = "# Test note\n\n## Progress\n\nOriginal paragraph.\n"
        self.note.write_text(self.source)
        self.mapping = {"path": "notes/test.md", "page_id": "fixture-page"}
        self.client = FakeNotion(self.source)
        self.baseline = {
            "local": SYNC.digest(self.source),
            "remote": SYNC.remote_digest(self.client.title, self.client.body),
        }
        for name, value in (("ROOT", self.root), ("LOCAL", self.root / ".local/notion-sync")):
            context = patch.object(SYNC, name, value)
            context.start()
            self.addCleanup(context.stop)

    def sync(self, operation="sync", baseline=None):
        return SYNC.sync_mapping(
            self.client, self.mapping,
            self.baseline if baseline is None else baseline, operation,
        )

    def test_roundtrip_preserves_dates_code_links_and_unicode(self):
        source = (
            "# 学习笔记\n\n记录日期：2026-10-26。\n\n"
            "[讲义](../course/example.pdf#page=23)\n\n"
            "`2026-10-26` 是字面代码。\n\n"
            "```text\n2026-10-26\n[example](../literal.md)\n```\n"
        )
        title, body = SYNC.render(source, "notes/test.md")
        self.assertIn('<date start="2026-10-26" />', body)
        self.assertIn("example.pdf#page=23", body)
        self.assertIn("`2026-10-26`", body)
        self.assertIn("```text\n2026-10-26", body)
        self.assertEqual("# " + title + "\n\n" + SYNC.markdown_body(body, "notes/test.md"), source)

    def test_notion_inline_markup_converts_to_readable_github_markdown(self):
        body = '## <code>MA := PC</code>\n\n<b>寄存器</b>与 <code>A&lt;B</code>。\n'
        self.assertEqual(
            SYNC.markdown_body(body, "notes/test.md"),
            "## `MA := PC`\n\n**寄存器**与 `A<B`。\n",
        )
        self.assertEqual(
            SYNC.markdown_body("<code>&lt;div&gt;</code>", "notes/test.md"),
            "`<div>`\n",
        )

    def test_code_examples_are_not_parsed_as_rich_blocks_or_date_mentions(self):
        source = "# Note\n\n```text\n```json\n2026-10-26\n<toggle>literal</toggle>\n```\n"
        _, body = SYNC.render(source, "notes/test.md")
        self.assertNotIn("<date", body)
        self.assertIn("<toggle>literal</toggle>", body)
        self.assertEqual(SYNC.markdown_body(body, "notes/test.md"), SYNC.split_note(source)[1])
        with self.assertRaisesRegex(ValueError, "raw HTML"):
            SYNC.render("# Note\n\n<toggle>rich block</toggle>", "notes/test.md")

    def test_all_change_directions_are_distinguished(self):
        cases = [
            ("a", "b", None, "uninitialized"),
            ("a", "b", {"local": "a", "remote": "b"}, "unchanged"),
            ("x", "b", {"local": "a", "remote": "b"}, "push"),
            ("a", "y", {"local": "a", "remote": "b"}, "pull"),
            ("x", "y", {"local": "a", "remote": "b"}, "conflict"),
        ]
        for local, remote, baseline, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(SYNC.choose_action(local, remote, baseline), expected)

    def test_matching_initial_copies_establish_baseline_without_writing(self):
        result = SYNC.sync_mapping(self.client, self.mapping, None, "init")
        self.assertEqual(result, self.baseline)
        self.assertEqual(self.client.writes, [])

    def test_different_initial_copies_are_not_adopted(self):
        self.client.body += "\nA remote addition.\n"
        with self.assertRaisesRegex(ValueError, "Initial copies differ"):
            SYNC.sync_mapping(self.client, self.mapping, None, "init")
        self.assertEqual(self.note.read_text(), self.source)
        self.assertEqual(self.client.writes, [])

    def test_unchanged_pair_is_a_noop(self):
        self.assertEqual(self.sync(), self.baseline)
        self.assertEqual(self.client.writes, [])
        self.assertEqual(self.note.read_text(), self.source)

    def test_local_edit_pushes_and_readback_is_checked(self):
        source = self.source.replace("Original paragraph.", "New local paragraph.")
        self.note.write_text(source)
        result = self.sync()
        self.assertEqual(SYNC.markdown_body(self.client.body, "notes/test.md"), SYNC.split_note(source)[1])
        self.assertEqual(result["local"], SYNC.digest(source))
        self.assertEqual(len(self.client.writes), 1)

    def test_remote_edit_pulls_without_writing_notion(self):
        self.client.body = self.client.body.replace("Original paragraph.", "New remote paragraph.")
        self.sync()
        self.assertIn("New remote paragraph.", self.note.read_text())
        self.assertEqual(self.client.writes, [])

    def test_both_sides_changed_preserves_both_and_stops(self):
        self.note.write_text(self.source + "\nLocal addition.\n")
        self.client.body += "\nRemote addition.\n"
        with self.assertRaisesRegex(ValueError, "Both copies changed"):
            self.sync()
        self.assertIn("Local addition.", self.note.read_text())
        snapshots = list((self.root / ".local/notion-sync/conflicts").iterdir())
        self.assertEqual(len(snapshots), 1)
        self.assertIn("Remote addition.", (snapshots[0] / "notion.md").read_text())
        self.assertEqual(self.client.writes, [])

    def test_matching_edits_on_both_sides_are_adopted_without_writes(self):
        source = self.source + "\nThe same addition.\n"
        self.note.write_text(source)
        self.client.title, self.client.body = SYNC.render(source, "notes/test.md")
        result = self.sync()
        self.assertEqual(result["local"], SYNC.digest(source))
        self.assertEqual(self.client.writes, [])

    def test_targeted_patch_keeps_unrelated_sections(self):
        original = "\n\n".join(f"Paragraph {i}." for i in range(30)) + "\n"
        changed = original.replace("Paragraph 15.", "Revised paragraph.")
        patches = SYNC.content_updates(original, changed, "notes/test.md")
        self.assertEqual(len(patches), 1)
        self.assertLess(len(patches[0]["old_str"]), len(original) // 2)
        self.assertEqual(original.replace(patches[0]["old_str"], patches[0]["new_str"]), changed)

    def test_remote_edit_during_push_is_not_overwritten(self):
        self.note.write_text(self.source + "\nLocal addition.\n")
        self.client.on_fetch = lambda client: (
            setattr(client, "body", client.body + "\nConcurrent remote edit.\n")
            if client.fetches == 2 else None
        )
        with self.assertRaisesRegex(ValueError, "Notion changed during sync"):
            self.sync()
        self.assertEqual(self.client.writes, [])
        self.assertIn("Concurrent remote edit.", self.client.body)

    def test_local_edit_during_pull_is_not_overwritten(self):
        self.client.body += "\nRemote addition.\n"
        self.client.on_fetch = lambda client: self.note.write_text(self.source + "\nConcurrent local edit.\n")
        with self.assertRaisesRegex(ValueError, "Local note changed during sync"):
            self.sync()
        self.assertIn("Concurrent local edit.", self.note.read_text())

    def test_rich_notion_content_is_saved_instead_of_lost(self):
        self.client.body += "\n<toggle>Rich content</toggle>\n"
        with self.assertRaisesRegex(ValueError, "unsupported rich content"):
            self.sync()
        self.assertEqual(self.note.read_text(), self.source)
        snapshots = list((self.root / ".local/notion-sync/conflicts").glob("*/notion.raw.md"))
        self.assertEqual(len(snapshots), 1)
        self.assertIn("<toggle>", snapshots[0].read_text())

    def test_paths_outside_personal_notes_are_rejected(self):
        self.mapping["path"] = "../private.md"
        with self.assertRaisesRegex(ValueError, "Only explicitly mapped"):
            self.sync()
        self.assertEqual(self.client.fetches, 0)

    def test_incomplete_remote_page_is_rejected(self):
        for key, value in (("truncated", True), ("unknown_block_count", 1)):
            with self.subTest(key=key):
                page = self.client.page()
                page[key] = value
                with self.assertRaisesRegex(ValueError, "incomplete page"):
                    SYNC.page_content(page)

    def test_api_error_payload_is_not_treated_as_a_successful_write(self):
        client = SYNC.Notion.__new__(SYNC.Notion)
        client.runtime = {}
        error = {"name": "APIResponseError", "status": 400, "code": "validation_error", "message": "Bad update"}
        for payload in (
            {"content": [{"type": "text", "text": json.dumps(error)}]},
            {"structuredContent": error},
        ):
            with self.subTest(payload=tuple(payload)), patch.object(
                SYNC.shutil, "which", return_value="/node"
            ), patch.object(
                SYNC.subprocess, "run",
                return_value=SimpleNamespace(returncode=0, stdout=json.dumps(payload)),
            ):
                with self.assertRaisesRegex(RuntimeError, "validation_error"):
                    client.call("notion-update-page", {})


if __name__ == "__main__":
    unittest.main()
