#!/usr/bin/env python3
"""Public snapshot API integration tests using small real Git repositories."""
import importlib.util
import os
from pathlib import Path
import subprocess
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


if __name__ == "__main__":
    unittest.main()
