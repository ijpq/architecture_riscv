#!/usr/bin/env python3
"""Source selection and single-commit Git metadata for teaching snapshots."""
from pathlib import Path
import subprocess

LOCAL_TOOLS = {
    "tools/barstools", "tools/DRAMSim2", "tools/chisel-testers", "tools/chisel3",
    "tools/firrtl", "tools/firrtl-interpreter", "tools/treadle", "tools/dsptools",
    "sims/firesim", "fpga/fpga-shells",
}
NESTED_TOOLS = ("hardfloat", "api-config", "cde", "berkeley-hardfloat", "mdf")
EXTRAS = {
    "edu_cs152/lab2": ("lab/open2/htif-clock.cc", "lab/open2/htif-cxx.specs"),
    "edu_cs152/lab3": ("lab/open2/pk-spectre",),
    "edu_cs152/lab5": ("lab/common/nharts.c",),
}


def git_bytes(root: Path, *args: str, data: bytes | None = None) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], input=data)


def git_text(root: Path, *args: str) -> str:
    return git_bytes(root, *args).decode().strip()


def index_entries(root: Path) -> list[tuple[str, str]]:
    entries = []
    for raw in git_bytes(root, "ls-files", "--stage", "-z").split(b"\0"):
        if raw:
            fields, name = raw.split(b"\t", 1)
            entries.append((fields.split()[0].decode(), name.decode()))
    return entries


def selected_repositories(root: Path, depth: int = 0) -> list[Path]:
    result = [root]
    for mode, name in index_entries(root):
        if mode != "160000":
            continue
        wanted = (name.startswith("generators/") or name in LOCAL_TOOLS) if depth == 0 else any(
            token in name.lower() for token in NESTED_TOOLS)
        child = root / name
        if wanted and (child / ".git").exists():
            result.extend(selected_repositories(child, depth + 1))
    return result


def source_files(root: Path) -> list[Path]:
    return [root / name for mode, name in index_entries(root)
            if mode != "160000" and ((root / name).is_file() or (root / name).is_symlink())]


def origin_url(root: Path) -> str:
    result = subprocess.run(["git", "-C", str(root), "config", "--get", "remote.origin.url"],
                            text=True, capture_output=True)
    origin = result.stdout.strip().replace("https://github.com:443/", "https://github.com/")
    if origin.startswith("git@github.com:"):
        origin = "https://github.com/" + origin.split(":", 1)[1]
    # Do not copy host-local paths, authentication details or configuration.
    if origin.startswith("https://github.com/") and "@" not in origin and "?" not in origin:
        return origin
    return ""


def exact_tags(root: Path, head: str) -> dict[str, str]:
    result = {}
    refs = git_text(root, "for-each-ref", "--points-at", head,
                    "--format=%(refname) %(objectname) %(*objectname)", "refs/tags")
    for line in refs.splitlines():
        parts = line.split()
        if parts[1] == head or (len(parts) == 3 and parts[2] == head):
            result[parts[0]] = parts[1]
    return result


def write_git_snapshot(root: Path, destination: Path) -> dict:
    head = git_text(root, "rev-parse", "HEAD")
    objects = {head, git_text(root, "rev-parse", "HEAD^{tree}")}
    for raw in git_bytes(root, "ls-tree", "-r", "-t", "HEAD", "-z").split(b"\0"):
        if raw:
            fields = raw.split(b"\t", 1)[0].split()
            if fields[1] != b"commit":
                objects.add(fields[2].decode())
    tags = exact_tags(root, head)
    objects.update(tags.values())
    packed = git_bytes(root, "pack-objects", "--stdout", "--compression=6",
                       data=("\n".join(sorted(objects)) + "\n").encode())
    subprocess.run(["git", "init", "--bare", "-q", str(destination)], check=True)
    git_bytes(destination, "index-pack", "--stdin", data=packed)
    (destination / "HEAD").write_text(head + "\n")
    (destination / "shallow").write_text(head + "\n")
    for ref, value in tags.items():
        target = destination / ref
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(value + "\n")
    git_bytes(destination, "read-tree", "HEAD")
    origin = origin_url(root)
    config = "[core]\n\trepositoryformatversion = 0\n\tbare = false\n\tfilemode = true\n"
    if origin:
        config += f'[remote "origin"]\n\turl = {origin}\n'
    (destination / "config").write_text(config)
    # Keep no hooks, credentials, logs, personal config, or unreachable history.
    kept = [destination / name for name in ("HEAD", "shallow", "config", "index", "refs")]
    kept += list((destination / "objects/pack").glob("*"))
    kept += [destination / name for name in tags]
    return {"commit": head, "origin": origin, "tags": list(tags),
            "metadata_files": [str(path.relative_to(destination)) for path in kept],
            "working_changes": git_text(root, "diff", "--name-status", "HEAD", "--")}
