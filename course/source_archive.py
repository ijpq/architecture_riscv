#!/usr/bin/env python3
"""Path confinement and extraction rules for the self-study source archives."""
from pathlib import Path, PurePosixPath
import posixpath
import shutil
import tarfile

MAX_UNPACKED_BYTES = 2 * 1024**3


def relative_path(value: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Unsafe relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value or value == ".":
        raise ValueError(f"Unsafe relative path: {value!r}")
    return path


def confined_destination(root: Path, relative: str) -> Path:
    path = relative_path(relative)
    destination = root
    for component in path.parts:
        destination = destination / component
        if destination.is_symlink():
            raise ValueError(f"Destination contains a symlink: {destination}")
        if destination.exists() and not destination.is_dir():
            raise ValueError(f"Destination contains a non-directory: {destination}")
    return destination


def validate_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = []
    names = set()
    nondirectories = set()
    total = 0
    for member in archive:
        path = relative_path(member.name.rstrip("/"))
        if path.parts[0] != "payload" or (str(path) == "payload" and not member.isdir()):
            raise ValueError(f"Unsafe archive prefix: {member.name}")
        if str(path) in names:
            raise ValueError(f"Duplicate archive member: {member.name}")
        if not (member.isfile() or member.isdir() or member.issym()):
            raise ValueError(f"Unsupported archive member type: {member.name}")
        names.add(str(path))
        if not member.isdir():
            nondirectories.add(str(path))
        total += member.size
        if member.size < 0 or total > MAX_UNPACKED_BYTES:
            raise ValueError("Source archive exceeds unpacked size limit")
        if member.issym():
            validate_link(path, member.linkname)
        members.append(member)
    for member in members:
        parents = PurePosixPath(member.name.rstrip("/")).parents
        if any(str(parent) in nondirectories for parent in parents):
            raise ValueError(f"Archive member traverses a file or symlink: {member.name}")
    if not members:
        raise ValueError("Empty source archive")
    return members


def validate_link(path: PurePosixPath, target: str) -> None:
    resolved = posixpath.normpath(posixpath.join(str(path.parent), target))
    if (not target or "\\" in target or PurePosixPath(target).is_absolute()
            or not (resolved == "payload" or resolved.startswith("payload/"))):
        raise ValueError(f"Unsafe archive symlink: {path} -> {target}")


def extract_members(archive: tarfile.TarFile, scratch: Path) -> None:
    members = validate_members(archive)
    for member in members:
        if member.issym():
            continue
        path = scratch / member.name
        path.parent.mkdir(parents=True, exist_ok=True)
        if member.isdir():
            path.mkdir(exist_ok=True)
        else:
            with archive.extractfile(member) as source, path.open("xb") as destination:
                shutil.copyfileobj(source, destination)
            path.chmod(member.mode & 0o777)
    for member in members:
        if member.issym():
            path = scratch / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.symlink_to(member.linkname)
    # Lexical checks alone miss symlink chains followed by '..'. Resolve only
    # after all links exist; no file writes ever follow an archive symlink.
    payload = (scratch / "payload").resolve()
    for member in members:
        if member.issym():
            try:
                resolved = (scratch / member.name).resolve()
            except (OSError, RuntimeError) as error:
                raise ValueError(f"Unsafe cyclic archive symlink: {member.name}") from error
            if not resolved.is_relative_to(payload):
                raise ValueError(f"Archive symlink chain escapes payload: {member.name}")
