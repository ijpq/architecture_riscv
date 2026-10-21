#!/usr/bin/env python3
"""Fetch/check the pinned public PDFs; never replace an existing different file."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("materials.json")


def validate(data, entry):
    if len(data) != entry["bytes"]:
        raise ValueError(f"Wrong size: {entry['path']}")
    if not data.startswith(b"%PDF-"):
        raise ValueError(f"Not a PDF (possibly a login page): {entry['path']}")
    if hashlib.sha256(data).hexdigest() != entry["sha256"]:
        raise ValueError(f"SHA-256 mismatch: {entry['path']}")
    git_blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
    if hashlib.sha1(git_blob).hexdigest() != entry["upstream_git_blob"]:
        raise ValueError(f"Upstream Git blob mismatch: {entry['path']}")


def one(entry, download):
    destination = ROOT / entry["path"]
    if destination.exists():
        validate(destination.read_bytes(), entry)
        return "OK " + entry["id"]
    if not download:
        raise ValueError("Missing: " + entry["path"])
    request = urllib.request.Request(entry["url"], headers={"User-Agent": "CS152-local-self-study/1"})
    with urllib.request.urlopen(request, timeout=90) as response:
        data = response.read(entry["bytes"] + 1)
    validate(data, entry)
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation also protects a concurrent user's newly created file.
    with destination.open("xb") as output:
        output.write(data)
    return "FETCH " + entry["id"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="download missing files only")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(one, entry, args.fetch) for entry in manifest["files"]]
        for future in futures:
            print(future.result(), flush=True)
    print(f"VERIFIED {len(manifest['files'])} public course PDFs; original copyrights retained.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError) as error:
        print("ERROR:", error, file=sys.stderr)
        sys.exit(1)
