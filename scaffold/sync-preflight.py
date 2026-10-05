#!/usr/bin/env python3
"""Validate sync destinations and render project-owned policy before writes."""

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


def refuse(message):
    raise ValueError(message)


def contained(root, target):
    return os.path.commonpath((root, target)) == root


def destination(root, value):
    target = os.path.abspath(root + "/" + value)
    resolved_root = os.path.realpath(root)
    resolved = os.path.realpath(target)
    if (os.path.isabs(value) or not contained(root, target)
            or not contained(resolved_root, resolved)):
        refuse("Refusing destination outside the repository: " + value)
    workflow = root + "/.github/workflows"
    for normalize in (os.path.abspath, os.path.realpath):
        path, protected = normalize(target), normalize(workflow)
        if os.path.commonpath((path, protected)) in (path, protected):
            refuse("Refusing workflow destination or ancestor: " + value)
    return target


def mappings(root, scaffold, name):
    manifest = scaffold / name
    if not manifest.is_file():
        return []
    result = []
    for line in manifest.read_text().splitlines():
        entry = line.strip(" ")
        if not entry or entry.startswith("#"):
            continue
        if entry == "AGENTS.md managed-section" and name == "manifest.txt":
            continue
        if " -> " not in entry:
            refuse("Refusing invalid manifest entry: " + entry)
        source = entry.split(" -> ", 1)[0]
        target = destination(root, entry.rsplit(" -> ", 1)[1])
        result.append((source, target))
    return result


def dirty_paths(root):
    commands = (
        ("diff", "--name-only", "--no-renames", "-z"),
        ("diff", "--cached", "--name-only", "--no-renames", "-z"),
        ("ls-files", "--others", "--exclude-standard", "-z"),
        ("ls-files", "--others", "--ignored", "--exclude-standard", "-z"),
    )
    paths = set()
    for args in commands:
        output = subprocess.check_output(("git", "-C", root, *args))
        paths.update(os.fsdecode(path) for path in output.split(b"\0") if path)
    return paths


def protect_uncommitted(root, targets):
    # Compare both lexical and resolved paths, including dirty parent symlinks.
    # A file mapping owns only that file; a recursive mapping owns descendants.
    for relative in dirty_paths(root):
        dirty = root + "/" + relative
        for target in targets:
            for normalize in (os.path.abspath, os.path.realpath):
                path, managed = normalize(dirty), normalize(target)
                if os.path.commonpath((path, managed)) in (path, managed):
                    refuse("Refusing uncommitted sync destination: " + relative)


def version_header(source):
    """Return the first canonical header marker, excluding fences/body sections."""
    offset = 0
    fence = None
    for line in source.splitlines(keepends=True):
        content = line.rstrip(b"\r\n")
        match = re.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", content)
        if fence:
            if (match and match[1][:1] == fence[:1]
                    and len(match[1]) >= len(fence) and not match[2].strip()):
                fence = None
        elif match:
            fence = match[1]
        elif re.match(rb"^##[ \t]", content):
            break
        elif content.startswith(b"**Template version:"):
            marker = re.fullmatch(rb"\*\*Template version: ([0-9]+\.[0-9]+\.[0-9]+)\*\*",
                                  content)
            if not marker:
                refuse("Invalid canonical template version marker")
            return offset, offset + len(content), marker[1].decode()
        offset += len(line)
    refuse("Missing canonical header template version marker")


def render_policy(root, temporary, version):
    policy = Path(root) / "records/REPO.md"
    if not policy.exists():
        return
    source = policy.read_bytes()
    start, end, _ = version_header(source)
    replacement = f"**Template version: {version}**".encode()
    (temporary / "repo-version.md").write_bytes(source[:start] + replacement + source[end:])


def render_agents(root, scaffold, temporary):
    agents = Path(root) / "AGENTS.md"
    if not agents.exists():
        return
    source = (scaffold / "AGENTS.md").read_bytes()
    current = agents.read_bytes()
    end = b"<!-- template-managed:end -->"
    legacy_tail = b"## Repo-Specific Rules"
    if end not in source:
        refuse("scaffold AGENTS.md is missing the template-managed:end marker")
    managed = source[:source.index(end) + len(end)]
    if end in current:
        tail = current[current.index(end) + len(end):]
    elif legacy_tail in current:
        tail = b"\n\n" + current[current.index(legacy_tail):]
    elif b"## Code Review Rules" in current:
        start = current.index(b"## Code Review Rules")
        next_section = current.find(b"\n## ", start + 1)
        tail = current[next_section:] if next_section >= 0 else b""
    else:
        refuse("AGENTS.md has no template boundary; refusing sync")
    output = temporary / "agents-merged.md"
    output.write_bytes(managed + tail)
    shutil.copymode(agents, output)


def main():
    root, scaffold, temporary, version = sys.argv[1:5]
    root = os.path.abspath(root)
    scaffold, temporary = Path(scaffold), Path(temporary)
    render_only = sys.argv[5:] == ["--render-only"]
    if sys.argv[5:] and not render_only:
        refuse("Invalid preflight arguments")
    agents = destination(root, "AGENTS.md")
    policy = destination(root, "records/REPO.md")
    if not render_only:
        managed = mappings(root, scaffold, "manifest.txt")
        mappings(root, scaffold, "seed-manifest-v2.txt")
        protect_uncommitted(root, [target for _, target in managed] + [agents, policy])
    render_agents(root, scaffold, temporary)
    render_policy(root, temporary, version)
    (temporary / "preflight-ready").touch()


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
