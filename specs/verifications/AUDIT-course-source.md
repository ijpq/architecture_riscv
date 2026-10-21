---
type: code-audit
context: learn/cs152-complete source snapshot delivery
---

# Source snapshot self-audit

## Result

PASS for the source pack/check/restore implementation. This is a self-review, not an independent review. The user has not authorized delegation.

- ✓ Correctness: eleven public-interface fixture tests pass. They exercise tracked edits, executable bits, relative symlinks, nested repositories, shallow history, retained tags, and preservation of existing student work.
- ✓ Regression protection: tests cover archive corruption, traversal, absolute paths, archive hard links/devices, duplicate members, symlink ancestors, symlink-chain escapes, cycles, destination-parent symlinks, credentials/hooks exclusion, archive replacement and dangling archive symlinks.
- ✓ Security: all archive hashes and member structure are checked before installation. No `extractall`, shell interpolation, executable hooks, private Git config or credentials are imported. Only temporary extraction directories are populated; no file writes follow archive symlinks. Existing nonempty directories are kept, not overwritten.
- ✓ Dependencies: Python standard library and the existing Git executable only; no new package or service.
- ✓ Scope: no changes to student TODOs, NAS contents, Conda installations or full Git histories. Only explicit compatibility files accompany tracked working sources.
- ✓ Performance: archives are streamed for SHA-256; a 2 GiB unpacked-size ceiling rejects oversized headers. Manifest verification deliberately checks all source bundles, even for a selective restore.
- ✓ Clarity: archive safety, Git metadata and orchestration are separate modules, all below 200 lines. Public production functions have parameter and return annotations.
- ✓ Tests: fixtures use disposable directories and local Git repositories, without network access. No external course environment or prior build result is required.

## Applicable conventions and limitations

There is no project `CONVENTIONS.md`; no project convention was fabricated. General skill preferences such as 4–20-line functions are guidance, not an existing repository constraint. Several straightforward orchestration/validation functions exceed twenty lines; splitting the three responsibilities into separate small modules preserves a readable validation order.

The tool is a local, unprivileged source installer, not a hostile multi-user sandbox. It checks destination symlinks, but does not promise protection against another process changing the directory tree concurrently. It does not make source code from upstream trustworthy: original licenses and source provenance remain in the archives and source manifest.

## Test-first evidence

- Initial source-roundtrip RED: `6ebd473`.
- Preserve-work/security RED: `500392d`.
- A later dangling-archive-symlink regression failed with `AssertionError: ValueError not raised`, then passed after checking `is_symlink()` as well as `exists()`.
- Nested untagged repositories exposed a missing empty `.git/refs` directory. The snapshot now includes it, and shallow nested repository restoration passes.

## Fresh-checkout follow-up

The isolated build exposed two gaps that a warm working tree concealed. The source selector now includes `tools/api-config-chipsalliance`, `tools/rocket-dsp-utils`, open-lab benchmark gitlinks and RISC-V tests' `env/encoding.h`. Fixture subtests failed for these dependencies before the selector was corrected. The six final archives contain 106 source repositories.

The CLI now creates the generated `.java_tmp` directory before Make sets `java.io.tmpdir` to it. A regression test failed before the fix and passed afterward. This does not change simulator semantics, student source code or the original pinned Scala versions. Lab5's Make prerequisite builds local FIRRTL before invoking sbt; a standalone `sbt compile` is not an equivalent cold-build test.

Four default RTL configurations were then built and run in the isolated checkout, without copying host simulators, Scala targets or C++ objects. A manually shortened 120-second Lab2 timeout failed and was retained as a failed attempt; the same program completed within the documented default 900-second limit. Full timing and scope are recorded in the course-delivery verification.

No independent reviewer was dispatched. The final course-delivery verification records real source restoration and environment checks separately.
