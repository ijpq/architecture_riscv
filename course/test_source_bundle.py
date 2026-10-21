#!/usr/bin/env python3
"""Public snapshot API integration tests using small real Git repositories."""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("source_bundle", Path(__file__).with_name("source_bundle.py"))
BUNDLES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUNDLES)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


class SourceBundleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        self.repo = self.source / "fixture"
        self.repo.mkdir(parents=True)
        git(self.repo, "init", "-q")
        (self.repo / "source.c").write_text("int original;\n")
        (self.repo / "LICENSE").write_text("Fixture license, not third-party code.\n")
        (self.repo / "resource").symlink_to("source.c")
        (self.repo / "run.sh").write_text("#!/bin/sh\nexit 0\n")
        (self.repo / "run.sh").chmod(0o755)
        git(self.repo, "add", "source.c", "LICENSE", "resource", "run.sh")
        git(self.repo, "-c", "user.name=Snapshot Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture: first")
        git(self.repo, "-c", "user.name=Snapshot Fixture", "-c", "user.email=fixture@example.invalid", "tag", "-a", "v1.0", "-m", "fixture tag")
        self.head = git(self.repo, "rev-parse", "HEAD")
        (self.repo / "source.c").write_text("int local_fix;\n")
        (self.repo / "target").mkdir()
        (self.repo / "target/cache.bin").write_bytes(b"must not enter source package")
        self.bundle_dir = self.base / "bundles"
        self.destination = self.base / "restored"
        self.destination.mkdir()

    def test_working_sources_and_pinned_git_state_survive_roundtrip(self):
        BUNDLES.pack_bundles(self.source, self.bundle_dir, {"lab1": "fixture"})
        BUNDLES.restore_bundles(self.destination, self.bundle_dir)
        restored = self.destination / "fixture"
        self.assertEqual((restored / "source.c").read_text(), "int local_fix;\n")
        self.assertEqual(git(restored, "rev-parse", "HEAD"), self.head)
        self.assertEqual(git(restored, "describe", "--tags", "--exact-match", "HEAD"), "v1.0")
        self.assertEqual(git(restored, "show", "HEAD:source.c"), "int original;")
        self.assertEqual(os.readlink(restored / "resource"), "source.c")
        self.assertTrue(os.access(restored / "run.sh", os.X_OK))
        self.assertFalse((restored / "target").exists())
        self.assertIn("M source.c", git(restored, "status", "--porcelain"))

    def package(self):
        return BUNDLES.pack_bundles(self.source, self.bundle_dir, {"lab1": "fixture"})

    def rewrite_archive(self, members):
        manifest = json.loads((self.bundle_dir / "manifest.json").read_text())
        entry = manifest["bundles"][0]
        archive = self.bundle_dir / entry["archive"]
        with tarfile.open(archive, "w:gz") as handle:
            for name, kind, target in members:
                member = tarfile.TarInfo(name)
                member.type = kind
                member.linkname = target
                payload = b"untrusted archive content"
                member.size = len(payload) if kind == tarfile.REGTYPE else 0
                handle.addfile(member, io.BytesIO(payload) if member.size else None)
        entry["bytes"] = archive.stat().st_size
        entry["sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        (self.bundle_dir / "manifest.json").write_text(json.dumps(manifest))

    def test_nonempty_directory_is_kept_without_touching_student_work(self):
        self.package()
        existing = self.destination / "fixture"
        existing.mkdir()
        (existing / "source.c").write_text("my unfinished exercise\n")
        results = BUNDLES.restore_bundles(self.destination, self.bundle_dir)
        self.assertEqual((existing / "source.c").read_text(), "my unfinished exercise\n")
        self.assertFalse((existing / ".git").exists())
        self.assertEqual(results, ["KEEP lab1: existing nonempty directory"])

    def test_hash_mismatch_is_rejected_before_restoration(self):
        manifest = self.package()
        with (self.bundle_dir / manifest["bundles"][0]["archive"]).open("ab") as handle:
            handle.write(b"corruption")
        with self.assertRaisesRegex(ValueError, "hash/size mismatch"):
            BUNDLES.restore_bundles(self.destination, self.bundle_dir)
        self.assertEqual(list(self.destination.iterdir()), [])

    def test_unsafe_members_are_rejected_before_any_files_are_installed(self):
        self.package()
        cases = [
            [("payload/../../escape", tarfile.REGTYPE, "")],
            [(str(self.base / "absolute-escape"), tarfile.REGTYPE, "")],
            [("payload/resource", tarfile.SYMTYPE, "../../escape")],
            [("payload/resource", tarfile.SYMTYPE, str(self.base / "absolute-escape"))],
            [("payload/resource", tarfile.LNKTYPE, "payload/source.c")],
            [("payload/device", tarfile.CHRTYPE, "")],
            [("payload/source.c", tarfile.REGTYPE, ""), ("payload/source.c", tarfile.REGTYPE, "")],
            [("payload/alias", tarfile.SYMTYPE, "directory"), ("payload/alias/file", tarfile.REGTYPE, "")],
        ]
        for number, members in enumerate(cases):
            with self.subTest(members=members):
                case_destination = self.destination / str(number)
                case_destination.mkdir()
                self.rewrite_archive(members)
                with self.assertRaises(ValueError):
                    BUNDLES.restore_bundles(case_destination, self.bundle_dir)
                self.assertEqual(list(case_destination.iterdir()), [])
                self.assertFalse((self.base / "absolute-escape").exists())

    def test_manifest_cannot_redirect_destination_outside_project(self):
        self.package()
        path = self.bundle_dir / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["bundles"][0]["destination"] = "../escape"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            BUNDLES.restore_bundles(self.destination, self.bundle_dir)
        self.assertFalse((self.base / "escape").exists())

    def test_destination_parent_symlink_is_not_followed(self):
        self.package()
        outside = self.base / "outside"
        outside.mkdir()
        (self.destination / "link").symlink_to(outside, target_is_directory=True)
        path = self.bundle_dir / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["bundles"][0]["destination"] = "link/fixture"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            BUNDLES.restore_bundles(self.destination, self.bundle_dir)
        self.assertEqual(list(outside.iterdir()), [])

    def test_nested_sources_are_real_repositories_and_history_is_shallow(self):
        child = self.repo / "generators/core"
        child.mkdir(parents=True)
        git(child, "init", "-q")
        (child / "Core.scala").write_text("class FixtureCore\n")
        git(child, "add", "Core.scala")
        git(child, "-c", "user.name=Snapshot Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture: nested source")
        child_head = git(child, "rev-parse", "HEAD")
        git(self.repo, "add", "generators/core")
        git(self.repo, "-c", "user.name=Snapshot Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-qm", "fixture: add source gitlink")
        self.package()
        BUNDLES.restore_bundles(self.destination, self.bundle_dir)
        restored = self.destination / "fixture"
        self.assertEqual(git(restored, "rev-list", "--count", "HEAD"), "1")
        self.assertEqual(git(restored / "generators/core", "rev-parse", "HEAD"), child_head)
        self.assertEqual((restored / "generators/core/Core.scala").read_text(), "class FixtureCore\n")


if __name__ == "__main__":
    unittest.main()
