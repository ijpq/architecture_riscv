"""Separate RVV 1.0 teaching environment; not the original Lab 4 model."""
import argparse
import fcntl
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / "scripts/cs152-local"
WORK = ROOT / ".local"
COURSE = ROOT / "edu_cs152/lab4/benchmarks"
LAB = ROOT / "lab4-modern"
GEM5 = WORK / "src/gem5"
GEM5_COMMIT = "c8222cc67a399bfc01e8658dd14b30d5bfd634f9"
GEM5_VERSION = "v25.1.0.1"
SCONS_VERSION = "4.9.1"
SIM = GEM5 / "build/CS152/gem5.opt"
OUTPUT = WORK / "benchmarks/lab4-modern"
KERNELS = ("csaxpy", "cmplxmult", "dgemv", "dgemm", "imax", "spmv", "rsort")
PROGRAMS = (*KERNELS, *("vec-" + name for name in KERNELS), "rvv-runtime")


def model_parameters(vlen=256, vector_latency=4, vector_units=2, memory_latency_ns=50):
    """Reject impossible/unsupported model settings before launching a simulator."""
    values = dict(vlen=vlen, vector_latency=vector_latency, vector_units=vector_units,
                  memory_latency_ns=memory_latency_ns)
    for name, value in values.items():
        if type(value) is not int:
            raise ValueError(f"{name} must be an integer")
    if vlen not in (128, 256, 512, 1024):
        raise ValueError("vlen must be 128, 256, 512 or 1024 bits")
    for name, maximum in (("vector_latency", 64), ("vector_units", 16), ("memory_latency_ns", 1000)):
        if not 1 <= values[name] <= maximum:
            raise ValueError(f"{name} must be in 1..{maximum}")
    return values


def build_commands(jobs):
    if type(jobs) is not int or not 1 <= jobs <= 64:
        raise ValueError("jobs must be an integer in 1..64")
    base = ["/usr/bin/python3", "-m", "SCons", "--ignore-style", "--without-tcmalloc",
            "--linker=gold"]
    return [base + ["defconfig", "build/CS152", str(LAB / "gem5-build-opts")],
            base + ["build/CS152/gem5.opt", f"-j{jobs}"]]


def validate_result(summary, stats_text, log_text):
    """Require full guest verification and the first, ROI-only statistics dump."""
    if (not isinstance(summary, dict)
            or summary.get("passed") is not True or summary.get("exit_code") != 0
            or summary.get("exit_cause") != "exiting with last active thread context"
            or summary.get("roi_count") != 1 or summary.get("roi_ticks", 0) <= 0):
        raise RuntimeError("gem5 did not complete one ROI and a successful guest exit")
    if "CS152_LAB4_CHECK_PASS code=0" not in log_text or "CS152_LAB4_CHECK_FAIL" in log_text:
        raise RuntimeError("guest verification failed or its full result is missing")
    blocks = re.split(r"-+\s*Begin Simulation Statistics\s*-+", stats_text)
    if len(blocks) < 2 or not re.search(r"-+\s*End Simulation Statistics\s*-+", blocks[1]):
        raise RuntimeError("missing complete ROI statistics dump")
    first = re.split(r"-+\s*End Simulation Statistics\s*-+", blocks[1])[0]
    raw = {}
    for line in first.splitlines():
        fields = line.split()
        if len(fields) >= 2 and not fields[0].startswith("#"):
            try:
                raw[fields[0]] = float(fields[1])
            except ValueError:
                continue
    values = {}
    for key, name in (("cycles", "system.cpu.numCycles"), ("instructions", "simInsts")):
        value = raw.get(name, 0)
        if not math.isfinite(value) or value <= 0 or value != int(value):
            raise RuntimeError(f"missing or invalid ROI statistic: {name}")
        values[key] = int(value)
    misses = raw.get("system.cpu.dcache.overallMisses::total")
    if misses is not None and math.isfinite(misses) and misses >= 0:
        values["dcache_misses"] = int(misses)
    return values


def validate_config(config, model):
    """Check actual SimObjects, rather than trusting echoed command-line values."""
    model = model_parameters(**model)
    try:
        system = config["system"]
        cpu = system["cpu"]
        isa = cpu["isa"][0]
        queues = cpu["instQueues"]
        units = [unit for unit in queues[0]["fuPool"]["FUList"]
                 if any(op["opClass"] == "SimdAdd" for op in unit["opList"])]
        correct = (system["mem_mode"] == "timing" and cpu["type"] == "BaseO3CPU"
                   and system["clk_domain"]["clock"] == [1000]
                   and isa["enable_rvv"] is True and isa["vlen"] == model["vlen"]
                   and isa["elen"] == 64
                   and system["memory"]["latency"] == model["memory_latency_ns"] * 1000
                   and len(queues) == 1 and "fuPool" not in cpu
                   and len(units) == 1 and units[0]["count"] == model["vector_units"]
                   and all(op["opLat"] == model["vector_latency"] for op in units[0]["opList"]))
    except (KeyError, TypeError, IndexError) as error:
        raise RuntimeError("missing or invalid gem5 configuration") from error
    if not correct:
        raise RuntimeError("actual gem5 configuration does not match the requested model")


def migrate_assembly(text):
    """Make implicit RVV 0.10 policies explicit; never fill a course TODO."""
    lines = []
    for line in text.splitlines(keepends=True):
        code, marker, comment = line.rstrip("\n").partition("#")
        if re.match(r"^\s*vsetvli\s", code) and len(code.split(",")) == 4:
            code = code.rstrip() + ", tu, mu"
            if marker:
                code += " "
            line = code + marker + comment + ("\n" if line.endswith("\n") else "")
        lines.append(line)
    return "".join(lines)


def prepare_exercises(course=COURSE, destination=LAB / "exercises"):
    copied = []
    for source in sorted(course.glob("vec-*/*.S")):
        target = destination / source.parent.name / source.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            # Exclusive creation is deliberate: repeated setup cannot erase work.
            with target.open("x") as stream:
                stream.write(migrate_assembly(source.read_text()))
            copied.append(target)
    return copied


def benchmark_commands(names=None):
    names = list(PROGRAMS if names is None else names)
    if any(name not in PROGRAMS for name in names):
        raise ValueError("unknown modern Lab 4 benchmark")
    base = ["/usr/bin/riscv64-linux-gnu-gcc", "-O2", "-std=gnu11", "-static",
            "-march=rv64gcv", "-mabi=lp64d", "-ffast-math", "-fno-tree-vectorize",
            "-fno-tree-loop-distribute-patterns", "-Wl,--wrap=main",
            "-I" + str(LAB / "compat"), "-I" + str(COURSE / "common"),
            "-I" + str(GEM5 / "include")]
    common = [str(LAB / "runtime.c"), str(GEM5 / "util/m5/src/abi/riscv/m5op.S")]
    commands = []
    for name in names:
        if name == "rvv-runtime":
            sources = [LAB / "checks/rvv-runtime.c", LAB / "checks/rvv-probe.S"]
            includes = []
        else:
            sources = sorted((COURSE / name).glob("*.c"))
            includes = ["-I" + str(COURSE / name.removeprefix("vec-"))]
            if name.startswith("vec-"):
                sources += [LAB / "exercises" / name / source.name
                            for source in sorted((COURSE / name).glob("*.S"))]
        commands.append(base + includes + [str(source) for source in sources] + common
                        + ["-lm", "-o", str(OUTPUT / (name + ".riscv"))])
    return commands


def compilation_inputs(name):
    command = benchmark_commands([name])[0]
    files = [Path(value) for value in command if value.endswith((".c", ".S"))]
    for directory in (COURSE / "common", COURSE / name, COURSE / name.removeprefix("vec-"),
                      LAB / "compat", LAB / "exercises" / name, GEM5 / "include"):
        files += [path for path in directory.rglob("*")
                  if path.is_file() and path.suffix in (".h", ".inc", ".c", ".S")]
    return sorted(set(files))


def compilation_record(name):
    return OUTPUT / (name + ".build.json")


def record_compilation(name, command, binary):
    from cli import digest
    files = compilation_inputs(name) + [binary]
    record = dict(command=command, files={str(path): digest(path) for path in files})
    compilation_record(name).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")


def verify_compilation(name, binary):
    try:
        record = json.loads(compilation_record(name).read_text())
        if not isinstance(record, dict) or record.get("command") != benchmark_commands([name])[0]:
            raise RuntimeError("build command changed")
        verify_fingerprints(record, compilation_inputs(name) + [binary])
    except (OSError, ValueError, RuntimeError) as error:
        raise RuntimeError(f"recompile {name}: run lab4-modern benchmarks {name}") from error


def isolated_command(command, build=False):
    prefix = ["/usr/bin/env", "-u", "PYTHONHOME", "-u", "PYTHONPATH", "-u", "LD_LIBRARY_PATH",
              "PATH=/usr/bin:/bin", "PYTHONNOUSERSITE=1"]
    if build:
        prefix += ["PYTHONPATH=" + str(WORK / "tools/gem5-python"),
                   "PYTHON_CONFIG=/usr/bin/python3.10-config"]
    return prefix + [str(value) for value in command]


def setup():
    from cli import execute
    if not Path("/usr/bin/riscv64-linux-gnu-gcc").is_file():
        raise RuntimeError("install gcc-riscv64-linux-gnu and libc6-dev-riscv64-cross first")
    if not Path("/usr/bin/python3.10-config").is_file():
        raise RuntimeError("gem5 build requires the system Python 3.10 development headers")
    if not GEM5.exists():
        GEM5.parent.mkdir(parents=True, exist_ok=True)
        execute(["git", "clone", "--depth", "1", "--branch", GEM5_VERSION,
                 "https://github.com:443/gem5/gem5.git", str(GEM5)], ROOT,
                "lab4-modern-fetch-gem5")
    actual = subprocess.check_output(["git", "-C", str(GEM5), "rev-parse", "HEAD"], text=True).strip()
    if actual != GEM5_COMMIT:
        raise RuntimeError(f"gem5 checkout mismatch: expected {GEM5_COMMIT}, got {actual}")
    for command in (["git", "-C", str(GEM5), "diff", "--quiet"],
                    ["git", "-C", str(GEM5), "diff", "--cached", "--quiet"]):
        if subprocess.run(command, check=False).returncode != 0:
            raise RuntimeError("gem5 contains tracked source changes; refusing to overwrite them")
    execute(isolated_command(["/usr/bin/python3", "-m", "pip", "install", "--no-deps",
                              "--require-hashes", "--target", str(WORK / "tools/gem5-python"),
                              "-r", str(LAB / "requirements-build.txt")]),
            ROOT, "lab4-modern-setup-scons")
    prepare_exercises()
    print("Modern RVV workspace prepared; original Lab 4 is unchanged.")


def build(jobs=8):
    from cli import execute
    setup()
    for command in build_commands(jobs):
        execute(isolated_command(command, build=True), GEM5, "lab4-modern-gem5-build")


def benchmarks(names=None):
    from cli import execute
    prepare_exercises()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for command in benchmark_commands(names):
        binary = Path(command[-1])
        name = binary.stem
        compilation_record(name).unlink(missing_ok=True)
        execute(command, ROOT, f"lab4-modern-{name}-build")
        record_compilation(name, command, binary)
    print("Built scalar kernels, the course vector example and unfinished vector exercises in", OUTPUT)


def model_key(model):
    model = model_parameters(**model)
    return (f"v{model['vlen']}-lat{model['vector_latency']}-u{model['vector_units']}"
            f"-mem{model['memory_latency_ns']}")


def run_command(binary, output, model, max_cycles, arguments):
    model = model_parameters(**model)
    if type(max_cycles) is not int or max_cycles <= 0:
        raise ValueError("max_cycles must be a positive integer")
    return isolated_command([str(SIM), "--outdir=" + str(output), str(LAB / "gem5_config.py"),
                             "--binary=" + str(binary), "--vlen=" + str(model["vlen"]),
                             "--vector-latency=" + str(model["vector_latency"]),
                             "--vector-units=" + str(model["vector_units"]),
                             "--memory-latency-ns=" + str(model["memory_latency_ns"]),
                             "--max-cycles=" + str(max_cycles),
                             *("--arg=" + str(value) for value in arguments)])


def evidence_path(name, model):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", name):
        raise ValueError("unsafe benchmark name")
    return WORK / "evidence" / f"lab4-modern-{name}-{model_key(model)}.json"


def input_files(name):
    files = [SIM, LAB / "gem5_config.py", LAB / "runtime.c", LAB / "compat/encoding.h",
             LAB / "gem5-build-opts", Path(__file__).resolve()]
    if name in PROGRAMS:
        command = benchmark_commands([name])[0]
        files += [Path(value) for value in command if value.endswith((".c", ".S"))]
        files += [COURSE / "common/util.h", compilation_record(name)]
        for directory in (COURSE / name, COURSE / name.removeprefix("vec-")):
            files += list(directory.glob("*.h"))
    return sorted(set(files))


def run(binary_or_name, model=None, max_cycles=100_000_000, seconds=900, arguments=()):
    from cli import digest, elf_segments, execute
    model = model_parameters() if model is None else model_parameters(**model)
    if type(seconds) is not int or seconds <= 0:
        raise ValueError("seconds must be a positive integer")
    value = str(binary_or_name)
    binary = (OUTPUT / (value + ".riscv") if value in PROGRAMS else Path(value)).resolve()
    name = binary.stem
    evidence = evidence_path(name, model)
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.unlink(missing_ok=True)  # A failed rerun must revoke any previous PASS.
    if not SIM.is_file():
        raise RuntimeError("gem5 is not built; run lab4-modern build first")
    elf_segments(binary)
    if name in PROGRAMS:
        verify_compilation(name, binary)
    output = WORK / "runs/lab4-modern" / name / model_key(model)
    output.mkdir(parents=True, exist_ok=True)
    for stale in ("summary.json", "stats.txt"):
        (output / stale).unlink(missing_ok=True)
    arguments = list(arguments)
    if name == "rvv-runtime" and not arguments:
        arguments = [str(model["vlen"])]
    command = run_command(binary, output, model, max_cycles, arguments)
    label = f"lab4-modern-{name}-{model_key(model)}-run"
    execute(command, ROOT, label, timeout=seconds)
    log = WORK / "logs" / (label + ".log")
    summary_path, stats_path = output / "summary.json", output / "stats.txt"
    summary = json.loads(summary_path.read_text())
    stats = validate_result(summary, stats_path.read_text(), log.read_text(errors="replace"))
    validate_config(json.loads((output / "config.json").read_text()), model)
    if summary.get("model") != model:
        raise RuntimeError("gem5 result does not match requested model parameters")
    if name == "rvv-runtime" and not re.search(
            rf"CS152_RVV_RUNTIME_PASS vlen={model['vlen']}\b", log.read_text(errors="replace")):
        raise RuntimeError("RVV self-check did not verify the requested VLEN")
    files = input_files(name) + [binary, summary_path, stats_path, log,
                                output / "config.json", output / "config.ini"]
    record = dict(program=name, model=model, stats=stats, gem5_commit=GEM5_COMMIT,
                  files={str(path): digest(path) for path in files}, command=command)
    temporary = evidence.with_suffix(".tmp")
    temporary.write_text(json.dumps(record, indent=2) + "\n")
    temporary.replace(evidence)
    print("PASS", name, model_key(model), stats, "evidence:", evidence)
    return record


def verify_fingerprints(record, required):
    from cli import digest
    if not isinstance(record, dict):
        raise RuntimeError("invalid evidence document")
    files = record.get("files", {})
    if not isinstance(files, dict) or not files or not {str(path) for path in required}.issubset(files):
        raise RuntimeError("incomplete evidence fingerprints")
    for filename, expected in files.items():
        path = Path(filename)
        if not path.is_file() or digest(path) != expected:
            raise RuntimeError(f"stale or missing evidence input: {filename}")


def required_runs():
    return ([(name, model_parameters()) for name in (*KERNELS, "vec-csaxpy")]
            + [("rvv-runtime", model_parameters(vlen=128, vector_latency=1)),
               ("rvv-runtime", model_parameters(vlen=512, vector_latency=1)),
               ("rvv-runtime", model_parameters(vlen=128, vector_latency=8))])


def read_evidence(name, model):
    record = json.loads(evidence_path(name, model).read_text())
    if (not isinstance(record, dict)
            or record.get("program") != name or record.get("model") != model
            or record.get("gem5_commit") != GEM5_COMMIT):
        raise RuntimeError("evidence identity does not match this benchmark/model")
    verify_compilation(name, OUTPUT / (name + ".riscv"))
    output = WORK / "runs/lab4-modern" / name / model_key(model)
    log = WORK / "logs" / f"lab4-modern-{name}-{model_key(model)}-run.log"
    summary_path, stats_path = output / "summary.json", output / "stats.txt"
    verify_fingerprints(record, input_files(name) + [OUTPUT / (name + ".riscv"),
                         summary_path, stats_path, log, output / "config.json", output / "config.ini"])
    summary = json.loads(summary_path.read_text())
    stats = validate_result(summary, stats_path.read_text(), log.read_text(errors="replace"))
    validate_config(json.loads((output / "config.json").read_text()), model)
    if summary.get("model") != model or stats != record.get("stats"):
        raise RuntimeError("evidence statistics/model do not match the saved result")
    return record


def doctor():
    results = {}
    cases = required_runs()
    for name, model in cases:
        key = (name, model_key(model))
        try:
            record = read_evidence(name, model)
            results[key] = record
            print("  PASS", name, key[1], record["stats"])
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
            print("  MISSING/STALE", name, key[1], str(error))
    passed = len(results) == len(cases)
    if passed:
        low = results[("rvv-runtime", model_key(model_parameters(vlen=128, vector_latency=1)))]["stats"]["cycles"]
        high = results[("rvv-runtime", model_key(model_parameters(vlen=128, vector_latency=8)))]["stats"]["cycles"]
        passed = high > low
        print("  VECTOR-LATENCY EFFECT:", low, "->", high, "cycles", "PASS" if passed else "FAIL")
    print("READY lab4-modern" if passed else "NOT READY lab4-modern",
          f"({len(results)}/{len(cases)} checks)", "[RVV 1.0 replacement, NOT original Lab 4]")
    return 0 if passed else 1


def verify(seconds=900):
    for name, model in required_runs():
        run(name, model=model, seconds=seconds)
    return doctor()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("setup", help="pin gem5/SCons and create non-overwriting exercise copies")
    builder = sub.add_parser("build", help="build the real gem5 simulator from source")
    builder.add_argument("--jobs", type=int, default=8)
    bench = sub.add_parser("benchmarks", help="compile course kernels without filling vector TODOs")
    bench.add_argument("names", nargs="*", help="optional names (default: all 15 programs)")
    runner = sub.add_parser("run", help="run one kernel with real simulated ROI statistics")
    runner.add_argument("binary", help="benchmark name or a RISC-V Linux ELF path")
    runner.add_argument("--vlen", type=int, default=256)
    runner.add_argument("--vector-latency", type=int, default=4)
    runner.add_argument("--vector-units", type=int, default=2)
    runner.add_argument("--memory-latency-ns", type=int, default=50)
    runner.add_argument("--max-cycles", type=int, default=100_000_000)
    runner.add_argument("--seconds", type=int, default=900)
    runner.add_argument("--arg", action="append", default=[])
    checker = sub.add_parser("verify", help="run scalar/example checks and VLEN/latency self-checks")
    checker.add_argument("--seconds", type=int, default=900)
    sub.add_parser("doctor", help="recheck saved results and every SHA-256 fingerprint")
    args = parser.parse_args(argv)
    try:
        if args.action == "doctor":
            return doctor()
        locks = WORK / "locks"
        locks.mkdir(parents=True, exist_ok=True)
        with (locks / "lab4-modern.lock").open("a") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise RuntimeError("another modern Lab 4 build/run is active") from error
            if args.action == "setup":
                setup()
            elif args.action == "build":
                build(args.jobs)
            elif args.action == "benchmarks":
                benchmarks(args.names or None)
            elif args.action == "verify":
                return verify(args.seconds)
            elif args.action == "run":
                model = model_parameters(args.vlen, args.vector_latency, args.vector_units,
                                         args.memory_latency_ns)
                run(args.binary, model, args.max_cycles, args.seconds, args.arg)
        return 0
    except (OSError, ValueError, RuntimeError) as error:
        print("ERROR:", error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
