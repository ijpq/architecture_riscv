"""Run the bundled Sodor trace analyzer without restoring or building RTL."""
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest


class TracerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temporary = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temporary.cleanup)
        cls.scripts = Path(temporary.name)
        with tarfile.open(Path(__file__).with_name("sources") / "lab1.tar.gz") as archive:
            for name in ("tracer.py", "instructions.py"):
                member = "payload/generators/riscv-sodor/scripts/" + name
                with archive.extractfile(member) as source:
                    (cls.scripts / name).write_bytes(source.read())

    def analyze(self, rows, ucode):
        lines = ["UART: ignoring non-trace output\n"]
        for cycle, retire, pc, inst, dasm in rows:
            if ucode:
                flags = "F  " if retire else " M "
                line = (
                    f"Cyc= {cycle:10d} [{retire}] PCReg=[{pc:08x}] "
                    "uPC=[0] Bus=[00000000] RegSel=[0] RegAddr=[ 0] "
                    "A=[00000000] B=[00000000] MA=[00000000] "
                    f"InstReg=[{inst:08x}] {flags} {dasm}\n"
                )
            else:
                line = (
                    f"Cyc= {cycle:10d} [{retire}] pc=[{pc:08x}] "
                    "W[r 0=00000000][0] Op1=[r 0][00000000] "
                    f"Op2=[r 0][00000000] inst=[{inst:08x}]     {dasm}\n"
                )
            lines.append(line)
        return subprocess.run(
            [sys.executable, str(self.scripts / "tracer.py"), *(["--ucode"] if ucode else [])],
            input="".join(lines), text=True, capture_output=True, timeout=10,
        )

    def assert_workload_statistics(self, ucode):
        result = self.analyze([
            (2, 1, 0x1000, 0x00000013, "nop"),
            (10, 0, 0x80000000, 0x00000013, "nop"),
            (11, 1, 0x1004, 0x00000013, "nop"),
            (20, 1, 0x80000000, 0x00000013, "nop"),
            (21, 0, 0x80000004, 0x00412083, "lw ra,4(sp)"),
            (24, 1, 0x80000004, 0x00412083, "lw ra,4(sp)"),
            (25, 0, 0x80000008, 0x00112423, "sw ra,8(sp)"),
            (28, 1, 0x80000008, 0x00112423, "sw ra,8(sp)"),
            (29, 1, 0x8000000C, 0x00000463, "beq zero,zero,8"),
            (30, 1, 0x80000010, 0x30001073, "csrrw zero,mstatus,zero"),
            (32, 0, 0x80000014, 0x00000013, "nop"),
        ], ucode)
        self.assertEqual(result.returncode, 0, result.stderr)
        stats = dict(line.strip().split(":", 1) for line in result.stdout.splitlines() if ":" in line)
        stats = {key.strip(): value.strip() for key, value in stats.items()}
        expected = {
            "Instructions": "5", "Cycles": "12", "Bubbles": "3",
            "CPI": "2.400", "IPC": "0.417",
            "% Arithmetic": "20.000 %", "% Ld/St": "40.000 %",
            "% Branch/Jump": "20.000 %", "% Misc.": "20.000 %",
            "Total Instructions": "5", "Total LD/ST Instructions": "2",
            "Non-zero Offset Load Count": "1", "Non-zero Offset Store Count": "1",
            "% of Non-zero Offset Loads": "50.00 %",
            "% of Non-zero Offset Stores": "50.00 %",
        }
        for name, value in expected.items():
            with self.subTest(statistic=name):
                self.assertEqual(stats[name], value)

    def test_microcode_counts_retirements_and_excludes_bootrom_and_bubbles(self):
        self.assert_workload_statistics(ucode=True)

    def test_pipeline_statistics_and_existing_offset_summary_are_preserved(self):
        self.assert_workload_statistics(ucode=False)

    def test_bootrom_and_unretired_entry_do_not_start_statistics(self):
        for ucode in (True, False):
            with self.subTest(ucode=ucode):
                result = self.analyze([
                    (1, 1, 0x1000, 0x00000013, "nop"),
                    (2, 0, 0x80000000, 0x00000013, "nop"),
                    (3, 0, 0x80000004, 0x00000013, "nop"),
                ], ucode)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Trace analyzer found no instructions", result.stderr)
                self.assertNotIn("Stats:", result.stdout)


if __name__ == "__main__":
    unittest.main()
