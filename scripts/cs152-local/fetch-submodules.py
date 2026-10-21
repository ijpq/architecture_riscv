#!/usr/bin/env python3
"""Fetch pinned local-simulation dependencies, without recursive FPGA/VLSI downloads."""
import argparse
import configparser
import pathlib
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]


def git(cwd, *args, capture=False):
    result = subprocess.run(["git", "-C", str(cwd), *args], check=True,
                            text=True, stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else None


def fetch(parent, path, url, commit):
    dest = parent / path
    # The host rewrites github HTTPS to SSH. Explicit port avoids that global rewrite.
    if url.startswith("https://github.com/"):
        url = url.replace("https://github.com/", "https://github.com:443/", 1)
    if (dest / ".git").exists():
        current = git(dest, "rev-parse", "HEAD", capture=True)
        if current != commit:
            raise RuntimeError(f"Keep existing checkout {dest}: {current} != {commit}")
        print(f"KEEP {dest.relative_to(ROOT)} {commit}", flush=True)
        return
    if dest.exists() and any(p.is_file() and "target" not in p.relative_to(dest).parts
                             for p in dest.rglob("*")):
        raise RuntimeError(f"Refuse to overwrite non-generated files: {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    git(dest, "init", "-q")
    git(dest, "remote", "add", "origin", url)
    print(f"FETCH {dest.relative_to(ROOT)} {commit} {url}", flush=True)
    git(dest, "fetch", "--depth=1", "origin", commit)
    git(dest, "checkout", "--detach", "-q", "FETCH_HEAD")


def restore(parent, predicate, nested=False):
    config = configparser.ConfigParser(interpolation=None)
    if not (parent / ".gitmodules").exists():
        return
    config.read(parent / ".gitmodules")
    for section in config.sections():
        path, url = config[section]["path"], config[section]["url"]
        if not predicate(path):
            continue
        line = git(parent, "ls-tree", "HEAD", "--", path, capture=True)
        if not line.startswith("160000 "):
            raise RuntimeError(f"Not a pinned gitlink: {parent}/{path}")
        commit = line.split()[2]
        fetch(parent, path, url, commit)
        if nested:
            restore(parent / path, lambda p: any(k in p.lower() for k in
                    ("hardfloat", "api-config", "cde", "berkeley-hardfloat", "mdf")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lab", choices=("lab2", "lab3", "lab4", "lab5"))
    args = parser.parse_args()
    parent = ROOT / "edu_cs152" / args.lab
    if args.lab == "lab4":
        restore(parent, lambda p: p == "env")
    else:
        restore(parent, lambda p: p.startswith("generators/") or p in (
            "tools/barstools", "tools/DRAMSim2", "tools/chisel-testers",
            "tools/chisel3", "tools/firrtl", "tools/firrtl-interpreter",
            "tools/treadle", "tools/dsptools", "sims/firesim", "fpga/fpga-shells"), nested=True)


if __name__ == "__main__":
    main()
