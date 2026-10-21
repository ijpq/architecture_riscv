# Repository Guidelines

## Project Structure & Module Organization

This repository provides a CS152 self-study course and local RISC-V laboratory environment.

- `course/`: roadmap, lab guides, original PDFs, material-fetching tools, and hash-checked source archives in `sources/`.
- `scripts/cs152-local/`: Python CLI, environment wrappers, runtime checks, plotting utilities, and adjacent tests.
- `lab4-modern/`: RVV 1.0 assembly exercises, C runtime adapters, and gem5 configuration.
- `chipyard-cs152-sp23/` and `edu_cs152/lab{2,3,4,5}/`: restored upstream lab sources; these directories are ignored by the root repository.
- `docs/` and `specs/`: environment instructions, plans, and verification records. `.local/` holds ignored toolchains, builds, logs, and evidence.

## Build, Test, and Development Commands

Run commands from the repository root. Follow `course/SOURCES.md` and `docs/LOCAL_ENVIRONMENT.md` for prerequisites; use Java 11 for legacy RTL builds.

- `python3 course/source_bundle.py check`: validate bundled source archives.
- `python3 course/source_bundle.py restore`: restore missing sources while preserving nonempty directories.
- `source scripts/cs152-local/env.sh`: configure tools for direct shell commands; the CLI loads this automatically.
- `scripts/cs152-local/cs152 setup lab2`: prepare Lab 2 dependencies.
- `scripts/cs152-local/cs152 build lab2`: regenerate and build its RTL simulator.
- `scripts/cs152-local/cs152 benchmarks lab2`: compile benchmark programs.
- `scripts/cs152-local/cs152 run lab2 edu_cs152/lab2/lab/directed/transpose.riscv --preload`: run a benchmark locally.
- `scripts/cs152-local/cs152 doctor all --lab4 modern`: inspect readiness and recorded runtime evidence.

## Coding Style & Naming Conventions

Use four-space indentation and `snake_case` functions in Python. Keep Scala/Chisel class and configuration names in CamelCase, such as `Sodor3StageConfig`. Match surrounding C, assembly, and shell style. No repository-wide formatter or linter is configured.

## Testing Guidelines

Tests use Python's standard-library `unittest`, with `test_*.py` files and descriptive `test_*` methods:

```bash
python3 -m unittest discover -s course -p 'test_*.py' -v
python3 -m unittest discover -s scripts/cs152-local -p 'test_*.py' -v
```

No numerical coverage threshold is configured. Add regression tests for tooling behavior changes. For simulator changes, rebuild and rerun affected benchmarks before checking `doctor`; stale evidence and timeouts cannot establish success.

## Commit & Pull Request Guidelines

Follow recent commit subjects: `feat(course): ...`, `fix(course): ...`, `test(course): ...`, or `docs(course): ...`. Keep changes focused. PRs should describe affected labs, behavior changes, validation commands/results, and relevant issues. Include model settings and measured cycles for performance claims.

## Source Preservation

Avoid recursive root submodule initialization; legacy Gitlinks reference private repositories. Preserve student edits and exercise TODOs. Modern Lab 4 uses RVV 1.0/gem5; document its model limitations when discussing original RVV 0.10 results.
