#!/usr/bin/env python3
"""Pack/check/restore pinned teaching sources, not toolchains or build caches."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile

from source_archive import confined_destination, extract_members, relative_path, validate_members
from source_git import EXTRAS, selected_repositories, source_files, write_git_snapshot

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLES = Path(__file__).with_name("sources")
SOURCES = {
    "lab1": "chipyard-cs152-sp23",
    "lab2": "edu_cs152/lab2",
    "lab3": "edu_cs152/lab3",
    "lab4-original": "edu_cs152/lab4",
    "lab5": "edu_cs152/lab5",
    "rv32-reference": "chipyard/toolchains/riscv-tools/riscv-tests",
}


def sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def normalized_info(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = info.gid = info.mtime = 0
    info.uname = info.gname = ""
    return info


def pack_one(source_root: Path, relative: str, archive: Path) -> dict:
    root = source_root / relative
    repositories = []
    with tempfile.TemporaryDirectory() as scratch, tarfile.open(archive, "w:gz") as output:
        for number, repo in enumerate(selected_repositories(root)):
            prefix = Path("payload") / repo.relative_to(root)
            for path in source_files(repo):
                output.add(path, arcname=str(prefix / path.relative_to(repo)), recursive=False,
                           filter=normalized_info)
            metadata = Path(scratch) / str(number)
            record = write_git_snapshot(repo, metadata)
            for name in record.pop("metadata_files"):
                output.add(metadata / name, arcname=str(prefix / ".git" / name), recursive=False,
                           filter=normalized_info)
            record["path"] = str(repo.relative_to(root))
            repositories.append(record)
        for name in EXTRAS.get(relative, ()):
            path = root / name
            if not path.is_file():
                raise ValueError(f"Required local compatibility file missing: {path}")
            output.add(path, arcname="payload/" + name, recursive=False, filter=normalized_info)
    return {"destination": relative, "archive": archive.name, "bytes": archive.stat().st_size,
            "sha256": sha256(archive), "repositories": repositories,
            "additional_files": list(EXTRAS.get(relative, ()))}


def pack_bundles(source_root: Path, bundle_dir: Path, sources: dict[str, str] | None = None) -> dict:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"format": 1, "git_history": "one shallow upstream commit per repository",
                "scope": "Current tracked working sources plus explicit course compatibility files",
                "bundles": []}
    for name, relative in (SOURCES if sources is None else sources).items():
        archive = bundle_dir / (name + ".tar.gz")
        if archive.exists() or archive.is_symlink():
            raise ValueError(f"Refuse to replace source archive: {archive}")
        record = pack_one(source_root, relative, archive)
        record["name"] = name
        manifest["bundles"].append(record)
        print(f"PACK {name}: {record['bytes']} bytes, {len(record['repositories'])} source repositories")
    (bundle_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return manifest


def checked_manifest(bundle_dir: Path) -> dict:
    manifest = json.loads((bundle_dir / "manifest.json").read_text())
    if manifest.get("format") != 1:
        raise ValueError("Unsupported source manifest format")
    names = set()
    destinations = set()
    for entry in manifest["bundles"]:
        relative_path(entry["destination"])
        archive_path = relative_path(entry["archive"])
        if len(archive_path.parts) != 1 or not entry["archive"].endswith(".tar.gz"):
            raise ValueError("Source archive must be a .tar.gz basename")
        if entry["name"] in names or entry["destination"] in destinations:
            raise ValueError("Duplicate source bundle name or destination")
        names.add(entry["name"])
        destinations.add(entry["destination"])
        archive = bundle_dir / entry["archive"]
        if archive.stat().st_size != entry["bytes"] or sha256(archive) != entry["sha256"]:
            raise ValueError(f"Source archive hash/size mismatch: {entry['name']}")
        with tarfile.open(archive, "r:gz") as handle:
            validate_members(handle)
    return manifest


def restore_bundles(root: Path, bundle_dir: Path, names: tuple[str, ...] = ()) -> list[str]:
    manifest = checked_manifest(bundle_dir)
    entries = [entry for entry in manifest["bundles"] if not names or entry["name"] in names]
    missing = set(names) - {entry["name"] for entry in manifest["bundles"]}
    if missing:
        raise ValueError(f"Unknown source bundles: {sorted(missing)}")
    root = root.resolve()
    for entry in entries:
        confined_destination(root, entry["destination"])
    results = []
    for entry in entries:
        destination = confined_destination(root, entry["destination"])
        if destination.exists() and any(destination.iterdir()):
            results.append(f"KEEP {entry['name']}: existing nonempty directory")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=destination.parent) as scratch:
            with tarfile.open(bundle_dir / entry["archive"], "r:gz") as archive:
                extract_members(archive, Path(scratch))
            if destination.exists():
                destination.rmdir()
            os.rename(Path(scratch) / "payload", destination)
        results.append("RESTORE " + entry["name"])
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("pack", "check", "restore"))
    parser.add_argument("--root", type=Path, default=ROOT, help="source/project root; default this checkout")
    parser.add_argument("--bundle-dir", type=Path, default=DEFAULT_BUNDLES)
    parser.add_argument("--only", action="append", choices=tuple(SOURCES), default=[])
    args = parser.parse_args()
    if args.action == "pack":
        pack_bundles(args.root, args.bundle_dir)
    elif args.action == "check":
        manifest = checked_manifest(args.bundle_dir)
        print(f"VERIFIED {len(manifest['bundles'])} source archives")
    else:
        for result in restore_bundles(args.root, args.bundle_dir, tuple(args.only)):
            print(result)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, tarfile.TarError) as error:
        print("ERROR:", error, file=sys.stderr)
        sys.exit(1)
