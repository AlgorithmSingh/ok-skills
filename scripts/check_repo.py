#!/usr/bin/env python3
"""Check the public working tree, including untracked deliverables, using Git and Python."""
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
STORE = runpy.run_path(str(ROOT / "extract-session-details/scripts/check_store.py"))
PRIVATE = re.compile(r"/(?:Users|home)/|[~]/|fleet[-]sandbox")
REFERENCE = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")


def skills_frontmatter(text):
    """Read the two required strings in the plain, quoted or block YAML style."""
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    header = lines[1:lines.index("---", 1)]
    fields = {}
    for i, line in enumerate(header):
        key, sep, value = line.partition(":")
        if line and not line[0].isspace() and not line.startswith("#") and not sep:
            return {}
        if key not in ("name", "description") or not sep:
            continue
        if key in fields or not value.startswith(" "):
            return {}
        value = value.strip()
        if re.fullmatch(r"[|>][-+]?", value):
            block = []
            for part in header[i + 1:]:
                if part and not part.startswith(" "):
                    break
                block.append(part.strip())
            value = " ".join(block).strip()
        elif value.startswith('"'):
            try:
                value = json.loads(value)
            except ValueError:
                return {}
        elif value.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                return {}
            value = value[1:-1].replace("''", "'")
        elif (not value or value[0] in "[]{}&*!|>@`%#" or ": " in value
              or re.match(r"[-?:](?:\s|$)", value)):
            return {}
        else:
            value = re.split(r"\s+#", value)[0].strip()
        if not isinstance(value, str) or not value.strip():
            return {}
        fields[key] = value
    return fields


def markdown_targets(text):
    lines = [line for _, line in STORE["prose_lines"](text)]
    for match in STORE["LINK_RE"].finditer("\n".join(lines)):
        yield match[1]
    for line in lines:
        match = REFERENCE.match(line)
        if match:
            yield match[1]


def markdown_anchors(text):
    """Collect ATX heading slugs and explicit HTML anchors in shipped Markdown."""
    anchors = set()
    for _, line in STORE["unfenced_lines"](text):
        anchors.update(re.findall(r'<(?:a|span)\b[^>]*\b(?:id|name)=["\']([^"\']+)', line))
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if heading:
            base = re.sub(r"[^\w -]", "", heading[1].lower()).replace(" ", "-")
            slug = base
            suffix = 0
            while slug in anchors:
                suffix += 1
                slug = f"{base}-{suffix}"
            anchors.add(slug)
    return anchors


def check(root=ROOT):
    names = subprocess.check_output(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=root)
    paths = {Path(os.fsdecode(p)) for p in names.split(b"\0") if p}
    errors = []
    catalog = set()
    anchors = {}
    linked = set()
    for path in sorted(paths):
        file = root / path
        if not file.exists():  # Deleted files will not ship with the working tree.
            continue
        if root not in file.resolve().parents:
            errors.append(f"{path} points outside repository")
            continue
        data = file.read_bytes()
        text = data.decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if path == Path("AGENTS.md") and line.startswith("- Never commit machine-local paths such as "):
                line = re.sub(r"(?:/(?:Users|home)/<name>/|[~]/)\.\.\.", "", line)
            if PRIVATE.search(line):
                errors.append(f"{path}:{i} contains a private path or host name")
        if path.name == "SKILL.md":
            fields = skills_frontmatter(text)
            if not fields.get("name") or not fields.get("description"):
                errors.append(f"{path} needs column-zero name and description strings")
        if ((len(path.parts) == 2 and path.name in ("SKILL.md", "PROMPT.md"))
                or (len(path.parts) == 2 and path.parts[0].endswith("-rules") and path.suffix == ".md")
                or (path.parent == Path("docs/essays") and path.suffix == ".md" and path.name != "index.md")):
            catalog.add(path)
        if path.suffix.lower() not in (".md", ".markdown", ".txt"):
            continue
        for target in markdown_targets(text):
            if target.lower().startswith("file:"):
                errors.append(f"{path}: local file URI")
                continue
            dest, fragment, problem = STORE["resolve_link"](root, file, target)
            if target.startswith("#"):
                dest, fragment = file, target[1:]
            if problem or (dest and not dest.exists()):
                errors.append(f"{path}: unresolved repository link {target!r}")
            elif dest:
                member = dest.relative_to(root)
                if dest.is_file() and member not in paths:
                    errors.append(f"{path}: link to excluded file {target!r}")
                if fragment and dest.is_file():
                    lines = STORE["LINE_ANCHOR_RE"].fullmatch(fragment)
                    if lines:
                        start, end = int(lines[1]), int(lines[2] or lines[1])
                        if not 1 <= start <= end <= len(dest.read_bytes().splitlines()):
                            errors.append(f"{path}: invalid line citation {target!r}")
                    elif dest.suffix.lower() == ".md":
                        if dest not in anchors:
                            anchors[dest] = markdown_anchors(dest.read_text(encoding="utf-8"))
                        if unquote(fragment) not in anchors[dest]:
                            errors.append(f"{path}: unknown heading {target!r}")
                if path == Path("README.md"):
                    linked.add(member)
    errors.extend(f"README.md is missing {p}" for p in sorted(catalog - linked))
    for folder in ("references", "scripts"):
        dirs = [root / ("extract-" + name) / folder for name in ("session-details", "meeting-notes")]
        members = {p.relative_to(d) for d in dirs for p in d.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts}
        for member in sorted(members):
            left, right = (d / member for d in dirs)
            if not left.is_file() or not right.is_file() or left.read_bytes() != right.read_bytes():
                errors.append(f"extraction skills differ at {folder}/{member}")
    return errors


if __name__ == "__main__":
    findings = check()
    for finding in findings:
        print(finding)
    print(f"{len(findings)} errors, 0 warnings")
    sys.exit(bool(findings))
