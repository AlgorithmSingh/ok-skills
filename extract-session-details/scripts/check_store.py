#!/usr/bin/env python3
"""Check the extraction store under docs/ and optionally export it as JSON Lines.

Usage:
    python3 -I check_store.py --root <repository root> [--export DIR] [--all]

Checks, each tied to a failure seen in earlier runs or to a consistency the
registry and ledger create:

- links: every relative Markdown link in docs/, outside code, resolves to an
  existing file, and a #L12 or #L12-L30 anchor is within the target's lines.
- placeholders: no unexpanded template token from the skills' references
  outside code in docs/knowledge/ and docs/extractions/.
- registry: page front matter id matches its path, every page has a registry
  row, every registry row has a page, merge and split targets exist, subject
  page item status lines match the status vocabulary, subject type index
  descriptions match page front matter descriptions, and no name is shared by
  two active subjects (a warning).
- ledger: evidence links exist, subject IDs exist, dates and Change values are
  valid, and page History rows, the holding page and ledger Subjects agree in
  both directions.

A missing docs/knowledge/ is not an error. Exit status is 1 when any error is
found, otherwise 0. Standard library only.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

TYPES = ("project", "service", "feature", "procedure", "decision", "problem")

CHANGES = frozenset((
    "added", "corroborated", "revised", "superseded", "conflict", "resolved",
    "status", "corrected", "withdrawn", "moved", "evidence removed",
))

# Template tokens used in references/store.md, references/knowledge.md and
# docs/extraction-prompt.md. tests/extraction-store/test_check_store.py checks
# that this list covers every token in those files.
PLACEHOLDERS = frozenset((
    "<the source's own title, plus its version if it states one>",
    "<one sentence: what kind of source it is, its date, and what it covers>",
    "<repository-relative path>",
    "<64 hex characters>",
    "<title>",
    "<the point, stated as a sentence>",
    "<relative link to the source>",
    "<who>",
    "<status>",
    "<every specific, stated once>",
    "<exact file or source name>",
    "<what the source says about it>",
    "<record heading>",
    "<name as the source states it>",
    "<feature, service, project, procedure, decision or recurring problem>",
    "<hash>",
    "<name>",
    "<link>",
    "<part>",
    "<type>",
    "<slug>",
    "<id>",
    "<sha12>",
    "<date>",
    "<reason>",
    "<current name>",
    "<one sentence>",
    "<ISO 8601 with offset, last update>",
    "<name as a source uses it>",
    "<broader subject id>",
    "<latest event date applied>",
    "<event date>",
    "<evidence links>",
    "<link to source>",
    "<link to page>",
    "<link to evidence document>",
    "<source label>",
    "<restriction as the source states it>",
    "<intervention, stated as a sentence>",
    "<why, as the source gives it>",
    "<as stated before the outcome was known, with its link>",
    "<result, with its link, and exactly what it covers>",
    "<repository, service, environment, version, model, dataset, date>",
    "<kept, revised, replaced or reverted, with link and date>",
    "<the question, stated as a sentence>",
    "<side>",
    "<who, with link, or \"no one in the evidence\">",
    "<current item heading>",
    "<change>",
    "<what changed>",
    "<ingested date>",
    "<evidence links or \"owner instruction\">",
    "<date basis>",
    "<stage>",
    "<subject ids>",
    "<subject ids or names>",
    "<path>",
    "<skill directory>",
    "<repository root>",
    "<description>",
    "<source path>",
    "<source folder>",
    "<paths of the sources>",
    "<where the files go, or the defaults below>",
    "<coding, enterprise automation, SRE, assistant; their tasks if known>",
))

ID_RE = re.compile(r"^(%s)/[a-z0-9]+(?:-[a-z0-9]+)*$" % "|".join(TYPES))
SHA12_RE = re.compile(r"`([0-9a-f]{12})`")
DATE_RE = re.compile(r"^(?:\d{4}(?:-\d{2}(?:-\d{2})?)?|unknown)$")
DAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STAGE_RE = re.compile(
    r"^(?:listed|compressed|extracted|routed|superseded by [0-9a-f]{12}"
    r"|removed \d{4}-\d{2}-\d{2}|skipped: \S.*)$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
TOKEN_RE = re.compile(r"<[^<>\n]+>")
LINK_RE = re.compile(
    r"!?\[(?:[^\[\]\\]|\\.|\[[^\[\]]*\])*\]"
    r"\(\s*(<[^<>\n]*>|(?:[^()\s\\]|\\.|\((?:[^()\s\\]|\\.)*\))*)"
    r"(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^()]*\)))?\s*\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
LINE_ANCHOR_RE = re.compile(r"^L(\d+)(?:-L(\d+))?$")
ITEM_STATUS_RE = re.compile(
    r"^(?:"
    r"(?:proposed|withdrawn|deferred|open|observed|reported|second-hand"
    r"|second-hand and reported|requested|submitted|approved|rejected"
    r"|completed|verified|assigned|accepted|superseded)"
    r"|superseded \(inferred from date order\)"
    r"|(?:proposed|decided|accepted|rejected|stated|requested|withdrawn"
    r"|deferred|observed|reported|submitted|approved|completed|verified"
    r"|assigned|claimed) by [^;]+"
    r"|(?:second-hand|requested|submitted|approved|rejected|completed"
    r"|verified|assigned|accepted), reported(?: by [^;]+)?"
    r"|proposed; [^;]+ replied .+"
    r")$"
)
INDEX_ENTRY_RE = re.compile(r"^\s*-\s*\[([^\]]+)\]\(([^)]+)\):\s*(.+)$")

REGISTRY_HEADER = ["ID", "Type", "Title", "Aliases", "Scope", "Status", "Page"]
LEDGER_HEADER = ["Source", "sha256 (first 12)", "Event date", "Date basis",
                 "Ingested", "Stage", "Evidence", "Subjects"]
HISTORY_HEADER = ["Event date", "Source", "Lines", "Change", "What changed",
                  "Ingested"]
HOLDING_HEADER = ["Added", "Source", "Lines", "Record", "Candidate subjects",
                  "Why unassigned"]


class Report:
    def __init__(self):
        self.sections = {}
        self.order = []
        self.notes = []

    def _section(self, name):
        if name not in self.sections:
            self.sections[name] = {"errors": [], "warnings": [], "checked": 0}
            self.order.append(name)
        return self.sections[name]

    def error(self, section, where, message):
        self._section(section)["errors"].append("%s: %s" % (where, message))

    def warn(self, section, where, message):
        self._section(section)["warnings"].append("%s: %s" % (where, message))

    def count(self, section, n=1):
        self._section(section)["checked"] += n

    def note(self, message):
        self.notes.append(message)

    @property
    def n_errors(self):
        return sum(len(s["errors"]) for s in self.sections.values())

    @property
    def n_warnings(self):
        return sum(len(s["warnings"]) for s in self.sections.values())

    def render(self, show_all=False, limit=20):
        out = []
        for name in self.order:
            s = self.sections[name]
            out.append("%s: %d checked, %d errors, %d warnings" % (
                name, s["checked"], len(s["errors"]), len(s["warnings"])))
            for kind, items in (("error", s["errors"]),
                                ("warning", s["warnings"])):
                shown = items if show_all else items[:limit]
                for item in shown:
                    out.append("  %s %s" % (kind, item))
                if len(items) > len(shown):
                    out.append("  ... %d more %ss (use --all)" % (
                        len(items) - len(shown), kind))
        out.extend(self.notes)
        out.append("%d errors, %d warnings" % (self.n_errors, self.n_warnings))
        return "\n".join(out)


# ---------------------------------------------------------------- parsing

def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")


def strip_code_spans(line):
    """Replace inline code spans with a space; keep unmatched backticks."""
    out = []
    i, n = 0, len(line)
    while i < n:
        if line[i] != "`":
            out.append(line[i])
            i += 1
            continue
        j = i
        while j < n and line[j] == "`":
            j += 1
        run = line[i:j]
        k, found = j, -1
        while True:
            k = line.find(run, k)
            if k == -1:
                break
            end = k + len(run)
            if end < n and line[end] == "`":
                while end < n and line[end] == "`":
                    end += 1
                k = end
                continue
            found = k
            break
        if found == -1:
            out.append(run)
            i = j
        else:
            out.append(" ")
            i = found + len(run)
    return "".join(out)


def unfenced_lines(text):
    """Yield (line number, line) for lines outside fenced code blocks."""
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                continue
            yield number, line
        else:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) \
                    and line.strip() == m.group(1):
                fence = None


def prose_lines(text):
    """Yield (line number, line without code) outside fences and code spans."""
    for number, line in unfenced_lines(text):
        yield number, strip_code_spans(line)


def split_row(line):
    """Split a Markdown table row into cells, honoring code spans and \\|."""
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    cells, cur = [], []
    i, n, code = 0, len(s), None
    while i < n:
        c = s[i]
        if c == "\\" and i + 1 < n and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if c == "`":
            j = i
            while j < n and s[j] == "`":
                j += 1
            run = s[i:j]
            if code is None:
                code = run
            elif run == code:
                code = None
            cur.append(run)
            i = j
            continue
        if c == "|" and code is None:
            cells.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    cells.append("".join(cur).strip())
    return cells


def find_tables(text, header):
    """Return the rows of every table whose header equals header.

    Each row is (line number, cells)."""
    lines = list(unfenced_lines(text))
    tables = []
    i = 0
    while i < len(lines):
        number, line = lines[i]
        if line.lstrip().startswith("|") and split_row(line) == header \
                and i + 1 < len(lines) \
                and re.match(r"^\s*\|?\s*:?-{3,}", lines[i + 1][1]):
            rows = []
            j = i + 2
            while j < len(lines) and lines[j][1].lstrip().startswith("|") \
                    and lines[j][0] == lines[j - 1][0] + 1:
                cells = split_row(lines[j][1])
                cells += [""] * (len(header) - len(cells))
                rows.append((lines[j][0], cells[:len(header)]))
                j += 1
            tables.append(rows)
            i = j
        else:
            i += 1
    return tables


def parse_scalar(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        if value[0] == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return value


def parse_inline_list(value):
    inner = value.strip()[1:-1]
    items = re.findall(r'"((?:[^"\\]|\\.)*)"|\'([^\']*)\'|([^,]+)', inner)
    out = []
    for dq, sq, bare in items:
        item = dq.replace('\\"', '"') if dq else (sq or bare.strip())
        if item:
            out.append(item)
    return out


def front_matter(text):
    """Parse simple YAML front matter: scalars and lists. None if absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data, key = {}, None
    for line in lines[1:]:
        if line.strip() in ("---", "..."):
            return data
        if re.match(r"^\s+-\s", line) and key is not None:
            if not isinstance(data.get(key), list):
                data[key] = []
            data[key].append(parse_scalar(line.strip()[1:]))
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2)
            if value.startswith("[") and value.rstrip().endswith("]"):
                data[key] = parse_inline_list(value.rstrip())
            elif value == "":
                data[key] = ""
            else:
                data[key] = parse_scalar(value)
    return None


def link_targets(text):
    return [m.group(1) for m in LINK_RE.finditer(text)]


def plain(cell):
    """A table cell with code-span backticks removed."""
    return cell.replace("`", "").strip()


def split_list(cell, sep):
    value = plain(cell)
    if value in ("", "-"):
        return []
    return [v.strip() for v in value.split(sep) if v.strip()]


def normalize_name(name):
    name = re.sub(r"[^\w\s]|_", " ", name.lower())
    return " ".join(name.split())


# ---------------------------------------------------------------- links

class Files:
    def __init__(self, root):
        self.root = root
        self._lines = {}

    def line_count(self, path):
        if path not in self._lines:
            data = path.read_bytes()
            n = data.count(b"\n")
            if data and not data.endswith(b"\n"):
                n += 1
            self._lines[path] = n
        return self._lines[path]


def resolve_link(root, source_file, target):
    """Return (path or None, fragment, problem) for a relative link target."""
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    if not target or target.startswith("#") or SCHEME_RE.match(target):
        return None, None, None
    path_part, _, fragment = target.partition("#")
    path_part = path_part.partition("?")[0]
    path_part = unquote(path_part)
    if not path_part:
        return None, None, None
    if path_part.startswith("/"):
        joined = os.path.join(str(root), path_part.lstrip("/"))
    else:
        joined = os.path.join(str(source_file.parent), path_part)
    normal = Path(os.path.normpath(joined))
    try:
        normal.relative_to(root)
    except ValueError:
        return normal, fragment, "points outside the repository"
    return normal, fragment, None


def check_link(report, files, root, source_file, number, target, section):
    path, fragment, problem = resolve_link(root, source_file, target)
    if path is None and problem is None:
        return None
    where = "%s:%d" % (rel(root, source_file), number)
    report.count(section)
    if problem:
        report.error(section, where, "link %r %s" % (target, problem))
        return None
    if not path.exists():
        report.error(section, where, "link %r: no such file" % target)
        return None
    if fragment:
        m = LINE_ANCHOR_RE.match(fragment)
        if m and path.is_file():
            start = int(m.group(1))
            end = int(m.group(2) or start)
            total = files.line_count(path)
            if start < 1 or end < start or end > total:
                report.error(section, where, "link %r: lines %d-%d outside "
                             "1-%d" % (target, start, end, total))
    return path


def rel(root, path):
    try:
        return str(Path(path).relative_to(root))
    except ValueError:
        return str(path)


def markdown_files(directory):
    out = []
    for dirpath, dirnames, filenames in os.walk(directory):
        dirnames.sort()
        for name in sorted(filenames):
            if name.endswith(".md"):
                out.append(Path(dirpath) / name)
    return out


def check_links(report, files, root, docs):
    for path in markdown_files(docs):
        text = read_text(path)
        for number, line in prose_lines(text):
            for target in link_targets(line):
                check_link(report, files, root, path, number, target, "links")
    report.count("links", 0)


def check_placeholders(report, root, docs):
    report.count("placeholders", 0)
    for sub in ("knowledge", "extractions"):
        directory = docs / sub
        if not directory.is_dir():
            continue
        for path in markdown_files(directory):
            report.count("placeholders")
            text = read_text(path)
            for number, line in prose_lines(text):
                for token in TOKEN_RE.findall(line):
                    if token in PLACEHOLDERS:
                        report.error("placeholders", "%s:%d" % (
                            rel(root, path), number),
                            "unexpanded template token %s" % token)


# ---------------------------------------------------------------- store

def cell_links(cell):
    return link_targets(strip_code_spans(cell))


def cell_sha(cell):
    m = SHA12_RE.search(cell)
    return m.group(1) if m else None


def repo_path(root, base_file, target):
    path, fragment, problem = resolve_link(root, base_file, target)
    if path is None or problem:
        return None
    out = rel(root, path)
    return out + ("#" + fragment if fragment else "")


def load_store(report, files, root, knowledge):
    """Parse registry, ledger, holding page and subject pages."""
    store = {"registry": {}, "ledger": [], "holding": [], "pages": {}}
    registry_file = knowledge / "subjects.md"
    ledger_file = knowledge / "sources.md"
    holding_file = knowledge / "unassigned.md"
    store["files"] = (registry_file, ledger_file, holding_file)

    if registry_file.is_file():
        tables = find_tables(read_text(registry_file), REGISTRY_HEADER)
        if not tables:
            report.error("registry", rel(root, registry_file),
                         "no table with columns %s" % " | ".join(REGISTRY_HEADER))
        for rows in tables:
            for number, cells in rows:
                sid = plain(cells[0])
                where = "%s:%d" % (rel(root, registry_file), number)
                if sid in store["registry"]:
                    report.error("registry", where, "duplicate ID %s" % sid)
                    continue
                links = cell_links(cells[6])
                store["registry"][sid] = {
                    "line": number,
                    "type": plain(cells[1]),
                    "title": cells[2].strip(),
                    "aliases": split_list(cells[3], ";"),
                    "scope": split_list(cells[4], ","),
                    "status": plain(cells[5]),
                    "page_target": links[0] if links else None,
                    "where": where,
                }

    if ledger_file.is_file():
        tables = find_tables(read_text(ledger_file), LEDGER_HEADER)
        if not tables:
            report.error("ledger", rel(root, ledger_file),
                         "no table with columns %s" % " | ".join(LEDGER_HEADER))
        for rows in tables:
            for number, cells in rows:
                links = cell_links(cells[6])
                store["ledger"].append({
                    "line": number,
                    "where": "%s:%d" % (rel(root, ledger_file), number),
                    "source": [p.strip() for p in
                               re.findall(r"`([^`]+)`", cells[0])]
                    or split_list(cells[0], ";"),
                    "sha": plain(cells[1]),
                    "event_date": plain(cells[2]),
                    "date_basis": cells[3].strip(),
                    "ingested": plain(cells[4]),
                    "stage": plain(cells[5]),
                    "evidence_cell": cells[6].strip(),
                    "evidence_target": links[0] if links else None,
                    "subjects": split_list(cells[7], ","),
                })

    if holding_file.is_file():
        tables = find_tables(read_text(holding_file), HOLDING_HEADER)
        if not tables:
            report.error("ledger", rel(root, holding_file),
                         "no table with columns %s" % " | ".join(HOLDING_HEADER))
        for rows in tables:
            for number, cells in rows:
                store["holding"].append({
                    "where": "%s:%d" % (rel(root, holding_file), number),
                    "sha": cell_sha(cells[1]),
                    "added": plain(cells[0]),
                })

    for kind in TYPES:
        folder = knowledge / (kind + "s")
        if not folder.is_dir():
            continue
        for path in sorted(folder.glob("*.md")):
            if path.name == "index.md":
                continue
            text = read_text(path)
            fm = front_matter(text) or {}
            expected = "%s/%s" % (kind, path.stem)
            history = []
            for rows in find_tables(text, HISTORY_HEADER):
                for number, cells in rows:
                    history.append({"line": number, "cells": cells})
            items = []
            ulines = list(unfenced_lines(text))
            for idx, (number, line) in enumerate(ulines):
                if line.startswith("#### "):
                    if idx + 1 < len(ulines):
                        items.append(ulines[idx + 1])
                    else:
                        items.append((number, ""))
            store["pages"][expected] = {
                "path": path, "fm": fm, "history": history, "items": items,
                "has_fm": front_matter(text) is not None,
            }
    return store


def check_registry(report, root, knowledge, store):
    registry, pages = store["registry"], store["pages"]
    registry_file = store["files"][0]
    if pages and not registry_file.is_file():
        report.error("registry", rel(root, knowledge),
                     "subject pages exist but subjects.md is missing")
    for sid, page in sorted(pages.items()):
        where = rel(root, page["path"])
        report.count("registry")
        if not page["has_fm"]:
            report.error("registry", where, "no front matter")
        fm_id = page["fm"].get("id")
        if fm_id != sid:
            report.error("registry", where,
                         "front matter id %r, expected %r" % (fm_id, sid))
        if page["fm"].get("type") not in (None, sid.split("/")[0]) \
                and page["has_fm"]:
            report.error("registry", where, "front matter type %r, expected "
                         "%r" % (page["fm"].get("type"), sid.split("/")[0]))
        if sid not in registry:
            report.error("registry", where, "no registry row for %s" % sid)
        for s_num, s_line in page.get("items", []):
            s_where = "%s:%d" % (where, s_num)
            report.count("registry")
            if " · " not in s_line:
                report.error("registry", s_where,
                             "item heading is not followed by a '<status> · ...' status line")
            else:
                item_status = s_line.split(" · ", 1)[0].strip()
                if not ITEM_STATUS_RE.match(item_status):
                    report.error("registry", s_where,
                                 "unknown item status %r" % item_status)
    for kind in TYPES:
        index_file = knowledge / (kind + "s") / "index.md"
        if not index_file.is_file():
            continue
        for number, line in unfenced_lines(read_text(index_file)):
            m = INDEX_ENTRY_RE.match(line)
            if not m:
                continue
            _, target, desc = m.groups()
            target_path, _, problem = resolve_link(root, index_file, target.strip())
            if target_path is None or problem:
                continue
            sid = "%s/%s" % (kind, target_path.stem)
            page = pages.get(sid)
            if page is not None and page["path"] == target_path:
                report.count("registry")
                fm_desc = page["fm"].get("description", "")
                if desc.strip() != fm_desc:
                    report.error("registry", "%s:%d" % (rel(root, index_file), number),
                                 "index description %r does not match page description %r"
                                 % (desc.strip(), fm_desc))
    names = {}
    for sid, row in sorted(registry.items()):
        where = row["where"]
        report.count("registry")
        if not ID_RE.match(sid):
            report.error("registry", where, "malformed ID %r" % sid)
            continue
        kind, slug = sid.split("/", 1)
        if row["type"] != kind:
            report.error("registry", where, "Type %r does not match ID %s" % (
                row["type"], sid))
        expected = knowledge / (kind + "s") / (slug + ".md")
        if row["page_target"] is None:
            report.error("registry", where, "no page link for %s" % sid)
        else:
            path, _, _ = resolve_link(root, registry_file, row["page_target"])
            if path != expected:
                report.error("registry", where, "page link %r, expected %s" % (
                    row["page_target"], rel(root, expected)))
        if not expected.is_file():
            report.error("registry", where, "page %s does not exist" %
                         rel(root, expected))
        status = row["status"]
        targets = []
        page = pages.get(sid)
        statuses = [status]
        if page and page["fm"].get("status"):
            statuses.append(page["fm"]["status"])
            if page["fm"]["status"] != status:
                report.error("registry", where, "status %r differs from page "
                             "status %r" % (status, page["fm"]["status"]))
        for value in statuses:
            if value == "active":
                continue
            m = re.match(r"^(merged into|split into) (.+)$", value)
            if not m:
                report.error("registry", where, "unknown status %r" % value)
                continue
            targets += [t.strip() for t in m.group(2).split(",") if t.strip()]
        for target in sorted(set(targets)):
            if target not in registry:
                report.error("registry", where,
                             "%s target %s is not in the registry" % (
                                 status.split(" into")[0], target))
        if status == "active":
            for name in [slug.replace("-", " "), row["title"]] + row["aliases"]:
                key = normalize_name(name)
                if key:
                    names.setdefault(key, set()).add(sid)
    for key, ids in sorted(names.items()):
        if len(ids) > 1:
            report.warn("registry", rel(root, registry_file),
                        "name %r is shared by active subjects %s" % (
                            key, ", ".join(sorted(ids))))


def check_ledger(report, root, knowledge, store):
    registry, pages = store["registry"], store["pages"]
    ledger_file = store["files"][1]
    by_sha = {}
    for row in store["ledger"]:
        where = row["where"]
        report.count("ledger")
        sha = row["sha"]
        if not re.match(r"^[0-9a-f]{12}$", sha):
            report.error("ledger", where, "sha256 prefix %r is not 12 lowercase "
                         "hex characters" % sha)
        elif sha in by_sha:
            report.error("ledger", where, "duplicate sha256 prefix %s" % sha)
        else:
            by_sha[sha] = row
        if not DATE_RE.match(row["event_date"]):
            report.error("ledger", where, "Event date %r is not an ISO date or "
                         "unknown" % row["event_date"])
        if not DAY_RE.match(row["ingested"]):
            report.error("ledger", where, "Ingested %r is not YYYY-MM-DD" %
                         row["ingested"])
        if not STAGE_RE.match(row["stage"]):
            report.error("ledger", where, "unknown Stage %r" % row["stage"])
        if row["evidence_target"]:
            path, _, problem = resolve_link(root, ledger_file,
                                            row["evidence_target"])
            if path is None or problem or not path.is_file():
                report.error("ledger", where, "evidence link %r does not "
                             "resolve to a file" % row["evidence_target"])
        elif plain(row["evidence_cell"]) not in ("", "-") and not (
                row["stage"].startswith("superseded by ")
                and "rewritten for " in plain(row["evidence_cell"])):
            report.error("ledger", where, "Evidence is neither a link nor -")
        for sid in row["subjects"]:
            if sid != "unassigned" and sid not in registry:
                report.error("ledger", where, "subject %s is not in the "
                             "registry" % sid)
    if (pages or store["holding"]) and not ledger_file.is_file():
        report.error("ledger", rel(root, knowledge),
                     "subject pages exist but sources.md is missing")

    cited = {}
    for sid, page in sorted(pages.items()):
        for entry in page["history"]:
            cells = entry["cells"]
            where = "%s:%d" % (rel(root, page["path"]), entry["line"])
            report.count("ledger")
            if not DATE_RE.match(plain(cells[0])):
                report.error("ledger", where, "History Event date %r is not an "
                             "ISO date or unknown" % plain(cells[0]))
            if plain(cells[3]) not in CHANGES:
                report.error("ledger", where, "Change %r is not one of: %s" % (
                    plain(cells[3]), ", ".join(sorted(CHANGES))))
            if not DAY_RE.match(plain(cells[5])):
                report.error("ledger", where, "History Ingested %r is not "
                             "YYYY-MM-DD" % plain(cells[5]))
            if plain(cells[1]) == "owner instruction":
                continue
            sha = cell_sha(cells[1])
            if sha is None:
                report.error("ledger", where, "History Source has no `sha12` "
                             "and is not 'owner instruction'")
                continue
            cited.setdefault(sha, set()).add(sid)
            row = by_sha.get(sha)
            if row is None:
                report.error("ledger", where, "source %s is not in the ledger"
                             % sha)
            elif sid not in row["subjects"]:
                report.error("ledger", where, "ledger row for %s does not list "
                             "%s in Subjects" % (sha, sid))
    held = set()
    for entry in store["holding"]:
        report.count("ledger")
        sha = entry["sha"]
        if sha is None:
            report.error("ledger", entry["where"], "holding row Source has no "
                         "`sha12`")
            continue
        held.add(sha)
        row = by_sha.get(sha)
        if row is None:
            report.error("ledger", entry["where"], "source %s is not in the "
                         "ledger" % sha)
        elif "unassigned" not in row["subjects"]:
            report.error("ledger", entry["where"], "ledger row for %s does not "
                         "list unassigned in Subjects" % sha)
    for sha, row in sorted(by_sha.items()):
        for sid in row["subjects"]:
            if sid == "unassigned":
                if sha not in held:
                    report.error("ledger", row["where"], "Subjects lists "
                                 "unassigned but the holding page has no row "
                                 "for %s" % sha)
            elif sid in pages and sid not in cited.get(sha, set()):
                report.error("ledger", row["where"], "Subjects lists %s but its "
                             "History has no row for %s" % (sid, sha))
            elif sid in registry and sid not in pages:
                report.error("ledger", row["where"], "Subjects lists %s but "
                             "its page does not exist" % sid)


# ---------------------------------------------------------------- export

def export(root, knowledge, store, directory):
    directory.mkdir(parents=True, exist_ok=True)
    registry_file, ledger_file, _ = store["files"]
    subjects, sources, history = [], [], []
    for sid, row in sorted(store["registry"].items()):
        page = store["pages"].get(sid, {})
        fm = page.get("fm", {})
        subjects.append({
            "id": sid, "type": row["type"], "title": row["title"],
            "aliases": row["aliases"], "scope": row["scope"],
            "status": row["status"],
            "page": repo_path(root, registry_file, row["page_target"])
            if row["page_target"] else None,
            "description": fm.get("description"),
            "evidence_through": fm.get("evidence_through"),
            "timestamp": fm.get("timestamp"),
        })
    for row in store["ledger"]:
        sources.append({
            "source": row["source"], "sha256_12": row["sha"],
            "event_date": row["event_date"], "date_basis": row["date_basis"],
            "ingested": row["ingested"], "stage": row["stage"],
            "evidence": repo_path(root, ledger_file, row["evidence_target"])
            if row["evidence_target"] else None,
            "subjects": row["subjects"],
        })
    for sid, page in sorted(store["pages"].items()):
        for entry in page["history"]:
            cells = entry["cells"]
            source_links = cell_links(cells[1])
            history.append({
                "subject": sid,
                "event_date": plain(cells[0]),
                "source": re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1",
                                 plain(cells[1])),
                "sha256_12": cell_sha(cells[1]),
                "evidence": repo_path(root, page["path"], source_links[0])
                if source_links else None,
                "lines": [p for p in (repo_path(root, page["path"], t)
                                      for t in cell_links(cells[2])) if p],
                "change": plain(cells[3]),
                "what_changed": cells[4].strip(),
                "ingested": plain(cells[5]),
            })
    for name, records in (("subjects.jsonl", subjects),
                          ("sources.jsonl", sources),
                          ("history.jsonl", history)):
        with open(directory / name, "w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False,
                                        sort_keys=True) + "\n")
    return len(subjects), len(sources), len(history)


# ---------------------------------------------------------------- main

def check(root, export_dir=None):
    root = Path(os.path.abspath(root))
    report = Report()
    docs = root / "docs"
    if not docs.is_dir():
        report.error("links", rel(root, docs), "no docs/ folder under the root")
        return report
    files = Files(root)
    check_links(report, files, root, docs)
    check_placeholders(report, root, docs)
    knowledge = docs / "knowledge"
    if not knowledge.is_dir():
        report.note("knowledge: docs/knowledge/ not present, store checks "
                    "skipped")
        if export_dir is not None:
            n = export(root, knowledge, {"registry": {}, "ledger": [],
                                         "holding": [], "pages": {},
                                         "files": (knowledge / "subjects.md",
                                                   knowledge / "sources.md",
                                                   knowledge / "unassigned.md")},
                       Path(export_dir))
            report.note("export: %d subjects, %d sources, %d history rows to %s"
                        % (n + (export_dir,)))
        return report
    store = load_store(report, files, root, knowledge)
    report.count("registry", 0)
    report.count("ledger", 0)
    check_registry(report, root, knowledge, store)
    check_ledger(report, root, knowledge, store)
    if export_dir is not None:
        n = export(root, knowledge, store, Path(export_dir))
        report.note("export: %d subjects, %d sources, %d history rows to %s"
                    % (n + (export_dir,)))
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Check the extraction store under docs/ and optionally "
                    "export it as JSON Lines.")
    parser.add_argument("--root", required=True,
                        help="repository root that contains docs/")
    parser.add_argument("--export", metavar="DIR",
                        help="write subjects.jsonl, sources.jsonl and "
                             "history.jsonl to DIR")
    parser.add_argument("--all", action="store_true",
                        help="print every finding instead of the first 20 "
                             "per check")
    args = parser.parse_args(argv)
    report = check(args.root, args.export)
    print(report.render(show_all=args.all))
    return 1 if report.n_errors else 0


if __name__ == "__main__":
    sys.exit(main())
