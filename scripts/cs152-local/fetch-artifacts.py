#!/usr/bin/env python3
"""Recover public, pinned course artifacts and the RV32 multilib compiler.

No exercise solutions are downloaded. Check Git blob identity or the publisher's
SHA256 before using a download; preserve any existing different course file.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local"
PK_REF = "296373efa4762bb41387970dfcb98f5f0914e160"
XPACK_VERSION = "12.2.0-3"


def opener():
    proxy = os.environ.get("CS152_PROXY")
    if proxy is None:
        proxy = subprocess.run(["git", "config", "--get", "http.proxy"],
                               text=True, stdout=subprocess.PIPE).stdout.strip()
    return urllib.request.build_opener(urllib.request.ProxyHandler(
        {} if proxy == "direct" else {"http": proxy, "https": proxy} if proxy else {}))


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "cs152-local-environment"})
    with opener().open(req, timeout=60) as response:
        return response.read()


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def pk_spectre():
    url = f"https://api.github.com/repos/cs152-teach/chipyard-cs152/contents/lab/open2/pk-spectre?ref={PK_REF}"
    artifact = json.loads(get(url))
    data = base64.b64decode(artifact["content"])
    identity = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if identity != artifact["sha"] or not data.startswith(b"\x7fELF"):
        raise RuntimeError("Course pk-spectre Git blob verification failed")
    dest = ROOT / "edu_cs152/lab3/lab/open2/pk-spectre"
    if dest.exists() and dest.read_bytes() != data:
        raise RuntimeError(f"Refuse to overwrite existing different {dest}")
    dest.write_bytes(data)
    dest.chmod(0o755)
    evidence = {"source": url, "ref": PK_REF, "git_blob": identity,
                "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    (LOCAL / "evidence").mkdir(parents=True, exist_ok=True)
    (LOCAL / "evidence/pk-spectre-download.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(f"Verified official course pk-spectre: {dest}, {len(data)} bytes")


def multilib():
    name = f"xpack-riscv-none-elf-gcc-{XPACK_VERSION}-linux-x64.tar.gz"
    url = f"https://github.com/xpack-dev-tools/riscv-none-elf-gcc-xpack/releases/download/v{XPACK_VERSION}/{name}"
    downloads = LOCAL / "downloads"
    downloads.mkdir(parents=True, exist_ok=True)
    dest = downloads / name
    checksum = get(url + ".sha").decode().split()[0].lower()
    if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
        raise RuntimeError("Unexpected publisher SHA256 format")
    if not dest.exists() or sha256(dest) != checksum:
        temporary = dest.with_suffix(".partial")
        req = urllib.request.Request(url, headers={"User-Agent": "cs152-local-environment"})
        print(f"Downloading {url}", flush=True)
        with opener().open(req, timeout=90) as response, temporary.open("wb") as stream:
            shutil.copyfileobj(response, stream, length=1024 * 1024)
        if sha256(temporary) != checksum:
            raise RuntimeError(f"SHA256 mismatch: retain {temporary} for diagnosis")
        temporary.replace(dest)
    tools = LOCAL / "tools"
    tools.mkdir(parents=True, exist_ok=True)
    install = tools / f"xpack-riscv-none-elf-gcc-{XPACK_VERSION}"
    if not (install / "bin/riscv-none-elf-gcc").exists():
        with tarfile.open(dest) as archive:
            members = archive.getmembers()
            for member in members:
                resolved = (tools / member.name).resolve()
                if tools.resolve() not in resolved.parents:
                    raise RuntimeError("Unsafe archive path")
                if member.issym() or member.islnk():
                    target = ((tools / member.name).parent / member.linkname).resolve() if member.issym() else (tools / member.linkname).resolve()
                    if tools.resolve() not in target.parents:
                        raise RuntimeError("Unsafe archive link")
                if member.isdev() or member.isfifo():
                    raise RuntimeError("Unsafe archive special file")
            archive.extractall(tools)
    if not (install / "bin/riscv-none-elf-gcc").exists():
        raise RuntimeError(f"Unexpected toolchain layout: {tools}")
    (LOCAL / "evidence").mkdir(parents=True, exist_ok=True)
    (LOCAL / "evidence/rv32-toolchain-download.json").write_text(json.dumps(
        {"source": url, "version": XPACK_VERSION, "sha256": checksum,
         "install": str(install)}, indent=2) + "\n")
    print(f"Verified RV32 multilib compiler: {install}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", choices=("pk-spectre", "multilib"))
    args = parser.parse_args()
    if args.artifact == "pk-spectre":
        pk_spectre()
    else:
        multilib()
