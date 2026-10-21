# Lab 4 modern local replacement — implementation plan

## Authorization and scope

The user selected a separate modern RVV replacement for the unavailable course
RVV 0.10 timing toolchain. Keep `edu_cs152/lab4` unchanged. Do not present this
replacement as the original timing model, and do not implement exercise answers.

The user also approved a new branch with all existing dirty files preserved.
Branch: `local/lab4-modern`. No stash, reset, staging, or commit was performed.
Baseline: all 25 local infrastructure unit tests passed before implementation
(`.local/logs/lab4-modern-preflight.log`). The approved preservation of existing
files is an explicit exception to the clean-tree kickoff procedure.

## Selected components

- gem5 v25.1.0.1, commit `c8222cc67a399bfc01e8658dd14b30d5bfd634f9`.
- RISC-V RVV 1.0, gem5 RiscvO3CPU and event-driven timing caches/memory.
- Existing `/usr/bin/riscv64-linux-gnu-gcc` 11.4.0, static Linux binaries.
  An assembly smoke test already compiles `vsetvli ..., e32, m1, ta, ma`.
- Private, version-pinned SCons installation; no global package changes.

## Model boundary

In this gem5 release, vector arithmetic uses one micro-operation per vector
register, with a host element loop inside that micro-operation. Its configured
functional-unit latency does not automatically scale with VLEN. This is not a
physical lane/chaining model. Expose VLEN, vector functional-unit latency/count,
and cache/memory timing explicitly. Do not invent an equivalent `dlen` option.
Use simulated ROI cycles and cache statistics, never host wall-clock duration
or functional Spike instruction counts, for performance comparisons.

## Vertical implementation slices

1. Add independent modern setup/build and strict model-parameter validation.
   Pin the source ref, isolate Python/build PATH, and retain build logs.
2. Add an explicit O3/timing-cache configuration and a non-answer RVV runtime
   check. Prove VLEN 128/512 and latency sensitivity with executable checks.
3. Adapt the existing seven scalar kernels, datasets, and verification routines
   to Linux SE through a small `setStats` bridge. Provide separate RVV 1.0
   exercise files with the original TODOs, not completed vector algorithms.
   Compile all harnesses; require scalar verification success. An unfinished
   vector exercise must fail verification, not count as an environment pass.
4. Integrate a distinct `lab4-modern` command, SHA-256-bound run evidence and a
   separate doctor status. Update local instructions, course-question mapping,
   and the machine-readable environment report. Preserve the blocked status of
   the original Lab 4 instead of silently switching implementations.

## Acceptance

- Fast, independent Python unit tests cover parameter rejection, source/build
  commands, stats/exit validation, and evidence invalidation.
- Real gem5 runs pass the RVV runtime self-check at VLEN 128 and 512.
- A dependent RVV instruction-chain check takes more simulated cycles when its
  functional-unit latency is increased; record both configurations and stats.
- All seven original scalar verification harnesses pass in the new runtime.
- The vector exercise harnesses build without supplying student answers; a
  known unfinished exercise is reported as failed/not implemented, not passed.
- Existing Lab 1/2/3/5 doctor checks and all infrastructure unit tests stay green.

## Completion evidence

All four slices are complete for the explicitly selected modern replacement.
The original RVV 0.10 timing environment remains blocked.

- gem5 built from the pinned source in 1274.9 seconds; build status is recorded
  in `.local/gem5-build-status.json` and `.local/logs/gem5-modern-build.log`.
- All 15 harnesses compile. Required modern runtime checks pass **11/11**:
  seven scalar kernels, the provided vector csaxpy example, and three probes.
- VLEN 128/512 probes verify 4/16 elements. The dependent-chain ROI grows from
  **598 to 1069 cycles** when latency changes from 1 to 8.
- The provided vector example also passes at VLEN 128, 512 and 1024; a probe
  passes with VLEN 1024, one vector unit, latency 8 and memory latency 80 ns.
- Negative integration checks reject a mismatched VLEN, reject an unfinished
  vector exercise, revoke prior success on failure, and map verify code 256 to
  guest exit 1 rather than false success. No exercise answers were supplied.
- All **51 infrastructure tests** pass. Existing RTL checks remain **21/21**.
  `scripts/cs152-local/cs152 doctor all --lab4 modern` returns 0 for **32/32**
  selected-route checks; the original-route command still returns 1.
- The real timing gate caught and led to a verified fix for an unused functional
  unit pool. Root-cause evidence is in `specs/bugs/BUG-LAB4-FU-ROUTING.md`.
- Usage: `docs/LOCAL_ENVIRONMENT.md` and `lab4-modern/README.md`.
  Snapshot: `specs/LOCAL_ENVIRONMENT_STATUS.json`; live state: `doctor`.

No external reviewer or subagent was dispatched. Local self-review and
executable verification were used; style and unavailable-checker limitations
are recorded separately in `specs/verifications/LOCAL_ENVIRONMENT_AUDIT.md`.
