#!/usr/bin/env python3
"""Restore missing build-resource symlinks only; never overwrite exercise files."""
from pathlib import Path
import os
import subprocess

root = Path(__file__).resolve().parents[2]
for lab in ("lab2", "lab3", "lab5"):
    base = root / "edu_cs152" / lab
    for relative in ("generators/utilities/src/main/resources/bootrom",
                     "sims/verilator/dramsim2_ini", "sims/vcs/dramsim2_ini"):
        dest = base / relative
        if os.path.lexists(dest):
            continue
        result = subprocess.run(["git", "-C", str(base), "ls-tree", "HEAD", "--", relative],
                                check=True, text=True, capture_output=True)
        if not result.stdout.startswith("120000 "):
            continue
        target = subprocess.run(["git", "-C", str(base), "show", f"HEAD:{relative}"],
                                check=True, text=True, capture_output=True).stdout
        if not (dest.parent / target).exists():
            raise RuntimeError(f"Missing target for build link {dest}: {target}")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(target)
        print(f"RESTORE {dest.relative_to(root)} -> {target}")
