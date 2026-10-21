#!/usr/bin/env python3
"""Plot course ccbench cycle measurements with Python 3, without matplotlib.

AppSize is a count of 32-bit int elements, not bytes. Keep each input log and
RunType separate; do not infer cache parameters or fill in the Mystery exercise.
"""
import argparse
import csv
from html import escape
import math
from pathlib import Path
import re
import sys

FIELDS = ("source", "run_type", "elements", "bytes", "cycles_per_iteration", "iterations")


def parse_records(text, source):
    records = []
    for number, line in enumerate(text.splitlines(), 1):
        if "App:[caches]" not in line:
            continue
        try:
            fields = dict(re.findall(r"(\w+):\[([^\]]*)\]", line))
            elements, iterations = int(fields["AppSize"]), int(fields["NumIterations"])
            cycles = float(fields["Time"])
            if (fields["TimeUnits"] != "Cycles Per Iteration" or
                    not 0 < elements <= 2**63 - 1 or iterations <= 0 or
                    not math.isfinite(cycles) or not 0 < cycles <= 2**64 - 1):
                raise ValueError("expected positive cycle measurements and array sizes")
            records.append(dict(zip(FIELDS, (source, int(fields["RunType"]), elements,
                                            elements * 4, cycles, iterations))))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"{source}:{number}: invalid ccbench record: {exc}") from exc
    if not records:
        raise ValueError(f"{source}: no App:[caches] cycle records")
    return records


def write_plot(records, prefix):
    if not records:
        raise ValueError("No cache measurements to plot")
    groups = {}
    for record in records:
        groups.setdefault((record["source"], record["run_type"]), []).append(record)
    xmin = math.floor(math.log2(min(row["bytes"] for row in records)))
    xmax = math.ceil(math.log2(max(row["bytes"] for row in records)))
    if xmax == xmin:
        xmin, xmax = xmin - 1, xmax + 1
    ymax = max(1.0, max(row["cycles_per_iteration"] for row in records)) * 1.1
    left, top, width, height = 85, 45, 790, 330
    x = lambda size: left + (math.log2(size) - xmin) / (xmax - xmin) * width
    y = lambda cycles: top + height - cycles / ymax * height
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="920" height="{475 + 22 * len(groups)}" viewBox="0 0 920 {475 + 22 * len(groups)}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<style>text{font-family:sans-serif;font-size:12px} .grid{stroke:#ddd}</style>',
           '<text x="85" y="24">ccbench caches — measured RTL cycles per iteration</text>']
    for i in range(6):
        value = ymax * i / 5
        position = y(value)
        svg += [f'<line x1="{left}" x2="{left + width}" y1="{position:.2f}" y2="{position:.2f}" class="grid"/>',
                f'<text x="{left - 9}" y="{position + 4:.2f}" text-anchor="end">{value:.3g}</text>']
    step = max(1, math.ceil((xmax - xmin) / 10))
    for power in range(xmin, xmax + 1, step):
        position = x(2**power)
        svg += [f'<line x1="{position:.2f}" x2="{position:.2f}" y1="{top}" y2="{top + height}" class="grid"/>',
                f'<text x="{position:.2f}" y="{top + height + 20}" text-anchor="middle">{2**power / 1024:g}</text>']
    svg += ['<text x="480" y="422" text-anchor="middle">Array size (KiB, logarithmic; AppSize × 4 bytes)</text>',
            '<text x="85" y="445">Lines only connect collected measurements; they do not identify cache parameters.</text>']
    colors = ("#1259a7", "#d04432", "#28834b", "#8456b3", "#8a6220")
    for index, ((source, run_type), rows) in enumerate(groups.items()):
        color = colors[index % len(colors)]
        rows = sorted(rows, key=lambda row: row["bytes"])
        points = " ".join(f'{x(row["bytes"]):.2f},{y(row["cycles_per_iteration"]):.2f}' for row in rows)
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
        for row in rows:
            svg.append(f'<circle cx="{x(row["bytes"]):.2f}" cy="{y(row["cycles_per_iteration"]):.2f}" r="3" fill="{color}"/>')
        label = escape(f"{Path(source).stem} [RunType={run_type}]")
        svg.append(f'<text x="85" y="{470 + 22 * index}" fill="{color}">{label}</text>')
    svg.append('</svg>')
    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_file, svg_file = Path(str(prefix) + ".csv"), Path(str(prefix) + ".svg")
    with csv_file.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(records)
    svg_file.write_text("\n".join(svg) + "\n")
    return csv_file, svg_file


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="ccbench logs, one source/configuration per file")
    parser.add_argument("--output", required=True, type=Path, help="Output prefix, without .csv/.svg suffix")
    args = parser.parse_args(argv)
    try:
        records = []
        for logfile in args.logs:
            records.extend(parse_records(logfile.read_text(errors="replace"), str(logfile.resolve())))
        for path in write_plot(records, args.output):
            print(path)
        print(f"Plotted {len(records)} actual measurements; no cache parameters inferred.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"CS152 plot error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
