#!/usr/bin/env python3
"""Local CS152 build/run entry point. No remote execution and no grading answers."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / "scripts/cs152-local"
LOCAL = ROOT / ".local"
DEFAULTS = {"lab1": "Sodor1StageConfig", "lab2": "CS152RocketConfig",
            "lab3": "CS152BaselineBoomConfig", "lab5": "Lab5MESIDualRocketConfig"}


def labroot(lab):
    return ROOT / ("chipyard-cs152-sp23" if lab == "lab1" else "edu_cs152/" + lab)


def config_name(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", value):
        raise argparse.ArgumentTypeError("CONFIG must be a Scala class name")
    return value


def positive_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise argparse.ArgumentTypeError("Limit must be a positive integer") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("Limit must be a positive integer")
    return number


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def execute(command, cwd, label, timeout=None):
    (LOCAL / "logs").mkdir(parents=True, exist_ok=True)
    logfile = LOCAL / "logs" / (label + ".log")
    print(f"RUN {label}\n  cwd: {cwd}\n  command: {shlex_join(command)}\n  log: {logfile}", flush=True)
    started = time.monotonic()
    with logfile.open("w") as out:
        out.write("cwd: " + str(cwd) + "\ncommand: " + shlex_join(command) + "\n")
        out.flush()
        try:
            with open(os.devnull) as null:
                result = subprocess.run(command, cwd=cwd, stdin=null, stdout=out,
                                        stderr=subprocess.STDOUT, timeout=timeout)
            rc = result.returncode
        except subprocess.TimeoutExpired:
            out.write("\nCS152: wall-clock timeout; this check did NOT pass.\n")
            rc = 124
    lines = logfile.read_text(errors="replace").splitlines()
    print("\n".join(line[:500] + (" ... [see full log]" if len(line) > 500 else "")
                    for line in lines[-12:]))
    print(f"EXIT {rc} ({time.monotonic() - started:.1f}s)", flush=True)
    if rc:
        raise RuntimeError(f"{label} failed with exit {rc}; see {logfile}")
    return logfile


def shlex_join(command):
    import shlex
    return shlex.join([str(x) for x in command])


def simulator(lab, config):
    return labroot(lab) / "sims/verilator" / ("simulator-chipyard-" + config)


def build(lab, config):
    if lab == "lab4":
        raise RuntimeError("Lab4 requires the course RVV 0.10 timing toolchain. See doctor and docs/LOCAL_ENVIRONMENT.md; standard Spike is NOT a replacement.")
    command = ["make", "-j" + os.environ.get("CS152_JOBS", "8"), "CONFIG=" + config]
    command += ["SBT_BIN=" + str(SUPPORT / "sbt"), "SBT=" + str(SUPPORT / "sbt")]
    command += ["VERILATOR=verilator --cc --exe --timing -Wno-fatal --max-num-width 1048576"]
    command += ["EXTRA_SIM_CXXFLAGS=-std=c++17", "EXTRA_SIM_CC_FLAGS=-std=c++17"]
    # Make does not track command-line flag changes. Only invalidate the generated
    # Verilator makefile when our build recipe changes, never student sources.
    signature = hashlib.sha256(shlex_join(command).encode()).hexdigest()
    stamp = LOCAL / "build-flags" / lab / config
    if not stamp.exists() or stamp.read_text() != signature:
        generated = labroot(lab) / "sims/verilator/generated-src"
        for directory in generated.glob("*." + config):
            for makefile in directory.glob("**/VTestHarness.mk"):
                makefile.unlink()
    # New Chipyard's Makefile sets java.io.tmpdir to this directory but does
    # not create it. It is generated state, so source snapshots omit it.
    (labroot(lab) / ".java_tmp").mkdir(exist_ok=True)
    execute(command, labroot(lab) / "sims/verilator", f"{lab}-{config}-build")
    stamp.parent.mkdir(parents=True, exist_ok=True)
    stamp.write_text(signature)
    binary = simulator(lab, config)
    evidence = {"lab": lab, "config": config, "binary": str(binary),
                "sha256": digest(binary), "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "command": command}
    (LOCAL / "evidence").mkdir(parents=True, exist_ok=True)
    (LOCAL / "evidence" / f"{lab}-{config}-build.json").write_text(json.dumps(evidence, indent=2) + "\n")


def elf_segments(binary):
    """Return file-backed PT_LOAD segments; accept little-endian RV32/RV64 ELFs."""
    data = Path(binary).read_bytes()
    if data[:4] != b"\x7fELF" or data[5:6] != b"\x01":
        raise RuntimeError("Expected a little-endian RISC-V ELF")
    if data[4] == 2:
        header_format, fmt = "<16sHHIQQQIHHHHHH", "<IIQQQQQQ"
    elif data[4] == 1:
        header_format, fmt = "<16sHHIIIIIHHHHHH", "<IIIIIIII"
    else:
        raise RuntimeError("Unsupported ELF class")
    if len(data) < struct.calcsize(header_format):
        raise RuntimeError("Truncated ELF header")
    header = struct.unpack_from(header_format, data)
    if header[2] != 243:
        raise RuntimeError("Expected RISC-V ELF machine type 243")
    if (header[9] < struct.calcsize(fmt) or header[10] > 4096 or
            header[5] + header[9] * header[10] > len(data)):
        raise RuntimeError("Truncated or invalid ELF program headers")
    result = []
    for index in range(header[10]):
        ph = struct.unpack_from(fmt, data, header[5] + index * header[9])
        if ph[0] != 1:
            continue
        if data[4] == 2:
            _, _, offset, virtual, physical, size, memsize, _ = ph
        else:
            _, offset, virtual, physical, size, memsize, _, _ = ph
        if offset + size > len(data) or size > memsize:
            raise RuntimeError("Truncated or invalid ELF load segment")
        result.append((physical, virtual, data[offset:offset + size], memsize))
    if not result:
        raise RuntimeError("ELF has no loadable segments")
    return result


def preload_options(binary):
    segments = elf_segments(binary)
    base = min(segment[0] for segment in segments) & ~7
    end = max(segment[0] + segment[3] for segment in segments)
    length = end - base
    if base < 0x80000000 or length <= 0 or length > 64 * 1024 * 1024:
        raise RuntimeError("HEX preload only supports a contiguous DRAM ELF up to 64 MiB")
    depth = 1 << max(0, ((length + 7) // 8 - 1).bit_length())
    dest = LOCAL / "loadmem" / (digest(binary) + ".hex")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if not dest.exists():
        fd, name = tempfile.mkstemp(dir=dest.parent, suffix=".tmp")
        temporary = Path(name)
        try:
            with os.fdopen(fd, "w") as out:
                # Old elf2hex parses its optional base with atoll: use decimal.
                subprocess.run(["elf2hex", "8", str(depth), str(binary), str(base)],
                               stdout=out, check=True)
            if not temporary.stat().st_size:
                raise RuntimeError("elf2hex produced no data")
            temporary.replace(dest)
        finally:
            temporary.unlink(missing_ok=True)
    return ["+loadmem_addr=" + format(base, "x"), "+loadmem=" + str(dest)]


def simulation_command(lab, config, binary, max_cycles, pk=None, preload=False, arguments=()):
    sim = simulator(lab, config)
    if lab == "lab5":
        if preload:
            raise RuntimeError("Lab5 HEX preload is not validated; omit --preload")
        command = [str(sim), "+dramsim", "+max-cycles=" + str(max_cycles)]
    else:
        command = [str(sim), "+permissive", "+dramsim",
                   "+dramsim_ini_dir=" + str(labroot(lab) / "generators/testchipip/src/main/resources/dramsim2_ini"),
                   "+max-cycles=" + str(max_cycles)]
        if preload:
            if lab not in ("lab2", "lab3") or pk:
                raise RuntimeError("--preload is validated only for bare-metal Lab2/3")
            command += preload_options(binary)
        command.append("+permissive-off")
    if pk:
        command.append(str(Path(pk).resolve(strict=True)))
    command.append(str(binary))
    command.extend(arguments)
    return command


def declared_harts(binary):
    """Read our compatibility constant from the ELF, not a stale .nharts file."""
    symbols = subprocess.check_output(["riscv64-unknown-elf-nm", str(binary)], text=True)
    match = re.search(r"^([0-9a-fA-F]+)\s+\w\s+nharts$", symbols, re.MULTILINE)
    if not match:
        return None
    address = int(match[1], 16)
    for _, virtual, data, _ in elf_segments(binary):
        offset = address - virtual
        if 0 <= offset <= len(data) - 4:
            return struct.unpack_from("<I", data, offset)[0]
    raise RuntimeError("ELF nharts symbol is not in a file-backed load segment")


def run(lab, config, binary, max_cycles, seconds, pk=None, preload=False, arguments=()):
    if lab == "lab4":
        raise RuntimeError("Lab4 timing tools have not been validated; refusing to silently run RVV 1.0 or fake cycle counts.")
    sim = simulator(lab, config)
    if not sim.is_file():
        raise RuntimeError(f"Build first: {sim}")
    binary = Path(binary).resolve(strict=True)
    if lab == "lab5":
        expected = 1 if config == "Lab5RocketConfig" else (2 if config in (
            "Lab5MESIDualRocketConfig", "Lab5MSIDualRocketConfig", "Lab5MIDualRocketConfig") else None)
        harts = declared_harts(binary)
        if expected is not None and harts is not None and harts != expected:
            raise RuntimeError(f"ELF NHARTS={harts}, but {config} has {expected}; rebuild benchmarks --harts {expected}")
    command = simulation_command(lab, config, binary, max_cycles, pk, preload, arguments)
    evidence_file = LOCAL / "evidence" / f"{lab}-{config}-{binary.stem}-run.json"
    evidence_file.unlink(missing_ok=True)
    logfile = execute(command, sim.parent, f"{lab}-{config}-{binary.stem}-run", timeout=seconds)
    # Exit 0 is necessary, not sufficient: old HTIF runtimes can print a trap.
    text = logfile.read_text(errors="replace")
    if re.search(r"(?:\*\*\* FAILED|TRAP:|Assertion failed|terminate called)", text):
        raise RuntimeError(f"Simulator printed a failure despite exit 0: {logfile}")
    evidence = {"lab": lab, "config": config, "binary": str(binary),
                "binary_sha256": digest(binary), "simulator_sha256": digest(sim),
                "log": str(logfile), "log_sha256": digest(logfile), "command": command,
                "time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "passed": True}
    if pk:
        evidence.update(pk=str(Path(pk).resolve()), pk_sha256=digest(Path(pk)))
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text(json.dumps(evidence, indent=2) + "\n")
    return logfile


def benchmarks(lab, harts):
    root = labroot(lab)
    if lab == "lab1":
        compiler = os.environ["CS152_RV32_GCC"]
        if not Path(compiler).is_file():
            raise RuntimeError("Missing RV32 multilib compiler. Run: cs152 setup lab1")
        source = ROOT / "chipyard/toolchains/riscv-tools/riscv-tests/benchmarks"
        output = LOCAL / "benchmarks/lab1"
        output.mkdir(parents=True, exist_ok=True)
        # xPack has no native TLS. These are single-hart benchmarks: the old
        # printf buffer needs no thread-local storage. ISA spec 2.2 includes
        # CSR instructions in I and keeps GCC's rv32i/ilp32 multilib selected.
        flags = ("-DPREALLOCATE=1 -D__thread= -march=rv32i -mabi=ilp32 -misa-spec=2.2 "
                 "-mcmodel=medany -static -std=gnu99 -O2 -ffast-math -fno-common "
                 "-fno-builtin-printf -fno-tree-loop-distribute-patterns "
                 "-Wno-implicit-function-declaration")
        execute(["make", "-B", "-j2", "-f", str(source / "Makefile"),
                 "src_dir=" + str(source), "XLEN=32", "RISCV_GCC=" + compiler,
                 "RISCV_GCC_OPTS=" + flags,
                 "RISCV_OBJDUMP=" + os.environ["CS152_RV32_OBJDUMP"] + " -d",
                 "bmarks=median qsort rsort towers vvadd multiply dhrystone spmv", "riscv"],
                output, "lab1-rv32-benchmarks")
        custom = root / "generators/riscv-sodor/test/custom-bmarks"
        execute(["make", "-B", "CC=" + compiler + " -march=rv32i -mabi=ilp32 -misa-spec=2.2",
                 "OBJDUMP=" + os.environ["CS152_RV32_OBJDUMP"]], custom, "lab1-custom-benchmarks")
        shutil.copy2(custom / "mix.riscv", output / "mix.riscv")
        print("Rebuilt editable RV32 benchmarks: " + str(output))
    elif lab == "lab2":
        execute(["make", "-B", "-j2"], root / "lab/directed", "lab2-directed-benchmarks")
        # open1 defaults to a long RTL sweep, open3 to licensed SPEC. Build only.
        execute(["make", "-B", "ccbench-caches"], root / "lab/open1", "lab2-open1-benchmarks")
        execute(["make", "-j2", "gapbs"], root / "lab/open2", "lab2-open2-benchmarks")
        print("SKIP optional open3: licensed SPEC CPU2006 is not bundled.")
    elif lab == "lab3":
        execute(["make", "-B", "-j2"], root / "lab/open2", "lab3-open2-benchmarks")
        checks = LOCAL / "checks"
        checks.mkdir(parents=True, exist_ok=True)
        execute(["riscv64-unknown-elf-gcc", "-O2", "-std=gnu11", "-specs=nano.specs",
                 "-o", str(checks / "pk-victim.riscv"), str(SUPPORT / "checks/pk-victim.c")],
                ROOT, "lab3-pk-victim-build")
        execute(["riscv64-unknown-elf-gcc", "-O2", "-std=gnu11", "-specs=htif_nano.specs",
                 "-o", str(checks / "boom-runtime.riscv"), str(SUPPORT / "checks/boom-runtime.c")],
                ROOT, "lab3-boom-runtime-build")
    elif lab == "lab5":
        execute(["make", "-j2", "NHARTS=" + str(harts)], root / "lab", f"lab5-p{harts}-benchmarks")
        output = LOCAL / "benchmarks" / f"lab5-p{harts}"
        output.mkdir(parents=True, exist_ok=True)
        for binary in (root / "lab").glob("*.riscv"):
            shutil.copy2(binary, output / binary.name)
        print("Core-count-specific benchmarks: " + str(output))
    else:
        raise RuntimeError("Lab4 is blocked on its legacy RVV/timing toolchain; see doctor.")


CHECKS = {
    "lab1": [(config, name, r"mcycle" if name == "towers" else "")
             for config in ("Sodor1StageConfig", "Sodor3StageConfig", "Sodor5StageConfig")
             for name in ("towers", "mix")],
    "lab2": [("CS152RocketConfig", "transpose", r"cycles\s*:\s*[1-9]"),
             ("CS152RocketConfig", "bfs", r"Verification:\s+PASS"),
             ("CS152RocketL2Config", "caches", r"\[caches\]"),
             ("CS152RocketMysteryConfig", "caches", r"\[caches\]"),
             ("CS152RocketNoPrefetchConfig", "bfs", r"Verification:\s+PASS"),
             ("CS152RocketPrefetchConfig", "bfs", r"Verification:\s+PASS")],
    "lab3": [(config, "boom-runtime", r"CS152_BOOM_RUNTIME_PASS cycles=[1-9][0-9]* instret=[1-9]") for config in (
        "CS152BaselineBoomConfig", "CS152SWPredBoomConfig", "CS152SmallBoomConfig")] + [
        ("CS152SmallBoomConfig", "pk-victim", r"CS152_PK_VICTIM_PASS")],
    "lab5": [(config, "mt-vvadd-naive", r"vvadd_naive:.*cycles") for config in (
        "Lab5RocketConfig", "Lab5MESIDualRocketConfig", "Lab5MSIDualRocketConfig", "Lab5MIDualRocketConfig")] + [
        ("Lab5MESIDualRocketConfig", "mt-matmul-naive", r"matmul_naive:.*cycles")],
}


def valid_run_evidence(lab, config, name, marker):
    """Readiness means an unchanged ELF/simulator/log, not just an executable."""
    path = LOCAL / "evidence" / f"{lab}-{config}-{name}-run.json"
    try:
        evidence = json.loads(path.read_text())
        if evidence.get("passed") is not True:
            return False, "not marked passed"
        for file, key in ((Path(evidence["binary"]), "binary_sha256"),
                          (simulator(lab, config), "simulator_sha256"),
                          (Path(evidence["log"]), "log_sha256")):
            if digest(file) != evidence[key]:
                return False, "changed artifact: " + str(file)
        if name == "pk-victim" and not evidence.get("pk"):
            return False, "missing proxy-kernel fingerprint"
        if evidence.get("pk") and digest(Path(evidence["pk"])) != evidence["pk_sha256"]:
            return False, "changed proxy kernel"
        if not re.search(marker, Path(evidence["log"]).read_text(errors="replace")):
            return False, "required runtime output missing"
        return True, "verified"
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return False, "missing/invalid evidence: " + str(exc)


def doctor(selected="all", lab4_mode="original"):
    ok = True
    for tool in ("java", "verilator", "riscv64-unknown-elf-gcc", "elf2hex", "spike", "make", "g++"):
        found = shutil.which(tool)
        print(f"{'FOUND' if found else 'MISSING'} {tool}: {found or '-'}")
        ok &= found is not None
    if selected in ("all", "lab1"):
        compiler = os.environ.get("CS152_RV32_GCC", "")
        found = bool(compiler and shutil.which(compiler))
        print(f"{'FOUND' if found else 'MISSING'} RV32 multilib: {compiler}")
        ok &= found
    for lab, checks in CHECKS.items():
        if selected not in ("all", lab):
            continue
        results = [(config, name, *valid_run_evidence(lab, config, name, marker))
                   for config, name, marker in checks]
        count = sum(result[2] for result in results)
        ready = count == len(checks)
        print(f"{'READY' if ready else 'NOT READY'} {lab}: {count}/{len(checks)} runtime checks have valid fingerprints")
        for config, name, passed, reason in results:
            if not passed:
                print(f"  {config}/{name}: {reason}")
        ok &= ready
    if selected in ("all", "lab4"):
        if lab4_mode == "modern":
            import lab4_modern
            print("SELECTED lab4-modern: explicit RVV 1.0 replacement; NOT original Lab 4.")
            ok &= lab4_modern.doctor() == 0
        else:
            print("BLOCKED lab4: course RVV0.10 compiler + timing Spike package is missing; ordinary Spike is NOT equivalent.")
            ok = False
    print("NOTE SPEC CPU2006 is licensed/optional and not bundled. See docs/LOCAL_ENVIRONMENT.md for scope.")
    return 0 if ok else 1


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "lab4-modern":
        import lab4_modern
        return lab4_modern.main(sys.argv[2:])
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("lab4-modern", help="separate RVV 1.0/gem5 replacement; use lab4-modern --help")
    plot = sub.add_parser("plot-caches", help="Python 3 CSV/SVG plotter; no Python 2 or matplotlib")
    plot.add_argument("logs", nargs="+")
    plot.add_argument("--output", required=True, help="Output prefix without .csv/.svg suffix")
    check = sub.add_parser("doctor")
    check.add_argument("lab", nargs="?", default="all", choices=("all", "lab1", "lab2", "lab3", "lab4", "lab5"))
    check.add_argument("--lab4", dest="lab4_mode", choices=("original", "modern"), default="original",
                       help="explicitly select the modern replacement (original remains blocked)")
    for action in ("setup", "build", "benchmarks", "run"):
        cmd = sub.add_parser(action)
        cmd.add_argument("lab", choices=("lab1", "lab2", "lab3", "lab4", "lab5"))
        if action in ("build", "run"):
            cmd.add_argument("--config", type=config_name)
        if action == "benchmarks":
            cmd.add_argument("--harts", type=int, choices=(1, 2), default=2)
        if action == "run":
            cmd.add_argument("binary")
            cmd.add_argument("--pk")
            cmd.add_argument("--max-cycles", type=positive_int, default=100000000)
            cmd.add_argument("--seconds", type=positive_int, default=900)
            cmd.add_argument("--preload", action="store_true", help="Use verified HEX DRAM preload for bare-metal Lab2/3")
            cmd.add_argument("--arg", action="append", default=[], help="Target argument, repeat as --arg=-g --arg=5")
    args = parser.parse_args()
    if args.action == "doctor":
        return doctor(args.lab, args.lab4_mode)
    if args.action == "plot-caches":
        return subprocess.call([sys.executable, str(SUPPORT / "plot-caches.py"), *args.logs, "--output", args.output])
    if args.action == "setup" and args.lab == "lab4":
        raise RuntimeError("Lab4 setup is blocked: the legacy RVV 0.10 compiler and course timing Spike are missing; see docs/LOCAL_ENVIRONMENT.md.")
    (LOCAL / "locks").mkdir(parents=True, exist_ok=True)
    with (LOCAL / "locks" / (args.lab + ".lock")).open("w") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError(f"Another local command is modifying {args.lab}. Wait for it to finish.")
        config = getattr(args, "config", None) or DEFAULTS.get(args.lab)
        if args.action == "setup":
            if args.lab in ("lab1", "lab3"):
                artifact = "multilib" if args.lab == "lab1" else "pk-spectre"
                execute([sys.executable, str(SUPPORT / "fetch-artifacts.py"), artifact], ROOT,
                        args.lab + "-artifacts")
            if args.lab != "lab1":
                execute([sys.executable, str(SUPPORT / "fetch-submodules.py"), args.lab], ROOT,
                        args.lab + "-setup")
            execute([sys.executable, str(SUPPORT / "restore-links.py")], ROOT, args.lab + "-links")
        elif args.action == "build":
            build(args.lab, config)
        elif args.action == "benchmarks":
            benchmarks(args.lab, args.harts)
        else:
            run(args.lab, config, args.binary, args.max_cycles, args.seconds, args.pk, args.preload, args.arg)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)
