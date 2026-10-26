#!/usr/bin/env python3
"""Synchronize the managed CS152 Markdown note with its Notion page."""
import argparse
import datetime
import fcntl
import hashlib
import html
import json
import os
from pathlib import Path
import posixpath
import re
import shutil
import socket
import stat
import struct
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "notes/notion-sync.json"
LOCAL = ROOT / ".local/notion-sync"


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def canonical(text):
    return text.replace("\r\n", "\n").strip() + "\n"


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = path.stat().st_mode & 0o777 if path.exists() else 0o600
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + "-", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
        Path(temporary).chmod(mode)
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def live_runtime():
    home = Path(os.environ.get("HAPI_HOME", "~/.hapi")).expanduser()
    settings = json.loads((home / "settings.json").read_text())
    hub = os.environ.get("HAPI_API_URL") or settings.get("apiUrl")
    token = os.environ.get("CLI_API_TOKEN") or settings.get("cliApiToken", "")
    wanted = os.environ.get("HAPI_SESSION_ID")
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser().resolve()
    candidates = []
    for path in (home / "codex-runtimes").glob("*.json"):
        try:
            record = json.loads(path.read_text())
            if record["hub"] != hub or record["authHash"] != digest(token):
                continue
            if Path(record["codexHome"]).resolve() != codex_home:
                continue
            os.kill(record["pid"], 0)
            endpoint = record["endpoint"]
            if not endpoint.startswith("unix://"):
                continue
            unix = Path(endpoint.removeprefix("unix://"))
            for item in (path, unix.parent, unix):
                metadata = item.stat()
                if metadata.st_uid != os.getuid() or metadata.st_mode & 0o077:
                    raise ValueError("Runtime ownership files/socket must be private")
            if not stat.S_ISSOCK(unix.stat().st_mode):
                continue
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as probe:
                probe.settimeout(2)
                probe.connect(str(unix))
                pid, uid, _ = struct.unpack(
                    "3i", probe.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
                )
            if pid != record["pid"] or uid != os.getuid():
                continue
            for sid, binding in record["sessions"].items():
                if binding.get("active") and (not wanted or sid == wanted):
                    candidates.append({
                        "endpoint": endpoint, "token": record.get("token"),
                        "threadId": binding["threadId"],
                    })
        except (OSError, ValueError, KeyError, TypeError):
            continue
    if not candidates:
        raise RuntimeError("No authenticated local HAPI/Codex runtime; sync can retry later")
    return candidates[0]


class Notion:
    def __init__(self):
        self.runtime = live_runtime()

    def call(self, tool, arguments):
        node = shutil.which("node")
        if not node:
            raise RuntimeError("Node.js is required for the local MCP bridge")
        result = subprocess.run(
            [node, str(ROOT / "scripts/notion-sync/bridge.mjs")],
            input=json.dumps({**self.runtime, "tool": tool, "arguments": arguments}),
            text=True, capture_output=True, timeout=55,
        )
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or "MCP bridge failed")
        response = json.loads(result.stdout)
        if isinstance(response.get("structuredContent"), dict):
            data = response["structuredContent"]
        else:
            text = "\n".join(
                item["text"] for item in response.get("content", []) if item.get("type") == "text"
            )
            try:
                data = json.loads(text)
            except ValueError:
                return {"text": text}
        if isinstance(data, dict) and (
            data.get("name") == "APIResponseError"
            or isinstance(data.get("status"), int) and data["status"] >= 400
        ):
            raise RuntimeError(f"Notion API error: {data.get('code', 'unknown')}: {data.get('message', '')}")
        return data


def transform_prose(body, transform):
    """Keep fenced examples and inline code literal while converting prose."""
    result = []
    fence = None
    for line in body.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            run = marker.group(1)
            if fence is None:
                fence = run
            elif run[0] == fence[0] and len(run) >= len(fence) and not line[marker.end():].strip():
                fence = None
            result.append(line)
        elif fence:
            result.append(line)
        else:
            parts = []
            position = 0
            for match in re.finditer(r"(`+)(.*?)\1", line):
                parts.append(transform(line[position:match.start()]))
                parts.append(match.group(0))
                position = match.end()
            parts.append(transform(line[position:]))
            result.append("".join(parts))
    return canonical("\n".join(result))


def split_note(source):
    lines = source.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ValueError("Managed note must start with one H1 title")
    return lines[0][2:].strip(), canonical("\n".join(lines[1:]))


def render_body(body, relative):
    def link(match):
        label, target = match.groups()
        parsed = urlsplit(target)
        if parsed.scheme or not parsed.path:
            return match.group(0)
        destination = posixpath.normpath(posixpath.join(posixpath.dirname(relative), parsed.path))
        if destination.startswith("../") or destination.startswith("/"):
            raise ValueError("Note link escapes the repository")
        suffix = ("?" + parsed.query if parsed.query else "") + (
            "#" + parsed.fragment if parsed.fragment else ""
        )
        return f"[{label}](https://github.com/ijpq/architecture_riscv/blob/main/{destination}{suffix})"

    def convert(text):
        if re.search(r"</?[A-Za-z][\w-]*(?:\s[^>]*)?/?>", text):
            raise ValueError("Use plain Markdown; raw HTML/rich blocks require manual conversion")
        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
        return re.sub(
            r"(?<![\w/])(\d{4}-\d{2}-\d{2})(?![\w/])",
            lambda match: f'<date start="{match.group(1)}" />', text,
        )

    return transform_prose(body, convert)


def render(source, relative):
    title, body = split_note(source)
    return title, render_body(body, relative)


def markdown_body(body, relative):
    def convert(text):
        text = re.sub(r'<date start="(\d{4}-\d{2}-\d{2})"\s*/>', r"\1", text)
        for tag, delimiter in (("b", "**"), ("i", "*"), ("s", "~~")):
            text = re.sub(
                rf"<{tag}>(.*?)</{tag}>",
                lambda match: delimiter + match.group(1) + delimiter, text,
            )
        text = re.sub(
            r"<code>(.*?)</code>",
            lambda match: "`" * (max((len(run) for run in re.findall(r"`+", match.group(1))), default=0) + 1)
            + html.unescape(match.group(1))
            + "`" * (max((len(run) for run in re.findall(r"`+", match.group(1))), default=0) + 1),
            text,
        )

        def link(match):
            label, target = match.groups()
            prefix = "https://github.com/ijpq/architecture_riscv/blob/main/"
            if not target.startswith(prefix):
                return match.group(0)
            parsed = urlsplit(target[len(prefix):])
            path = posixpath.relpath(unquote(parsed.path), posixpath.dirname(relative))
            suffix = ("?" + parsed.query if parsed.query else "") + (
                "#" + parsed.fragment if parsed.fragment else ""
            )
            return f"[{label}]({path}{suffix})"

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
        prose = re.sub(r"(`+).*?\1", "", text)
        if re.search(r"</?[A-Za-z][\w-]*(?:\s[^>]*)?/?>", prose):
            raise ValueError("Rich Notion blocks need manual conversion; saved remote snapshot")
        return text

    # The Notion serializer names plain-text code blocks 'txt'.
    body = re.sub(r"^(`{3,})txt\s*$", r"\1text", body, flags=re.MULTILINE)
    return transform_prose(body, convert)


def page_content(page):
    if page.get("truncated") or page.get("unknown_block_count") or page.get("unknown_block_ids"):
        raise ValueError("Notion fetch omitted content; refusing to synchronize an incomplete page")
    text = page.get("text", "")
    start, end = text.find("<content>"), text.rfind("</content>")
    if start < 0 or end < start or not isinstance(page.get("title"), str):
        raise ValueError("Notion response has no complete page content")
    return page["title"], canonical(text[start + len("<content>"):end])


def remote_digest(title, body):
    return digest(title + "\n" + canonical(body))


def choose_action(local_hash, remote_hash, baseline):
    if baseline is None:
        return "uninitialized"
    local_changed = local_hash != baseline["local"]
    remote_changed = remote_hash != baseline["remote"]
    if local_changed and remote_changed:
        return "conflict"
    if local_changed:
        return "push"
    if remote_changed:
        return "pull"
    return "unchanged"


def content_updates(old_body, new_source_body, relative):
    """Match canonical lines, but replace the exact raw Notion fragments."""
    import difflib

    old_lines = canonical(old_body).splitlines()
    plain_lines = markdown_body(old_body, relative).splitlines()
    new_lines = canonical(new_source_body).splitlines()
    rendered = render_body(new_source_body, relative).splitlines()
    if len(old_lines) != len(plain_lines) or len(new_lines) != len(rendered):
        raise ValueError("Conversion changed line structure; manual merge required")
    groups = list(difflib.SequenceMatcher(None, plain_lines, new_lines, autojunk=False).get_grouped_opcodes(2))
    patches = []
    for group in groups:
        first, last = group[0], group[-1]
        a, b, c, d = first[1], last[2], first[3], last[4]
        old = "\n".join(old_lines[a:b])
        if not old or old_body.count(old) != 1:
            # Uniqueness can require the whole managed note. No other pages/blocks are targeted.
            return [{"old_str": old_body.strip(), "new_str": "\n".join(rendered)}]
        patches.append({"old_str": old, "new_str": "\n".join(rendered[c:d])})
    return list(reversed(patches))


def snapshot(relative, source, title, body):
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    folder = LOCAL / "conflicts" / (Path(relative).stem + "-" + stamp)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "local.md").write_text(source)
    (folder / "notion.raw.md").write_text("# " + title + "\n\n" + body)
    try:
        (folder / "notion.md").write_text(
            "# " + title + "\n\n" + markdown_body(body, relative)
        )
    except ValueError:
        pass
    return folder


def sync_mapping(client, mapping, baseline, operation):
    relative = mapping["path"]
    path = (ROOT / relative).resolve()
    if not path.is_relative_to((ROOT / "notes").resolve()) or path.suffix != ".md":
        raise ValueError("Only explicitly mapped Markdown files under notes/ may be synchronized")
    source = canonical(path.read_text())
    page = client.call("notion-fetch", {"id": mapping["page_id"]})
    title, body = page_content(page)
    local_hash, remote_hash = digest(source), remote_digest(title, body)
    action = choose_action(local_hash, remote_hash, baseline)
    print(f"{relative}: {action}")
    if operation == "status":
        return baseline
    if action == "uninitialized":
        if operation != "init":
            raise ValueError("Run init after reviewing both copies; no baseline exists")
        expected = "# " + title + "\n\n" + markdown_body(body, relative)
        if canonical(expected) != source:
            saved = snapshot(relative, source, title, body)
            raise ValueError(f"Initial copies differ; review {saved}")
    elif action == "conflict":
        try:
            reconciled = canonical("# " + title + "\n\n" + markdown_body(body, relative)) == source
        except ValueError:
            reconciled = False
        if reconciled:
            print(f"{relative}: copies already reconciled; accepting matching content")
            return {"local": local_hash, "remote": remote_hash}
        saved = snapshot(relative, source, title, body)
        raise ValueError(f"Both copies changed; preserved versions in {saved}")
    elif action == "push":
        new_title, new_body = split_note(source)
        patches = content_updates(body, new_body, relative)
        # Re-read immediately before writing so a detected remote edit is never overwritten.
        check = client.call("notion-fetch", {"id": mapping["page_id"]})
        if remote_digest(*page_content(check)) != remote_hash:
            raise ValueError("Notion changed during sync; retry after reviewing both copies")
        if new_title != title:
            client.call("notion-update-page", {
                "page_id": mapping["page_id"], "command": "update_properties",
                "properties": {"title": new_title},
            })
        if patches:
            result = client.call("notion-update-page", {
                "page_id": mapping["page_id"], "command": "update_content",
                "content_updates": patches,
            })
            if result.get("warnings"):
                raise ValueError("Notion returned warnings; inspect the page before accepting a baseline")
        title, body = page_content(client.call("notion-fetch", {"id": mapping["page_id"]}))
        if canonical("# " + title + "\n\n" + markdown_body(body, relative)) != source:
            raise ValueError("Notion readback differs; no new baseline accepted")
    elif action == "pull":
        try:
            updated = canonical("# " + title + "\n\n" + markdown_body(body, relative))
        except ValueError:
            saved = snapshot(relative, source, title, body)
            raise ValueError(f"Notion uses unsupported rich content; preserved it in {saved}")
        if canonical(path.read_text()) != source:
            raise ValueError("Local note changed during sync; no overwrite performed")
        atomic_write(path, updated)
        source = updated
    return {"local": digest(source), "remote": remote_digest(title, body)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("status", "init", "sync"), nargs="?", default="sync")
    parser.add_argument("--scheduled", action="store_true", help="skip cleanly if no live local runtime")
    args = parser.parse_args()
    LOCAL.mkdir(parents=True, exist_ok=True)
    with (LOCAL / "sync.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        config = json.loads(CONFIG.read_text())
        if config.get("version") != 1:
            raise ValueError("Unsupported sync configuration version")
        state_path = LOCAL / "state.json"
        state = json.loads(state_path.read_text()) if state_path.exists() else {"notes": {}}
        try:
            client = Notion()
        except RuntimeError as error:
            if args.scheduled:
                print("SKIPPED:", error)
                return
            raise
        for mapping in config["notes"]:
            key = mapping["path"] + ":" + mapping["page_id"]
            baseline = state["notes"].get(key)
            updated = sync_mapping(client, mapping, baseline, args.operation)
            if args.operation != "status":
                state["notes"][key] = updated
                state["last_success_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
                atomic_write(state_path, json.dumps(state, indent=2) + "\n")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        print("ERROR:", error, file=__import__("sys").stderr)
        raise SystemExit(1)
