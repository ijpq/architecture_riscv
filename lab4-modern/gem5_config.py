"""RVV 1.0 + O3/timing-cache teaching model, NOT the old Lab 4 Spike model."""
import argparse
import json
import sys
from pathlib import Path

import m5
from m5.objects import (
    AddrRange, Cache, DefaultFUPool, Process, RiscvO3CPU, Root,
    SEWorkload, SIMD_Unit, SimpleMemory, SrcClockDomain, System,
    SystemXBar, L2XBar, VoltageDomain,
)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/cs152-local"))
from lab4_modern import model_parameters

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--binary", required=True)
parser.add_argument("--vlen", type=int, default=256)
parser.add_argument("--vector-latency", type=int, default=4)
parser.add_argument("--vector-units", type=int, default=2)
parser.add_argument("--memory-latency-ns", type=int, default=50)
parser.add_argument("--max-cycles", type=int, default=100_000_000)
parser.add_argument("--arg", action="append", default=[])
args = parser.parse_args()
model = model_parameters(args.vlen, args.vector_latency, args.vector_units, args.memory_latency_ns)
if args.max_cycles <= 0:
    parser.error("--max-cycles must be positive")

m5.ticks.setGlobalFrequency("1THz")
system = System()
system.clk_domain = SrcClockDomain(clock="1GHz", voltage_domain=VoltageDomain())
system.mem_mode = "timing"
system.mem_ranges = [AddrRange("512MiB")]
system.cache_line_size = 64
system.cpu = RiscvO3CPU()
# Preserve the standard scalar/memory functional units; replace SIMD only.
pool = DefaultFUPool()
for unit in pool.FUList:
    if isinstance(unit, SIMD_Unit):
        unit.count = model["vector_units"]
        for op in unit.opList:
            op.opLat = model["vector_latency"]
# gem5 25.1 routes execution through IQUnit's pool, not a CPU child named fuPool.
# Adding an unused CPU child serializes correctly but has no timing effect.
system.cpu.instQueues[0].fuPool = pool
system.cpu.icache = Cache(size="32KiB", assoc=4, tag_latency=2, data_latency=2,
                         response_latency=2, mshrs=8, tgts_per_mshr=16)
system.cpu.dcache = Cache(size="32KiB", assoc=4, tag_latency=2, data_latency=2,
                         response_latency=2, mshrs=16, tgts_per_mshr=16)
system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side
system.l2bus = L2XBar(width=32)
system.cpu.icache.mem_side = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side = system.l2bus.cpu_side_ports
system.l2 = Cache(size="256KiB", assoc=8, tag_latency=12, data_latency=12,
                  response_latency=12, mshrs=32, tgts_per_mshr=16)
system.l2bus.mem_side_ports = system.l2.cpu_side
system.membus = SystemXBar(width=32)
system.l2.mem_side = system.membus.cpu_side_ports
system.memory = SimpleMemory(range=system.mem_ranges[0],
                             latency=f"{model['memory_latency_ns']}ns",
                             bandwidth="12.8GiB/s")
system.memory.port = system.membus.mem_side_ports
system.system_port = system.membus.cpu_side_ports
system.cpu.createInterruptController()
system.workload = SEWorkload.init_compatible(args.binary)
process = Process()
process.cmd = [args.binary, *args.arg]
process.cwd = str(Path(m5.options.outdir).resolve())
process.env = ["LC_ALL=C"]
system.cpu.workload = process
system.cpu.createThreads()
system.cpu.isa[0].enable_rvv = True
system.cpu.isa[0].vlen = model["vlen"]
system.cpu.isa[0].elen = 64
system.exit_on_work_items = True
root = Root(full_system=False, system=system)
m5.instantiate()

# Work markers bracket the kernel only; startup and verification are excluded.
# The first stats dump is the ROI. gem5 may append a second dump at process exit.
deadline = args.max_cycles * 1000  # 1 THz tick frequency, 1 GHz model clock.
roi_start = None
roi_ticks = 0
roi_count = 0
complete = False
while True:
    remaining = deadline - m5.curTick()
    if remaining <= 0:
        cause, code = "simulate() limit reached", 1
        break
    event = m5.simulate(remaining)
    cause, code = event.getCause(), event.getCode()
    if cause == "workbegin" and roi_start is None and roi_count == 0:
        roi_start = m5.curTick()
        m5.stats.reset()
    elif cause == "workend" and roi_start is not None and not complete:
        roi_ticks = m5.curTick() - roi_start
        roi_count += 1
        complete = True
        m5.stats.dump()
        m5.stats.reset()
    else:
        break
passed = (complete and roi_count == 1 and roi_ticks > 0 and code == 0
          and cause == "exiting with last active thread context")
summary = dict(passed=passed, exit_cause=cause, exit_code=code,
               roi_count=roi_count, roi_ticks=roi_ticks, model=model,
               model_name="gem5-O3-RVV1.0-per-register-FU", clock_hz=1_000_000_000)
(Path(m5.options.outdir) / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print("CS152_GEM5_RESULT", json.dumps(summary, sort_keys=True))
sys.exit(0 if passed else 1)
