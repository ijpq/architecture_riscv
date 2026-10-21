"""Fast host-side tests; real gem5 checks are run separately."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import lab4_modern as modern


class ModelTests(unittest.TestCase):
    def test_model_parameters_are_explicit_and_do_not_alias_dlen(self):
        self.assertEqual(modern.model_parameters(), {
            "vlen": 256, "vector_latency": 4, "vector_units": 2,
            "memory_latency_ns": 50,
        })
        self.assertEqual(modern.model_parameters(vlen=512)["vlen"], 512)

    def test_rejects_unsupported_or_non_integer_vlen(self):
        for value in (0, 64, 129, 384, 2048, True, "256"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                modern.model_parameters(vlen=value)

    def test_rejects_nonpositive_or_excessive_timing_parameters(self):
        for name, values in {
            "vector_latency": (0, -1, 65, 1.5),
            "vector_units": (0, 17, True),
            "memory_latency_ns": (0, 1001, "50"),
        }.items():
            for value in values:
                with self.subTest(name=name, value=value), self.assertRaises(ValueError):
                    modern.model_parameters(**{name: value})


class BuildTests(unittest.TestCase):
    def test_build_uses_isolated_scons_and_a_minimal_named_configuration(self):
        commands = modern.build_commands(4)
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0][:3], ["/usr/bin/python3", "-m", "SCons"])
        self.assertIn("defconfig", commands[0])
        self.assertIn("build/CS152", commands[0])
        self.assertIn(str(modern.LAB / "gem5-build-opts"), commands[0])
        self.assertIn("build/CS152/gem5.opt", commands[1])
        self.assertIn("-j4", commands[1])
        self.assertIn("--ignore-style", commands[1])

    def test_build_rejects_unsafe_job_counts(self):
        for jobs in (0, -1, 65, True, "8"):
            with self.subTest(jobs=jobs), self.assertRaises(ValueError):
                modern.build_commands(jobs)


class ResultTests(unittest.TestCase):
    STATS = """---------- Begin Simulation Statistics ----------
simInsts 100 # instruction count
system.cpu.numCycles 200 # simulated cycles
system.cpu.dcache.overallMisses::total 3
---------- End Simulation Statistics ----------
---------- Begin Simulation Statistics ----------
simInsts 999
system.cpu.numCycles 9999
---------- End Simulation Statistics ----------
"""
    SUMMARY = {"passed": True, "exit_code": 0,
               "exit_cause": "exiting with last active thread context",
               "roi_count": 1, "roi_ticks": 200000}
    LOG = "CS152_LAB4_CHECK_PASS code=0\n"

    def test_uses_the_roi_dump_not_post_verification_statistics(self):
        stats = modern.validate_result(self.SUMMARY, self.STATS, self.LOG)
        self.assertEqual(stats["cycles"], 200)
        self.assertEqual(stats["instructions"], 100)
        self.assertEqual(stats["dcache_misses"], 3)

    def test_rejects_missing_or_failed_guest_verification(self):
        for log in ("", "CS152_LAB4_CHECK_FAIL code=256", self.LOG + "CS152_LAB4_CHECK_FAIL"):
            with self.subTest(log=log), self.assertRaises(RuntimeError):
                modern.validate_result(self.SUMMARY, self.STATS, log)

    def test_rejects_timeout_nonzero_exit_missing_or_incomplete_roi(self):
        for changes in ({"passed": False}, {"exit_code": 1}, {"roi_count": 0},
                        {"roi_ticks": 0}, {"exit_cause": "simulate() limit reached"}):
            with self.subTest(changes=changes), self.assertRaises(RuntimeError):
                modern.validate_result(dict(self.SUMMARY, **changes), self.STATS, self.LOG)

    def test_rejects_missing_nonfinite_or_zero_required_statistics(self):
        for stats in ("", self.STATS.replace("numCycles 200", "numCycles 0"),
                      self.STATS.replace("simInsts 100", "simInsts nan")):
            with self.subTest(stats=stats), self.assertRaises(RuntimeError):
                modern.validate_result(self.SUMMARY, stats, self.LOG)


class ConfigurationTests(unittest.TestCase):
    CONFIG = {"system": {
        "mem_mode": "timing", "clk_domain": {"clock": [1000]},
        "memory": {"latency": 50000},
        "cpu": {"type": "BaseO3CPU", "isa": [{"enable_rvv": True, "vlen": 256, "elen": 64}],
                "instQueues": [{"fuPool": {"FUList": [{"count": 2, "opList": [
                    {"opClass": "SimdAdd", "opLat": 4},
                    {"opClass": "SimdMult", "opLat": 4}]}]}}]}}}

    def test_validates_actual_isa_clock_memory_and_functional_unit_configuration(self):
        modern.validate_config(self.CONFIG, modern.model_parameters())
        changes = (("vlen", 512), ("vector_latency", 8), ("vector_units", 1),
                   ("memory_latency_ns", 80))
        for name, value in changes:
            with self.subTest(name=name), self.assertRaises(RuntimeError):
                modern.validate_config(self.CONFIG, modern.model_parameters(**{name: value}))

    def test_disabled_vectors_atomic_mode_or_wrong_clock_cannot_pass(self):
        for change in ("rvv", "mode", "clock", "missing_fu"):
            config = copy.deepcopy(self.CONFIG)
            if change == "rvv":
                config["system"]["cpu"]["isa"][0]["enable_rvv"] = False
            elif change == "mode":
                config["system"]["mem_mode"] = "atomic"
            elif change == "clock":
                config["system"]["clk_domain"]["clock"] = [500]
            else:
                config["system"]["cpu"]["instQueues"][0]["fuPool"]["FUList"] = []
            with self.subTest(change=change), self.assertRaises(RuntimeError):
                modern.validate_config(config, modern.model_parameters())

    def test_unused_cpu_pool_cannot_hide_the_active_queue_configuration(self):
        config = copy.deepcopy(self.CONFIG)
        cpu = config["system"]["cpu"]
        cpu["fuPool"] = copy.deepcopy(cpu["instQueues"][0]["fuPool"])
        active_unit = cpu["instQueues"][0]["fuPool"]["FUList"][0]
        active_unit["count"] = 4
        for op in active_unit["opList"]:
            op["opLat"] = 1
        with self.assertRaises(RuntimeError):
            modern.validate_config(config, modern.model_parameters())


class ExerciseTests(unittest.TestCase):
    def test_migration_only_adds_explicit_undisturbed_policies(self):
        source = "vsetvli t0, a0, e32, m4 # mode\n# TODO: implement kernel\nret\n"
        migrated = modern.migrate_assembly(source)
        self.assertIn("vsetvli t0, a0, e32, m4, tu, mu # mode", migrated)
        self.assertIn("# TODO: implement kernel\nret\n", migrated)
        explicit = "vsetvli t0, a0, e32, m1, ta, ma\n"
        self.assertEqual(modern.migrate_assembly(explicit), explicit)

    def test_preparation_preserves_existing_exercise_edits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            course = root / "course/vec-demo"
            course.mkdir(parents=True)
            source = course / "kernel.S"
            source.write_text("vsetvli t0, a0, e32, m4\n# TODO\nret\n")
            destination = root / "exercises"
            modern.prepare_exercises(course.parent, destination)
            copied = destination / "vec-demo/kernel.S"
            self.assertIn("tu, mu", copied.read_text())
            copied.write_text("# Student work must survive setup\n")
            modern.prepare_exercises(course.parent, destination)
            self.assertEqual(copied.read_text(), "# Student work must survive setup\n")
            self.assertNotIn("tu, mu", source.read_text())

    def test_benchmark_commands_keep_course_runtime_out_and_keep_scalar_scalar(self):
        commands = modern.benchmark_commands(["csaxpy", "vec-cmplxmult", "rvv-runtime"])
        self.assertEqual(len(commands), 3)
        for command in commands:
            self.assertEqual(command[0], "/usr/bin/riscv64-linux-gnu-gcc")
            self.assertIn("-static", command)
            self.assertIn("-fno-tree-vectorize", command)
            self.assertIn("-Wl,--wrap=main", command)
            self.assertFalse(any(value.endswith(("syscalls.c", "crt.S")) for value in command))
        self.assertIn(str(modern.COURSE / "csaxpy/csaxpy.c"), commands[0])
        self.assertIn(str(modern.LAB / "exercises/vec-cmplxmult/vec_cmplxmult.S"), commands[1])
        self.assertIn(str(modern.LAB / "checks/rvv-probe.S"), commands[2])
        with self.assertRaises(ValueError):
            modern.benchmark_commands(["../not-a-benchmark"])


class RunCommandTests(unittest.TestCase):
    def test_passes_model_and_guest_arguments_without_shell_interpretation(self):
        command = modern.run_command(Path("/tmp/input.riscv"), Path("/tmp/output"),
                                     modern.model_parameters(vlen=512), 1234, ["-g", "5"])
        self.assertIn(str(modern.SIM), command)
        self.assertIn("--outdir=/tmp/output", command)
        self.assertIn(str(modern.LAB / "gem5_config.py"), command)
        self.assertIn("--vlen=512", command)
        self.assertIn("--vector-latency=4", command)
        self.assertIn("--vector-units=2", command)
        self.assertIn("--memory-latency-ns=50", command)
        self.assertIn("--max-cycles=1234", command)
        self.assertEqual(command[-2:], ["--arg=-g", "--arg=5"])
        self.assertFalse(any("dlen" in value for value in command))
        with self.assertRaises(ValueError):
            modern.run_command(Path("/tmp/x"), Path("/tmp/o"), modern.model_parameters(), 0, [])

    def test_model_identity_is_stable_and_contains_all_timing_parameters(self):
        baseline = modern.model_parameters()
        key = modern.model_key(baseline)
        self.assertEqual(key, "v256-lat4-u2-mem50")
        for changes in ({"vlen": 512}, {"vector_latency": 8}, {"vector_units": 1},
                        {"memory_latency_ns": 80}):
            self.assertNotEqual(key, modern.model_key(dict(baseline, **changes)))


class CompilationTests(unittest.TestCase):
    def test_edited_sources_or_build_command_require_recompilation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, binary = root / "source.S", root / "csaxpy.riscv"
            source.write_text("old assembly")
            binary.write_bytes(b"built program")
            with mock.patch.object(modern, "OUTPUT", root), \
                    mock.patch.object(modern, "compilation_inputs", return_value=[source]), \
                    mock.patch.object(modern, "benchmark_commands", return_value=[["gcc", "-O2"]]):
                modern.record_compilation("csaxpy", ["gcc", "-O2"], binary)
                modern.verify_compilation("csaxpy", binary)
                source.write_text("student edited assembly")
                with self.assertRaisesRegex(RuntimeError, "recompile"):
                    modern.verify_compilation("csaxpy", binary)
                modern.record_compilation("csaxpy", ["gcc", "-O2"], binary)
                with mock.patch.object(modern, "benchmark_commands", return_value=[["gcc", "-O3"]]):
                    with self.assertRaisesRegex(RuntimeError, "recompile"):
                        modern.verify_compilation("csaxpy", binary)

    def test_missing_build_record_does_not_attest_an_old_executable(self):
        with tempfile.TemporaryDirectory() as directory, mock.patch.object(modern, "OUTPUT", Path(directory)):
            with self.assertRaisesRegex(RuntimeError, "recompile"):
                modern.verify_compilation("csaxpy", Path(directory) / "csaxpy.riscv")


class EvidenceTests(unittest.TestCase):
    def test_empty_missing_or_changed_fingerprints_cannot_pass(self):
        from cli import digest
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input"
            source.write_text("original")
            record = {"files": {str(source): digest(source)}}
            modern.verify_fingerprints(record, [source])
            with self.assertRaises(RuntimeError):
                modern.verify_fingerprints({"files": {}}, [source])
            with self.assertRaises(RuntimeError):
                modern.verify_fingerprints(record, [source, Path(directory) / "missing"])
            source.write_text("changed")
            with self.assertRaises(RuntimeError):
                modern.verify_fingerprints(record, [source])

    def test_malformed_evidence_is_a_clear_failure_not_an_attribute_error(self):
        for record in ([], {"files": []}, {"files": "not a mapping"}):
            with self.subTest(record=record), self.assertRaises(RuntimeError):
                modern.verify_fingerprints(record, [])

    def test_required_runs_cover_course_checks_widths_and_latency(self):
        cases = modern.required_runs()
        names = [name for name, model in cases]
        self.assertTrue(set(modern.KERNELS).issubset(names))
        self.assertIn("vec-csaxpy", names)  # An example provided by the course, not a new answer.
        smoke = [model for name, model in cases if name == "rvv-runtime"]
        self.assertTrue({128, 512}.issubset({model["vlen"] for model in smoke}))
        self.assertEqual({model["vector_latency"] for model in smoke if model["vlen"] == 128}, {1, 8})
        self.assertNotIn("vec-cmplxmult", names)  # An uncompleted exercise must not be a PASS requirement.

    def test_benchmarks_with_no_names_means_all_programs(self):
        with tempfile.TemporaryDirectory() as directory, \
                mock.patch.object(modern, "WORK", Path(directory)), \
                mock.patch.object(modern, "benchmarks") as build_all:
            self.assertEqual(modern.main(["benchmarks"]), 0)
            build_all.assert_called_once_with(None)

    def test_independent_modern_help_does_not_need_a_built_simulator(self):
        with self.assertRaises(SystemExit) as result, mock.patch("sys.stdout"):
            modern.main(["--help"])
        self.assertEqual(result.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
