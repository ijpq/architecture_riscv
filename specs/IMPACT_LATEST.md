# Local CS152 environment recovery

## Target
Restore local build and execution for Lab 1–5 without completing student exercises. Preserve the course processors for Labs 1/2/3/5. After the original Lab 4 toolchain proved unavailable, the user explicitly authorized a separate modern RVV replacement (not an equivalent implementation of the old timing model).

## Baseline
- Lab 1: `chipyard-cs152-sp23` (2023), Chisel 3.5.2.
- Lab 2: `edu_cs152/lab2` (2022), Chisel 3.4.1; internal course jar is present.
- Lab 3: `edu_cs152/lab3` (2022), Chisel 3.4.4, BOOM.
- Lab 4: `edu_cs152/lab4`, RVV 0.10 and a timing-enabled course Spike.
- Lab 5: `edu_cs152/lab5` (2021/2022), course-modified Rocket coherence implementation.
- Existing uncommitted changes and missing tracked symlinks were present before recovery. Do not reset changes or overwrite optimized exercise files. Restore an absent build-resource symlink only when its tracked target exists, and record the restoration; keep exercise-file deletions untouched.

## Dependents
Build plugins, dependency repositories, Java, RISC-V tools, submodules and shared Makefiles affect hardware generation and every simulator. Keep legacy toolchains isolated. Do not change the global Git configuration, system Java, or the existing Conda installation.

## Affected stories
No release-plan or story metadata existed before this work. User request: recover all labs locally before studying.

## Test coverage
The initial investigation only ran three existing Sodor binaries. No complete source rebuild had passed. Acceptance must include fresh Scala/RTL/C++ builds, benchmark execution with success/exit checks, representative alternative configurations, and a rebuild after a configuration edit. Unimplemented student assembly kernels are not environment failures; test the supplied reference/scalar harness without filling in answers.

## Remote dependencies
Remove Berkeley-specific absolute paths from the local entry points. Use Verilator rather than licensed VCS/FPGA services for local RTL simulation. Preserve timing behavior where performance experiments require it. SPEC CPU2006 and unavailable restricted course artifacts must be reported as explicit limitations, not silently substituted.

## REA decision
Inspected `morluto/rea` at commit `080c0e2b2b82a7d9394b59d3d86630d9d85346a5`. Its skill says to skip REA for ordinary source-repository architecture analysis. It is a reverse-engineering tool, not an environment recovery tool. Do not install its native analysis stack for these source-available labs.

## Authorized modern Lab 4 extension
- Keep `edu_cs152/lab4` intact and keep its original-toolchain blocker visible.
- Add independent `lab4-modern` tooling, Linux SE runtime adapters, RVV 1.0 exercise stubs, and a pinned gem5 O3/timing-cache configuration.
- Shared CLI changes affect help, dispatch, and aggregate doctor status only; existing Labs 1/2/3/5 command construction and evidence validation must not change.
- gem5 arithmetic micro-operations are per vector register, not physical lanes. VLEN, functional-unit latency/count and memory timing are model parameters, not equivalents of the original `dlen` or chaining model.
- New tests: parameter rejection, failed/missing ROI/exit handling, evidence fingerprint invalidation, real RVV self-checks at two VLENs, latency sensitivity, and original scalar verification harnesses. Unfinished vector exercises cannot produce readiness evidence.
- Original recovery branch `local/lab4-modern` preserved the dirty tree without staging or committing. The later complete-course request explicitly authorizes selected course/environment commits on `learn/cs152-complete`; unrelated changes must still not be staged, reset or stashed.
- Detailed implementation and acceptance: `specs/LAB4_MODERN_PLAN.md`.

## Authorized complete-course branch
- Add attributable Spring 2023 public teaching materials, Chinese gap-filling instruction, assignment/lab mappings, and source snapshots sufficient to restore the selected experiments.
- The user explicitly approved committing only selected course material, local support, and necessary lab sources to `learn/cs152-complete`, without a remote push.
- Never absorb the old NAS link, unrelated working-tree edits, Conda directories, generated outputs, or unrestricted nested Git histories into the commit.
- New coverage: PDF/source manifests, local links, curriculum completeness, safe no-overwrite source restoration, source fingerprints, and a clean-checkout materialization check. Reuse the verified runtime environment without changing processor behavior.
- Detailed scope: `specs/COURSE_BRANCH_PLAN.md`.

## Risk: High
Several generations of build systems share environment tools, and original dependency repositories have disappeared. Recover in isolated steps and retain full command logs.

## Recommended action
Add local setup/doctor/build/verify scripts and dependency locks. Prefer packaging-only patches over hardware changes. Mark a lab ready only after its own build and execution checks pass.
