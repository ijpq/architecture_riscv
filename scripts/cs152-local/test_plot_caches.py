"""Offline tests for the Python 3 cache-plot replacement."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET


class PlotTests(unittest.TestCase):
    def module(self):
        spec = importlib.util.spec_from_file_location("cache_plot", Path(__file__).with_name("plot-caches.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def line(self, size=1024, time="4.63166", units="Cycles Per Iteration"):
        return (f"App:[caches],NumThreads:[0],AppSize:[{size}],Time:[{time}],"
                f"TimeUnits:[{units}],NumIterations:[21632],RunType:[0]\n")

    def test_parses_only_benchmark_records_with_correct_byte_units(self):
        plot = self.module()
        records = plot.parse_records("UART ready\nWARNING unrelated\n" + self.line(), "Rocket")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["bytes"], 4096)
        self.assertEqual(records[0]["cycles_per_iteration"], 4.63166)
        self.assertEqual(records[0]["iterations"], 21632)
        self.assertEqual(records[0]["source"], "Rocket")

    def test_empty_or_invalid_records_are_not_silently_plotted(self):
        plot = self.module()
        for text in ("only simulator warnings", self.line(size=0), self.line(time="nan"),
                     self.line(time="-1"), self.line(units="Seconds"), "App:[caches],Time:[1]"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                plot.parse_records(text, "bad")

    def test_writes_csv_and_valid_svg_with_separate_sources(self):
        plot = self.module()
        records = plot.parse_records(self.line() + self.line(size=2048, time="5.5"), "Rocket")
        records += plot.parse_records(self.line(), "L2")
        with tempfile.TemporaryDirectory() as tmp:
            csv_file, svg_file = plot.write_plot(records, Path(tmp) / "subdir/measurements")
            with csv_file.open(newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 3)
            self.assertEqual(rows[1]["bytes"], "8192")
            self.assertEqual(rows[2]["source"], "L2")
            svg = ET.parse(svg_file).getroot()
            self.assertTrue(svg.tag.endswith("svg"))
            self.assertEqual(len(svg.findall("{http://www.w3.org/2000/svg}polyline")), 2)

    def test_single_point_svg_escapes_filename_text(self):
        plot = self.module()
        records = plot.parse_records(self.line(), "R<&>")
        with tempfile.TemporaryDirectory() as tmp:
            _, svg_file = plot.write_plot(records, Path(tmp) / "one")
            ET.parse(svg_file)
            self.assertIn("R&lt;&amp;&gt;", svg_file.read_text())
