"""Headless tests for recovery tooling; no downloads or RTL builds."""
import argparse
import hashlib
import importlib.util
import io
from contextlib import redirect_stdout
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("cs152_cli", Path(__file__).with_name("cli.py"))
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)


def elf_image(bits=64, data=b"abcd", memory_size=24):
    """Minimal real ELF load segment, with no compiler or network dependency."""
    ident = b"\x7fELF" + bytes([2 if bits == 64 else 1, 1, 1]) + bytes(9)
    header_format = "<16sHHIQQQIHHHHHH" if bits == 64 else "<16sHHIIIIIHHHHHH"
    ph_format = "<IIQQQQQQ" if bits == 64 else "<IIIIIIII"
    header_size, ph_size = struct.calcsize(header_format), struct.calcsize(ph_format)
    offset, base = header_size + ph_size, 0x80000000
    header = struct.pack(header_format, ident, 2, 243, 1, base, header_size, 0, 0,
                         header_size, ph_size, 1, 0, 0, 0)
    ph = ((1, 7, offset, base, base, len(data), memory_size, 8) if bits == 64 else
          (1, offset, base, base, len(data), memory_size, 7, 8))
    return header + struct.pack(ph_format, *ph) + data


class CliTests(unittest.TestCase):
    def test_config_accepts_scala_name_but_not_shell_or_path(self):
        self.assertEqual(cli.config_name("CS152RocketL2Config"), "CS152RocketL2Config")
        for value in ("../../other", "X; touch /tmp/no", "", "two configs", "A/B"):
            with self.assertRaises(argparse.ArgumentTypeError):
                cli.config_name(value)

    def test_cycle_and_wall_clock_limits_must_be_positive(self):
        self.assertEqual(cli.positive_int("123"), 123)
        for value in ("0", "-1", "not-a-number"):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                cli.positive_int(value)

    def test_binary_hash_matches_sha256(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data"
            path.write_bytes(b"binary\x00content")
            self.assertEqual(cli.digest(path), hashlib.sha256(path.read_bytes()).hexdigest())

    def test_nonzero_exit_is_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            with self.assertRaisesRegex(RuntimeError, "exit 7"):
                cli.execute([sys.executable, "-c", "raise SystemExit(7)"], Path(tmp), "bad")

    def test_timeout_is_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            with self.assertRaisesRegex(RuntimeError, "exit 124"):
                cli.execute([sys.executable, "-c", "import time; time.sleep(5)"], Path(tmp), "slow", timeout=0.1)

    def test_success_logs_output(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            logfile = cli.execute([sys.executable, "-c", "print('selfcheck passed')"], Path(tmp), "good")
            self.assertIn("selfcheck passed", logfile.read_text())

    def test_unvalidated_lab4_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "RVV 0.10"):
            cli.build("lab4", None)
        with self.assertRaisesRegex(RuntimeError, "fake cycle counts"):
            cli.run("lab4", None, "unused", 100, 1)

    def test_lab4_setup_explains_blocker_without_running_downloads(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)), \
                patch.object(sys, "argv", ["cs152", "setup", "lab4"]), \
                patch.object(cli, "execute") as execute:
            with self.assertRaisesRegex(RuntimeError, "RVV 0.10"):
                cli.main()
            execute.assert_not_called()

    def test_doctor_reports_nonzero_for_incomplete_environment(self):
        with patch.object(cli.shutil, "which", return_value="/bin/tool"), \
                patch.object(cli, "valid_run_evidence", return_value=(False, "missing")), \
                redirect_stdout(io.StringIO()):
            self.assertNotEqual(cli.doctor("lab2"), 0)

    def test_doctor_can_pass_a_ready_lab_but_not_all_with_lab4_missing(self):
        with patch.object(cli.shutil, "which", return_value="/bin/tool"), \
                patch.object(cli, "valid_run_evidence", return_value=(True, "verified")), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(cli.doctor("lab2"), 0)
            self.assertEqual(cli.doctor("lab3"), 0)
            self.assertEqual(cli.doctor("lab5"), 0)
            self.assertNotEqual(cli.doctor("all"), 0)
            self.assertNotEqual(cli.doctor("lab4"), 0)

    def test_modern_lab4_dispatch_is_explicit_and_preserves_arguments(self):
        import lab4_modern
        with patch.object(sys, "argv", ["cs152", "lab4-modern", "run", "csaxpy", "--vlen", "512"]), \
                patch.object(lab4_modern, "main", return_value=7) as modern:
            self.assertEqual(cli.main(), 7)
            modern.assert_called_once_with(["run", "csaxpy", "--vlen", "512"])

    def test_doctor_accepts_modern_lab4_only_when_explicitly_selected(self):
        import lab4_modern
        with patch.object(cli.shutil, "which", return_value="/bin/tool"), \
                patch.object(cli, "valid_run_evidence", return_value=(True, "verified")), \
                patch.object(lab4_modern, "doctor", return_value=0) as modern, \
                redirect_stdout(io.StringIO()):
            self.assertNotEqual(cli.doctor("lab4"), 0)
            modern.assert_not_called()
            self.assertEqual(cli.doctor("lab4", lab4_mode="modern"), 0)
            modern.assert_called_once_with()
            modern.return_value = 1
            self.assertNotEqual(cli.doctor("lab4", lab4_mode="modern"), 0)

    def test_elf32_and_elf64_load_segments_include_bss_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "program"
            for bits in (32, 64):
                with self.subTest(bits=bits):
                    binary.write_bytes(elf_image(bits))
                    self.assertEqual(cli.elf_segments(binary), [(0x80000000, 0x80000000, b"abcd", 24)])

    def test_malformed_elf_is_a_clear_error(self):
        image = elf_image()
        wrong_machine = bytearray(image)
        struct.pack_into("<H", wrong_machine, 18, 62)
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "bad"
            for data in (b"not ELF", image[:16], image[:70], image[:-1], bytes(wrong_machine)):
                with self.subTest(length=len(data)):
                    binary.write_bytes(data)
                    with self.assertRaises(RuntimeError):
                        cli.elf_segments(binary)

    def test_preload_uses_decimal_base_and_atomic_cached_hex(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            binary = Path(tmp) / "program"
            binary.write_bytes(elf_image())
            calls = []
            def converter(command, stdout, check):
                calls.append(command)
                stdout.write("0000000064636261\n")
            with patch.object(cli.subprocess, "run", side_effect=converter):
                first = cli.preload_options(binary)
                self.assertEqual(first, cli.preload_options(binary))
            self.assertEqual(calls, [["elf2hex", "8", "4", str(binary), "2147483648"]])
            self.assertIn("+loadmem_addr=80000000", first)
            self.assertEqual(len(list((Path(tmp) / "loadmem").glob("*.hex"))), 1)
            self.assertEqual(list((Path(tmp) / "loadmem").glob("*.tmp")), [])

    def test_preload_refuses_empty_converter_output(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            binary = Path(tmp) / "program"
            binary.write_bytes(elf_image())
            with patch.object(cli.subprocess, "run"), self.assertRaisesRegex(RuntimeError, "no data"):
                cli.preload_options(binary)
            self.assertEqual(list((Path(tmp) / "loadmem").iterdir()), [])

    def test_lab5_command_uses_only_supported_old_driver_flags(self):
        command = cli.simulation_command("lab5", "Lab5RocketConfig", Path("/program"), 123)
        self.assertIn("+dramsim", command)
        self.assertIn("+max-cycles=123", command)
        self.assertEqual(command[-1], "/program")
        self.assertFalse(any("permissive" in arg or "dramsim_ini_dir" in arg for arg in command))

    def test_lab2_command_forwards_target_arguments_after_binary(self):
        command = cli.simulation_command("lab2", "CS152RocketConfig", Path("/bfs"), 456,
                                         arguments=("-g", "5", "-v"))
        self.assertEqual(command[-5:], ["+permissive-off", "/bfs", "-g", "5", "-v"])

    def test_declared_harts_reads_elf_constant_and_handles_no_symbol(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "program"
            binary.write_bytes(elf_image(data=struct.pack("<I", 2)))
            with patch.object(cli.subprocess, "check_output", return_value="80000000 R nharts\n"):
                self.assertEqual(cli.declared_harts(binary), 2)
            with patch.object(cli.subprocess, "check_output", return_value="80000000 T main\n"):
                self.assertIsNone(cli.declared_harts(binary))

    def test_lab5_rejects_wrong_hart_count_before_simulation(self):
        with tempfile.TemporaryDirectory() as tmp:
            binary = Path(tmp) / "program"
            binary.write_bytes(elf_image())
            with patch.object(cli, "simulator", return_value=binary), \
                    patch.object(cli, "declared_harts", return_value=1), \
                    patch.object(cli, "execute") as execute:
                with self.assertRaisesRegex(RuntimeError, "ELF NHARTS=1"):
                    cli.run("lab5", "Lab5MESIDualRocketConfig", binary, 100, 1)
                execute.assert_not_called()

    def test_failure_text_even_with_exit_zero_invalidates_old_evidence(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            binary, logfile = Path(tmp) / "program", Path(tmp) / "run.log"
            binary.write_bytes(elf_image())
            logfile.write_text("*** FAILED *** (tohost = 2)\n")
            evidence = Path(tmp) / "evidence/lab1-Config-program-run.json"
            evidence.parent.mkdir()
            evidence.write_text('{"passed": true}')
            with patch.object(cli, "simulator", return_value=binary), \
                    patch.object(cli, "execute", return_value=logfile):
                with self.assertRaises(RuntimeError):
                    cli.run("lab1", "Config", binary, 100, 1)
            self.assertFalse(evidence.exists())

    def test_runtime_evidence_detects_modified_binary_log_and_proxy_kernel(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            binary, sim, logfile, pk = (Path(tmp) / name for name in ("pk-victim", "sim", "run.log", "pk"))
            binary.write_bytes(elf_image())
            sim.write_bytes(b"simulator")
            pk.write_bytes(b"kernel")
            logfile.write_text("CS152_PK_VICTIM_PASS\n")
            with patch.object(cli, "simulator", return_value=sim), \
                    patch.object(cli, "execute", return_value=logfile):
                cli.run("lab3", "Config", binary, 100, 1, pk=pk)
                self.assertTrue(cli.valid_run_evidence("lab3", "Config", "pk-victim", "PASS")[0])
                self.assertFalse(cli.valid_run_evidence("lab3", "Config", "pk-victim", "MISSING")[0])
                for file in (binary, sim, logfile, pk):
                    original = file.read_bytes()
                    file.write_bytes(original + b"changed")
                    self.assertFalse(cli.valid_run_evidence("lab3", "Config", "pk-victim", "PASS")[0])
                    file.write_bytes(original)

    def test_missing_evidence_is_not_ready(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(cli, "LOCAL", Path(tmp)):
            self.assertFalse(cli.valid_run_evidence("lab3", "Config", "absent", "PASS")[0])


if __name__ == "__main__":
    unittest.main()
