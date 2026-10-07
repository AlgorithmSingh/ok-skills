#!/usr/bin/env python3
"""Render Claude Code, Codex and pi session logs as Markdown transcripts, with credentials redacted.

One file:
  export_transcript.py <out.md> <session.jsonl> [<agent.jsonl> ...] [--agents-only] [--preamble <file>]
                       [--secrets-from <file-or-glob> ...]
  The first log is the main session; each later one is an agent appended under its own heading. With
  --agents-only every log is an agent, labelled from its .meta.json. --preamble inserts a Markdown file first.

A session tree:
  export_transcript.py --tree <plan.json> --out <dir> [--previous <MANIFEST.md>] [--secrets-from <file-or-glob> ...]
  The main session, its workflow runs and subagents, and related tool sessions, laid out as the plan says, plus
  MANIFEST.md. The manifest lists every source log and the file it went to, and records three checks: that each
  prompt, reply, structured result and user answer in a source appears verbatim in that file and every tool call
  has its line (found by a parser separate from the renderer); that every session log written on the machine
  since the plan's start is exported or excluded for a stated reason; and, with --previous, that no source log of
  an earlier export has gone missing.

Prompts (including messages queued while the agent was busy), replies, workflow agents' structured results and the
user's answers to questions are kept verbatim. Every other tool call becomes one line with a short result, and
hidden thinking is dropped. Exact credential values read from the --secrets-from files (env, JSON, YAML, netrc,
git-credentials, SQLite) and key-shaped strings become [REDACTED]; the finished text is scanned again, and nothing
is written if any are left. Exits 1 if a check fails.
"""
import glob
import hashlib
import json
import os
import re
import sqlite3
import sys
from collections import Counter
from datetime import datetime, timezone

REDACTED = "[REDACTED]"
PATTERNS = [
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_\-]{20,}")),
    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("google-key", re.compile(r"\bAIza[0-9A-Za-z_\-]{35}")),
    ("google-oauth", re.compile(r"\bya29\.[0-9A-Za-z_\-]{20,}")),
    ("google-refresh", re.compile(r"(?<![A-Za-z0-9/])1//0[A-Za-z0-9_\-]{20,}")),
    ("openai-refresh", re.compile(r"\brt\.1[A-Za-z0-9._\-]{20,}")),
    ("hf-token", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9\-]{10,}")),
]
# NAME_API_KEY=value, token: value, PGPASSWORD=value, "refresh_token": "value"; the name and separator are kept.
ASSIGNED = re.compile(r"(?i)\b([A-Z0-9_]*(?:API_KEY|SECRET|TOKEN|PASSWORD))(\s*[=:]\s*[\"']?)([A-Za-z0-9_\-./+=]{16,})")
PASSWORD_ASSIGNED = re.compile(r"(?i)\b([A-Za-z0-9_.]*(?:_PASS|PASSWORD|PASSWD))(\s*[=:]\s*[\"']?)"
                               r"([^\s\"'$`{}()\[\],;]{4,})")
JSON_ASSIGNED = re.compile(r"(?i)(\"[A-Za-z0-9_]*(?:api_?key|secret|token|password)\"\s*:\s*\")([^\"\\]{16,})\"")
JSON_PASSWORD = re.compile(r"(?i)(\"[A-Za-z0-9_]*(?:_pass|password|passwd)\"\s*:\s*\")([^\"\\]{4,})\"")
SECRET_NAME = re.compile(r"(?i)(token|secret|passw|api[_-]?key|apikey|access|refresh|account_?id|credential|"
                         r"private[_-]?key|cookie)")

SYSTEM_PREFIXES = ("<task-notification>", "<system-reminder>", "<local-command-stdout>", "<local-command-stderr>",
                   "<bash-stdout>", "<bash-stderr>")
CLAUDE_DROPPED = {"mode", "permission-mode", "atis-latch", "last-prompt", "file-history-delta",
                  "file-history-snapshot", "cost-state", "summary", "custom-title", "tag", "agent-name", "pr-link"}
USER_INPUT_TOOLS = {"AskUserQuestion", "ExitPlanMode"}
USER_REPLY_MARKERS = ("The user doesn't want to proceed", "User has answered your questions", "The user rejected")
CODEX_CONTEXT = ("<environment_context", "<user_instructions", "<recommended_plugins", "<skills_instructions",
                 "<permissions", "<apps_instructions", "<collaboration_mode", "# AGENTS.md instructions",
                 "<user_shell_command", "<INSTRUCTIONS>", "<turn_aborted", "<plugins_instructions", "<personality")
CODEX_DROPPED = {"world_state", "token_usage_record", "turn_context", "inter_agent_communication_metadata"}
CODEX_TOOL_ITEMS = ("function_call", "custom_tool_call", "local_shell_call", "web_search_call")
PI_DROPPED = {"agent_start", "turn_start", "turn_end", "message_start", "message_update", "tool_execution_start",
              "tool_execution_update", "tool_execution_end", "agent_settled", "auto_retry_end", "label",
              "session_info"}


# ---------- credentials ----------

def plausible_secret(v):
    return (len(v) >= 12 and " " not in v and not re.fullmatch(r"[A-Za-z]+|[0-9.]+|[a-z_\-]+", v)
            and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}", v))


def walk_json(o, key, out):
    if isinstance(o, dict):
        for k, v in o.items():
            walk_json(v, str(k), out)
    elif isinstance(o, list):
        for v in o:
            walk_json(v, key, out)
    elif isinstance(o, str):
        out.append((key, o))


def sqlite_pairs(path):
    pairs = []
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        for (table,) in con.execute("select name from sqlite_master where type='table'"):
            cur = con.execute(f'select * from "{table}"')
            cols = [c[0] for c in cur.description]
            for row in cur:
                for col, val in zip(cols, row):
                    if isinstance(val, bytes):
                        val = val.decode("utf-8", "replace")
                    if not isinstance(val, str):
                        continue
                    try:
                        walk_json(json.loads(val), col, pairs)
                    except ValueError:
                        pairs.append((col, val))
        con.close()
    except sqlite3.Error:
        pass
    return pairs


def load_secrets(specs):
    """Exact credential values from env, JSON, YAML, netrc, git-credentials and SQLite files: {value: label}."""
    values = {}
    for spec in specs:
        for path in sorted(glob.glob(os.path.expanduser(spec))):
            if not os.path.isfile(path):
                continue
            try:
                raw = open(path, "rb").read()
            except OSError:
                continue
            pairs = []
            if raw.startswith(b"SQLite format 3\0"):
                pairs = sqlite_pairs(path)
                text = ""
            else:
                text = raw.decode("utf-8", "replace")
                try:
                    walk_json(json.loads(text), "", pairs)
                except ValueError:
                    pass
                pairs += re.findall(r"(?m)^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_.\-]*)\s*[=:]\s*[\"']?([^\"'\s#]+)",
                                    text)
                pairs += re.findall(r"\"([A-Za-z0-9_]+)\"\s*:\s*\"([^\"]+)\"", text)
                pairs += [("url-password", v) for v in re.findall(r"https?://[^:/\s@]+:([^@\s]+)@", text)]
                pairs += [("password", v) for v in re.findall(r"(?m)\bpassword\s+(\S+)", text)]
            label = os.path.basename(path)
            for name, value in pairs:
                value = value.strip()
                if (SECRET_NAME.search(name) or name in ("url-password", "password")) and plausible_secret(value):
                    values.setdefault(value, f"{label}:{name}")
            for m in PATTERNS[0][1].finditer(text):
                values.setdefault(m.group(0), f"{label}:private-key")
    return values


class Redactor:
    def __init__(self, values):
        self.values = sorted(values.items(), key=lambda kv: -len(kv[0]))
        self.sources = Counter(label.split(":")[0] for label in values.values())
        self.counts = Counter()

    def __call__(self, text, count=True):
        if not text:
            return text
        for value, label in self.values:
            if value in text:
                if count:
                    self.counts["exact value from " + label] += text.count(value)
                text = text.replace(value, REDACTED)
        for name, rx in PATTERNS:
            text, n = rx.subn(REDACTED, text)
            if n and count:
                self.counts["key-shaped string: " + name] += n
        for name, rx in (("assigned secret", ASSIGNED), ("assigned password", PASSWORD_ASSIGNED)):
            text, n = rx.subn(lambda m: m.group(1) + m.group(2) + REDACTED, text)
            if n and count:
                self.counts["key-shaped string: " + name] += n
        for name, rx in (("JSON secret field", JSON_ASSIGNED), ("JSON password field", JSON_PASSWORD)):
            text, n = rx.subn(lambda m: m.group(1) + REDACTED + '"', text)
            if n and count:
                self.counts["key-shaped string: " + name] += n
        return text

    def quiet(self, text):
        return self(text, count=False)

    def leftovers(self, text):
        n = sum(text.count(v) for v, _ in self.values)
        n += sum(len(rx.findall(text)) for _, rx in PATTERNS)
        return n + sum(len(rx.findall(text)) for rx in (ASSIGNED, PASSWORD_ASSIGNED, JSON_ASSIGNED, JSON_PASSWORD))


# ---------- helpers ----------

def clip(s, n):
    s = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", s).strip()  # binary tool output would make the file binary to git
    return s if len(s) <= n else s[:n] + f"… ({len(s)} chars)"


def parse_iso(ts):
    if isinstance(ts, (int, float)) or (isinstance(ts, str) and ts.isdigit()):
        v = float(ts)
        return datetime.fromtimestamp(v / 1000 if v > 1e11 else v, timezone.utc)
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def ts_short(ts):
    t = parse_iso(ts) if ts else None
    return t.strftime("%m-%d %H:%MZ") if t else ""


def read_jsonl(path):
    entries, bad = [], 0
    with open(path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                d = json.loads(raw)
            except ValueError:
                bad += 1
                continue
            if isinstance(d, dict):
                entries.append(d)
            else:
                bad += 1
    return entries, bad


def log_format(first):
    if first.get("type") == "session_meta":
        return "codex"
    if first.get("type") == "session" and "version" in first:
        return "pi"
    return "claude"


def first_record(path):
    """(first timestamp, cwd, format, session id) from the start of a log."""
    ts = cwd = sid = None
    fmt = None
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            for i, raw in enumerate(fh):
                if i > 60 or (ts and cwd and fmt):
                    break
                try:
                    d = json.loads(raw)
                except ValueError:
                    continue
                if not isinstance(d, dict):
                    continue
                fmt = fmt or log_format(d)
                pl = d.get("payload") if isinstance(d.get("payload"), dict) else {}
                ts = ts or d.get("timestamp") or pl.get("timestamp")
                cwd = cwd or d.get("cwd") or pl.get("cwd")
                sid = sid or d.get("sessionId") or pl.get("id") or (d.get("id") if d.get("type") == "session" else None)
    except OSError:
        pass
    return ts, cwd, fmt or "claude", sid


def text_of(c):
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        out = []
        for x in c:
            if isinstance(x, dict):
                if x.get("type") in ("text", "Text", "input_text", "output_text"):
                    out.append(x.get("text", ""))
                elif x.get("type") == "image":
                    out.append("[image]")
        return "\n".join(out)
    return ""


def user_texts(d):
    c = (d.get("message") or {}).get("content")
    if isinstance(c, str):
        return [c]
    return [b.get("text", "") for b in c or [] if isinstance(b, dict) and b.get("type") == "text"]


def attachment_prompt(a):
    p = a.get("prompt")
    if isinstance(p, list):
        return "\n".join(x.get("text", "") for x in p if isinstance(x, dict) and x.get("type") == "text")
    return p if isinstance(p, str) else ""


def new_stats():
    return {"prompts": 0, "replies": 0, "results": 0, "answers": 0, "tool_calls": 0, "notifications": 0,
            "summaries": 0, "undelivered": 0, "thinking_dropped": 0, "dropped": Counter(), "unknown": Counter(),
            "models": Counter(), "titles": [], "bad_lines": 0, "expected_tool_calls": 0}


def generic(ts, kind, obj, R):
    return f"⚙ [{ts_short(ts)}] {kind}: {clip(R(json.dumps(obj, ensure_ascii=False, default=str)), 200)}"


# ---------- Claude Code ----------

def tool_input_line(name, i, R):
    def first(*keys):
        for k in keys:
            v = i.get(k)
            if isinstance(v, str) and v.strip():
                return v
        return ""
    if name == "Bash":
        s = f"  ⎿ Bash: {clip(R(first('description')), 160)}"
        cmd = first("command")
        return s + ("\n    $ " + clip(R(cmd).replace("\n", " ⏎ "), 300) if cmd else "")
    if name == "Workflow":
        what = first("scriptPath", "name")
        if not what and isinstance(i.get("script"), str):
            m = re.search(r"name:\s*['\"]([^'\"]+)['\"]", i["script"])
            what = f"inline script '{m.group(1)}'" if m else "inline script"
        if i.get("resumeFromRunId"):
            what += f" (resume {i['resumeFromRunId']})"
        return f"  ⎿ Workflow: {clip(R(what), 200)}"
    if name in ("Agent", "Task"):
        return f"  ⎿ {name}: {clip(R(first('description')), 160)} [{i.get('subagent_type') or 'default'}]"
    if name == "AskUserQuestion":
        lines = ["  ⎿ AskUserQuestion:"]
        for q in i.get("questions") or []:
            lines.append(f"    ❓ [{R(str(q.get('header', '')))}] {R(str(q.get('question', '')))}")
            for o in q.get("options") or []:
                lines.append(f"       - {R(str(o.get('label', '')))}: {R(str(o.get('description', '')))}")
        return "\n".join(lines)
    if name == "ExitPlanMode" and isinstance(i.get("plan"), str):
        return f"  ⎿ ExitPlanMode, plan:\n\n{R(i['plan'].strip())}\n"
    what = first("description", "file_path", "path", "pattern", "url", "query", "to", "skill", "action",
                 "command", "prompt", "message") or json.dumps(i, ensure_ascii=False)
    return f"  ⎿ {name}: {clip(R(what), 160)}"


def tool_names(entries):
    names = {}
    for d in entries:
        if d.get("type") == "assistant":
            for b in (d.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use":
                    names[b.get("id")] = b.get("name")
    return names


def render_claude(entries, R, st, main):
    names = tool_names(entries)
    delivered = [t.strip() for d in entries if d.get("type") == "user" for t in user_texts(d)]
    delivered += [attachment_prompt(d["attachment"]).strip() for d in entries
                  if d.get("type") == "attachment" and isinstance(d.get("attachment"), dict)
                  and "prompt" in d["attachment"]]
    out = []
    for d in entries:
        t, ts = d.get("type"), d.get("timestamp")
        if ts:
            st["first"] = st.get("first") or ts
            st["last"] = ts
        for k, src in (("session", "sessionId"), ("cwd", "cwd"), ("version", "version")):
            st[k] = st.get(k) or d.get(src)
        side = "↳ " if main and d.get("isSidechain") else ""
        m = d.get("message") if isinstance(d.get("message"), dict) else {}
        if t == "assistant":
            if m.get("model") and m["model"] != "<synthetic>":
                st["models"][m["model"]] += 1
            for b in m.get("content") or []:
                bt = b.get("type")
                if bt == "text":
                    if b.get("text", "").strip():
                        out.append(f"{side}⏺ {R(b['text'].strip())}\n")
                        st["replies"] += 1
                elif bt == "tool_use" and b.get("name") == "StructuredOutput":
                    js = json.dumps(b.get("input"), indent=2, ensure_ascii=False)
                    out.append(f"{side}⏺ Structured result:\n\n```json\n{R(js)}\n```\n")
                    st["results"] += 1
                elif bt == "tool_use":
                    i = b.get("input") if isinstance(b.get("input"), dict) else {"input": b.get("input")}
                    out.append(side + tool_input_line(b.get("name", "tool"), i, R))
                    st["tool_calls"] += 1
                elif bt in ("thinking", "redacted_thinking"):
                    st["thinking_dropped"] += 1
                elif bt == "fallback":
                    frm = (b.get("from") or {}).get("model")
                    to = (b.get("to") or {}).get("model")
                    out.append(f"{side}⚙ [{ts_short(ts)}] model fallback: {frm} → {to}")
                else:
                    out.append(side + generic(ts, f"assistant block {bt}", b, R))
                    st["unknown"][f"assistant block: {bt}"] += 1
        elif t == "user":
            if d.get("isCompactSummary"):
                txt = "\n".join(user_texts(d)).strip()
                out.append(f"\n<details><summary>Context summary written at compaction ({ts_short(ts)})</summary>\n\n"
                           f"{R(txt)}\n\n</details>\n")
                st["summaries"] += 1
                continue
            if d.get("isMeta"):
                txt = "\n".join(user_texts(d)).strip()
                if txt and not txt.startswith(("<local-command-caveat>", "Caveat:")):
                    out.append(f"⚙ [{ts_short(ts)}] (system message) {clip(R(txt), 300)}")
                st["dropped"]["meta message (one clipped line)"] += 1
                continue
            c = m.get("content")
            for b in ([{"type": "text", "text": c}] if isinstance(c, str) else c or []):
                bt = b.get("type")
                if bt == "tool_result":
                    r = R(text_of(b.get("content")))
                    if names.get(b.get("tool_use_id")) in USER_INPUT_TOOLS or r.lstrip().startswith(USER_REPLY_MARKERS):
                        out.append(f"\n{side}❯ [{ts_short(ts)}] (answer) {r.strip()}\n")
                        st["answers"] += 1
                        continue
                    head = " ⏎ ".join(r.strip().splitlines()[:3])
                    if head:
                        out.append(f"    → {'error' if b.get('is_error') else 'result'}: {clip(head, 300)}")
                elif bt == "text" and b.get("text", "").strip():
                    txt = b["text"]
                    s = txt.lstrip()
                    if s.startswith("<task-notification>"):
                        out.append(f"\n🔔 [{ts_short(ts)}] {clip(R(txt), 600)}\n")
                        st["notifications"] += 1
                    elif s.startswith(SYSTEM_PREFIXES):
                        st["dropped"]["system text in a user turn"] += 1
                    else:
                        out.append(f"\n{side}❯ [{ts_short(ts)}] {R(txt.strip())}\n")
                        st["prompts"] += 1
                elif bt in ("image", "document"):
                    out.append(f"{side}❯ [{ts_short(ts)}] [{bt}]")
                elif bt != "text":
                    out.append(side + generic(ts, f"user block {bt}", b, R))
                    st["unknown"][f"user block: {bt}"] += 1
            answers = (d.get("toolUseResult") or {}).get("answers") if isinstance(d.get("toolUseResult"), dict) else None
            if isinstance(answers, dict):
                for q, a in answers.items():
                    out.append(f"{side}❯ [{ts_short(ts)}] (answer) {R(str(q))} → {R(str(a))}")
        elif t == "attachment":
            a = d.get("attachment") if isinstance(d.get("attachment"), dict) else {}
            if "prompt" in a and attachment_prompt(a).lstrip().startswith(SYSTEM_PREFIXES):
                out.append(f"\n🔔 [{ts_short(ts)}] {clip(R(attachment_prompt(a)), 600)}\n")
                st["notifications"] += 1
            elif "prompt" in a:
                txt = attachment_prompt(a).strip()
                if txt:
                    tag = "queued while busy" if a.get("type") == "queued_command" else a.get("type")
                    out.append(f"\n{side}❯ [{ts_short(ts)}] ({tag}) {R(txt)}\n")
                    st["prompts"] += 1
            else:
                st["dropped"]["context attachment: " + str(a.get("type"))] += 1
        elif t == "queue-operation":
            c = d.get("content")
            if d.get("operation") == "enqueue" and isinstance(c, str) and c.strip() \
                    and not c.lstrip().startswith(SYSTEM_PREFIXES):
                if not any(c.strip() in x for x in delivered):
                    out.append(f"\n❯ [{ts_short(ts)}] (queued, never delivered) {R(c.strip())}\n")
                    st["undelivered"] += 1
            else:
                st["dropped"]["queue operation"] += 1
        elif t == "system":
            sub, content = d.get("subtype"), d.get("content")
            if sub == "compact_boundary":
                out.append(f"\n— context compacted at {ts_short(ts)} —\n")
            elif sub == "turn_duration":
                st["dropped"]["system: turn_duration"] += 1
            elif sub == "away_summary" and isinstance(content, str):
                out.append(f"⚙ [{ts_short(ts)}] away summary: {R(content.strip())}")
            elif sub == "informational" and isinstance(content, str):
                out.append(f"⚙ [{ts_short(ts)}] notice: {R(content.strip())}")
            elif isinstance(content, str) and content.strip():
                out.append(f"⚙ [{ts_short(ts)}] system {sub}: {clip(R(content), 300)}")
                st["dropped"][f"system: {sub} (one clipped line)"] += 1
            else:
                st["dropped"][f"system: {sub}"] += 1
        elif t == "ai-title":
            title = d.get("aiTitle") or d.get("title")
            if isinstance(title, str) and title not in st["titles"]:
                st["titles"].append(title)
        elif t in CLAUDE_DROPPED:
            st["dropped"][t] += 1
        else:
            out.append(generic(ts, f"entry {t}", d, R))
            st["unknown"][f"entry: {t}"] += 1
    return out


def expected_claude(entries):
    """What must appear verbatim, and how many tool lines, read without the renderer's logic."""
    exp, tools, ids = [], 0, {}
    for d in entries:
        if d.get("type") != "assistant":
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if b.get("type") == "text":
                exp.append(("reply", b.get("text", "")))
            elif b.get("type") == "tool_use":
                ids[b.get("id")] = b.get("name")
                i = b.get("input") if isinstance(b.get("input"), dict) else {}
                if b.get("name") == "StructuredOutput":
                    exp.append(("result", json.dumps(b.get("input"), indent=2, ensure_ascii=False)))
                    continue
                tools += 1
                for q in i.get("questions") or [] if b.get("name") == "AskUserQuestion" else []:
                    exp.append(("question", str(q.get("question", ""))))
                    exp += [("option", str(o.get(k, ""))) for o in q.get("options") or [] for k in ("label", "description")]
                if b.get("name") == "ExitPlanMode" and isinstance(i.get("plan"), str):
                    exp.append(("plan", i["plan"]))
    for d in entries:
        t, m = d.get("type"), d.get("message") or {}
        if t == "user" and not d.get("isMeta"):
            exp += [("prompt", x) for x in user_texts(d) if not x.lstrip().startswith(SYSTEM_PREFIXES)]
            for b in m.get("content") if isinstance(m.get("content"), list) else []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    r = text_of(b.get("content"))
                    if ids.get(b.get("tool_use_id")) in USER_INPUT_TOOLS or r.lstrip().startswith(USER_REPLY_MARKERS):
                        exp.append(("answer", r))
            tur = d.get("toolUseResult")
            if isinstance(tur, dict) and isinstance(tur.get("answers"), dict):
                exp += [("answer", str(a)) for a in tur["answers"].values()]
        elif t == "attachment" and isinstance(d.get("attachment"), dict) and "prompt" in d["attachment"] \
                and not attachment_prompt(d["attachment"]).lstrip().startswith(SYSTEM_PREFIXES):
            exp.append(("prompt", attachment_prompt(d["attachment"])))
        elif t == "queue-operation" and d.get("operation") == "enqueue" and isinstance(d.get("content"), str) \
                and not d["content"].lstrip().startswith(SYSTEM_PREFIXES):
            exp.append(("queued prompt", d["content"]))
        elif t == "system" and d.get("subtype") in ("away_summary", "informational") \
                and isinstance(d.get("content"), str):
            exp.append(("system text", d["content"]))
    return [(k, x) for k, x in exp if x.strip()], tools


# ---------- Codex ----------

def codex_error(pl):
    kind = str(pl.get("type"))
    if pl.get("error"):
        e = pl["error"]
        return f"{kind} error", e if isinstance(e, str) else json.dumps(e, ensure_ascii=False)
    if "error" in kind or "warning" in kind:
        return kind, str(pl.get("message") or json.dumps(pl, ensure_ascii=False))
    return None


def render_codex(entries, R, st):
    out = []
    for d in entries:
        t, ts = d.get("type"), d.get("timestamp")
        pl = d.get("payload") if isinstance(d.get("payload"), dict) else {}
        if ts:
            st["first"] = st.get("first") or ts
            st["last"] = ts
        if t == "session_meta":
            st["session"], st["cwd"] = pl.get("id"), pl.get("cwd")
            st["version"], st["originator"] = pl.get("cli_version"), pl.get("originator")
        elif t == "turn_context":
            if pl.get("model"):
                st["models"][pl["model"]] += 1
        elif t == "response_item":
            pt = pl.get("type")
            if pt == "message":
                role = pl.get("role")
                for c in pl.get("content") or []:
                    ct, txt = c.get("type"), c.get("text") or ""
                    if role == "assistant" and ct == "output_text" and txt.strip():
                        out.append(f"⏺ {R(txt.strip())}\n")
                        st["replies"] += 1
                    elif role == "user" and ct == "input_text" and txt.strip():
                        if txt.lstrip().startswith(CODEX_CONTEXT):
                            tag = txt.lstrip().split(">", 1)[0][:40]
                            out.append(f"⚙ context {tag}> ({len(txt)} chars, not shown)")
                            st["dropped"]["injected context block"] += 1
                        else:
                            out.append(f"\n❯ [{ts_short(ts)}] {R(txt.strip())}\n")
                            st["prompts"] += 1
                    elif role in ("developer", "system") and txt.strip():
                        out.append(f"⚙ {role} instructions ({len(txt)} chars, not shown)")
                        st["dropped"][role + " instructions"] += 1
                    elif ct in ("input_image", "local_image"):
                        out.append(f"❯ [{ts_short(ts)}] [image]")
            elif pt == "reasoning":
                st["thinking_dropped"] += 1
            elif pt in ("function_call", "custom_tool_call"):
                args = pl.get("arguments") if pt == "function_call" else pl.get("input")
                out.append(f"  ⎿ {pl.get('name')}: {clip(R(str(args or '')).replace(chr(10), ' ⏎ '), 300)}")
                st["tool_calls"] += 1
            elif pt in ("function_call_output", "custom_tool_call_output"):
                o = pl.get("output")
                if isinstance(o, dict):
                    o = o.get("content") if isinstance(o.get("content"), str) else json.dumps(o)
                head = " ⏎ ".join(R(str(o or "")).strip().splitlines()[:3])
                if head:
                    out.append(f"    → result: {clip(head, 300)}")
            elif pt == "local_shell_call":
                cmd = (pl.get("action") or {}).get("command")
                cmd = " ".join(cmd) if isinstance(cmd, list) else str(cmd)
                out.append(f"  ⎿ shell: {clip(R(cmd), 300)}")
                st["tool_calls"] += 1
            elif pt == "web_search_call":
                out.append(f"  ⎿ web_search: {clip(R(json.dumps(pl.get('action'))), 200)}")
                st["tool_calls"] += 1
            elif pt == "agent_message":  # a message between Codex agents, such as a helper's report to the main one
                txt = "".join(c.get("text") or "" for c in pl.get("content") or [] if isinstance(c, dict)).strip()
                out.append(f"\n⇠ [{ts_short(ts)}] {pl.get('author')} → {pl.get('recipient')}: {R(txt)}\n")
            else:
                out.append(generic(ts, f"response item {pt}", pl, R))
                st["unknown"][f"response_item: {pt}"] += 1
        elif t == "event_msg":
            err = codex_error(pl)
            if err:
                out.append(f"⚠ [{ts_short(ts)}] {err[0]}: {R(err[1].strip())}")
            else:
                st["dropped"]["event: " + str(pl.get("type"))] += 1
        elif t == "compacted":
            out.append(f"\n— context compacted at {ts_short(ts)} —\n")
        elif t in CODEX_DROPPED:
            st["dropped"][t] += 1
        else:
            out.append(generic(ts, f"entry {t}", d, R))
            st["unknown"][f"entry: {t}"] += 1
    return out


def expected_codex(entries):
    exp, tools = [], 0
    for d in entries:
        pl = d.get("payload") if isinstance(d.get("payload"), dict) else {}
        if d.get("type") == "response_item":
            if pl.get("type") in CODEX_TOOL_ITEMS:
                tools += 1
            if pl.get("type") != "message":
                continue
            for c in pl.get("content") or []:
                txt = c.get("text") or ""
                if pl.get("role") == "assistant" and c.get("type") == "output_text":
                    exp.append(("reply", txt))
                elif pl.get("role") == "user" and c.get("type") == "input_text" \
                        and not txt.lstrip().startswith(CODEX_CONTEXT):
                    exp.append(("prompt", txt))
        elif d.get("type") == "event_msg":
            item = pl.get("item") if isinstance(pl.get("item"), dict) else {}
            if pl.get("type") == "item_completed" and item.get("type") in ("AgentMessage", "UserMessage"):
                for c in item.get("content") or []:
                    txt = (c.get("text") or "") if isinstance(c, dict) else ""
                    if txt.strip() and not txt.lstrip().startswith(CODEX_CONTEXT):
                        exp.append(("reply" if item["type"] == "AgentMessage" else "prompt", txt))
            err = codex_error(pl)
            if err:
                exp.append(("error", err[1]))
    return [(k, x) for k, x in exp if x.strip()], tools


# ---------- pi ----------

def pi_message_lines(msg, ts, R, st):
    out = []
    role = msg.get("role")
    c = msg.get("content")
    blocks = [{"type": "text", "text": c}] if isinstance(c, str) else c or []
    ts = ts or msg.get("timestamp")
    if role == "user":
        for b in blocks:
            if b.get("type") == "text" and b.get("text", "").strip():
                out.append(f"\n❯ [{ts_short(ts)}] {R(b['text'].strip())}\n")
                st["prompts"] += 1
            elif b.get("type") == "image":
                out.append(f"❯ [{ts_short(ts)}] [image]")
    elif role == "assistant":
        if msg.get("model"):
            st["models"][f"{msg.get('provider')}/{msg['model']}" if msg.get("provider") else msg["model"]] += 1
        for b in blocks:
            bt = b.get("type")
            if bt == "text" and b.get("text", "").strip():
                out.append(f"⏺ {R(b['text'].strip())}\n")
                st["replies"] += 1
            elif bt == "toolCall":
                args = json.dumps(b.get("arguments"), ensure_ascii=False)
                out.append(f"  ⎿ {b.get('name')}: {clip(R(args).replace(chr(10), ' ⏎ '), 300)}")
                st["tool_calls"] += 1
            elif bt == "thinking":
                st["thinking_dropped"] += 1
            elif bt != "text":
                out.append(generic(ts, f"assistant block {bt}", b, R))
                st["unknown"][f"pi assistant block: {bt}"] += 1
        if msg.get("errorMessage"):
            out.append(f"⚠ [{ts_short(ts)}] assistant error ({msg.get('stopReason')}): {R(str(msg['errorMessage']))}")
    elif role == "toolResult":
        head = " ⏎ ".join(R(text_of(c)).strip().splitlines()[:3])
        if head:
            out.append(f"    → {'error' if msg.get('isError') else 'result'} ({msg.get('toolName')}): {clip(head, 300)}")
    else:
        out.append(generic(ts, f"message role {role}", msg, R))
        st["unknown"][f"pi message role: {role}"] += 1
    return out


def render_pi(entries, R, st):
    use_events = not any(d.get("type") == "message" for d in entries)
    st["pi_events"] = use_events
    out = []
    for d in entries:
        t, ts = d.get("type"), d.get("timestamp")
        if ts:
            st["first"] = st.get("first") or ts
            st["last"] = ts
        if t == "session":
            st["session"], st["cwd"], st["version"] = d.get("id"), d.get("cwd"), f"session v{d.get('version')}"
            st["first"] = st.get("first") or d.get("timestamp")
        elif t == "model_change":
            out.append(f"⚙ [{ts_short(ts)}] model: {d.get('provider')}/{d.get('modelId')}")
        elif t == "thinking_level_change":
            out.append(f"⚙ [{ts_short(ts)}] thinking level: {d.get('thinkingLevel')}")
        elif t == "message" and isinstance(d.get("message"), dict):
            out += pi_message_lines(d["message"], ts, R, st)
        elif t == "message_end" and isinstance(d.get("message"), dict):
            if use_events:
                out += pi_message_lines(d["message"], ts, R, st)
            else:
                st["dropped"]["message_end event (same message as a session entry)"] += 1
        elif t in ("compaction", "branch_summary") and isinstance(d.get("summary"), str):
            out.append(f"\n<details><summary>{t} ({ts_short(ts)})</summary>\n\n{R(d['summary'].strip())}\n\n</details>\n")
            st["summaries"] += 1
        elif t == "custom_message":  # a message a pi extension added to the conversation for the agent
            out.append(f"\n⚙ [{ts_short(ts)}] {d.get('customType')} message to the agent: "
                       f"{R(str(d.get('content') or '').strip())}\n")
        elif t == "custom" or (t == "entry_appended" and isinstance(d.get("entry"), dict)
                               and d["entry"].get("type") != "message"):
            e = d if t == "custom" else d["entry"]
            out.append(f"⚙ [{ts_short(ts)}] custom entry {e.get('customType')}: "
                       f"{clip(R(json.dumps(e.get('data'), ensure_ascii=False, default=str)), 200)}")
        elif t == "entry_appended":
            st["dropped"]["entry_appended (a message also logged as an event)"] += 1
        elif t == "auto_retry_start":
            out.append(f"⚠ [{ts_short(ts)}] auto retry {d.get('attempt')}/{d.get('maxAttempts')}: "
                       f"{clip(R(str(d.get('errorMessage'))), 300)}")
        elif t == "agent_end" and (d.get("error") or d.get("errorMessage")):
            out.append(f"⚠ [{ts_short(ts)}] agent end: {clip(R(str(d.get('error') or d.get('errorMessage'))), 300)}")
        elif t in PI_DROPPED or t == "agent_end":
            st["dropped"]["event: " + str(t)] += 1
        else:
            out.append(generic(ts, f"entry {t}", d, R))
            st["unknown"][f"pi entry: {t}"] += 1
    return out


def expected_pi(entries):
    exp, tools = [], 0
    use_events = not any(d.get("type") == "message" for d in entries)
    for d in entries:
        if d.get("type") in ("message", "message_end") and isinstance(d.get("message"), dict):
            msg = d["message"]
            c = msg.get("content")
            blocks = [{"type": "text", "text": c}] if isinstance(c, str) else c or []
            if msg.get("role") in ("user", "assistant"):
                exp += [("prompt" if msg["role"] == "user" else "reply", b.get("text", "")) for b in blocks
                        if isinstance(b, dict) and b.get("type") == "text"]
            if (d["type"] == "message") != use_events:
                tools += sum(1 for b in blocks if isinstance(b, dict) and b.get("type") == "toolCall")
        elif d.get("type") in ("compaction", "branch_summary") and isinstance(d.get("summary"), str):
            exp.append(("summary", d["summary"]))
    return [(k, x) for k, x in exp if x.strip()], tools


# ---------- one log ----------

class Unit:
    def __init__(self, path, R, main=False):
        self.path = path
        entries, bad = read_jsonl(path)
        self.kind = log_format(entries[0]) if entries else "claude"
        self.st = st = new_stats()
        st["bad_lines"], st["lines"] = bad, len(entries) + bad
        if self.kind == "codex":
            body = render_codex(entries, R, st)
            self.expected, st["expected_tool_calls"] = expected_codex(entries)
            what = f"Codex session {st.get('session')} · {st.get('originator')} {st.get('version')}"
            dropped = "reasoning and injected context omitted"
        elif self.kind == "pi":
            body = render_pi(entries, R, st)
            self.expected, st["expected_tool_calls"] = expected_pi(entries)
            what = f"pi session {st.get('session')} ({st.get('version')})"
            dropped = "thinking omitted"
        else:
            body = render_claude(entries, R, st, main)
            self.expected, st["expected_tool_calls"] = expected_claude(entries)
            what = f"Claude Code session {st.get('session')} · Claude Code {st.get('version')}"
            dropped = "hidden thinking omitted, tool calls summarized"
        models = ", ".join(f"{k} ({v})" for k, v in st["models"].most_common()) or "unknown"
        title = f" · title \"{R(st['titles'][-1])}\"" if st["titles"] else ""
        head = (f"{what} · models {models}{title} · cwd {st.get('cwd')} · {st.get('first')} → {st.get('last')}\n"
                f"{st['prompts']} prompts, {st['replies']} replies, {st['results']} structured results, "
                f"{st['answers']} answers, {st['tool_calls']} tool calls; {dropped}.\n")
        self.text = head + "-" * 80 + "\n" + "\n".join(body) + "\n"

    def check(self, final_text, R):
        """(items expected, missing items, tool-call count problem or None)."""
        missing = [(k, x) for k, x in self.expected if R.quiet(x).strip() not in final_text]
        tools = None
        if self.st["expected_tool_calls"] != self.st["tool_calls"]:
            tools = f"{self.st['tool_calls']} tool lines for {self.st['expected_tool_calls']} tool calls"
        return len(self.expected), missing, tools


def agent_meta(path):
    meta = path[:-len(".jsonl")] + ".meta.json"
    try:
        return json.load(open(meta, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


# ---------- single-file mode ----------

def take(argv, flag, has_value, many=False):
    vals = []
    while flag in argv:
        i = argv.index(flag)
        vals.append(argv[i + 1] if has_value else True)
        del argv[i:i + (2 if has_value else 1)]
        if not many:
            break
    return vals if many else (vals[0] if vals else None)


def single(argv, R, agents_only, pre):
    out, srcs = argv[0], argv[1:]
    parts, units = [pre], []
    for n, src in enumerate(srcs):
        u = Unit(src, R, main=(n == 0 and not agents_only))
        units.append(u)
        if n == 0 and not agents_only:
            parts.append(u.text)
        else:
            meta = agent_meta(src)
            label = meta.get("description") or meta.get("label") or os.path.basename(src)
            parts.append(f"\n\n## {'Agent' if agents_only else 'Subagent'} transcript: {label} "
                         f"({os.path.basename(src)})\n\n" + u.text)
    text = "".join(parts)
    if R.leftovers(text):
        sys.exit("refusing to write: credential-shaped text left after redaction")
    total = missing = problems = 0
    for u in units:
        n, miss, tools = u.check(text, R)
        total, missing = total + n, missing + len(miss)
        for k, x in miss[:5]:
            print(f"MISSING {k} from {u.path}: {clip(R.quiet(x), 120)}", file=sys.stderr)
        if tools or u.st["unknown"]:
            problems += 1
            print(f"PROBLEM in {u.path}: {tools or ''} unknown {dict(u.st['unknown'])}", file=sys.stderr)
    open(out, "w", encoding="utf-8").write(text)
    print(f"wrote {out}: {len(text)} chars; {len(units)} logs; verbatim check {total - missing}/{total}; "
          f"tool-line or unknown-type problems {problems}; redactions {sum(R.counts.values())}")
    return 1 if (missing or problems) else 0


# ---------- tree mode ----------

def shown_path(p):
    home = os.path.expanduser("~")
    return "~" + p[len(home):] if p.startswith(home + "/") else p


def previous_sources(path):
    """Source logs listed in an earlier MANIFEST.md's Sources table."""
    found = set()
    try:
        for line in open(path, encoding="utf-8"):
            cells = [c.strip() for c in line.split(" | ")]
            if line.startswith("| ") and len(cells) > 2 and cells[1].startswith("`") and cells[1].endswith("`"):
                found.add(cells[1].strip("`"))
    except OSError:
        pass
    return found


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-") or "unnamed"


def tree(plan_path, out_dir, R, previous=None):
    plan = json.load(open(plan_path, encoding="utf-8"))
    E = os.path.expanduser
    since = parse_iso(plan["since"])
    until = parse_iso(plan["until"]) if plan.get("until") else None
    files, rows, included, unreadable, journal_paths = {}, [], set(), [], set()
    sub, machine = plan["subagents_out"], plan.get("machine", "")

    def add(rel, chunk):
        files.setdefault(rel, []).append(chunk)

    def link_to_main(rel):
        return os.path.relpath(main_rel, os.path.dirname(rel))

    # main session
    main_path = E(plan["main"]["jsonl"])
    main_rel = plan["main"]["out"]
    u = Unit(main_path, R, main=True)
    add(main_rel, f"# {plan['title']}\n\n{plan['description']}\n\n"
                  f"Workflow agents, subagents and tool sessions: [{sub}/]({sub}/MANIFEST.md).\n\n" + u.text)
    rows.append(("main session", shown_path(main_path), main_rel, [u]))
    included.add(os.path.realpath(main_path))

    # workflow agents and subagents (a copies entry renders an unreadable directory from a readable copy)
    copies = {os.path.realpath(E(c["original"])): E(c["copy"]) for c in plan.get("copies", [])}
    found = []
    for sd in plan["session_dirs"]:
        if not os.path.lexists(E(sd)):  # a session that has started no subagent or tool output yet
            continue
        for root, _, fns in os.walk(E(sd), onerror=lambda e: unreadable.append(e.filename)):
            found += [(os.path.join(root, f), os.path.join(root, f)) for f in fns if f.endswith(".jsonl")]
    for orig, cp in copies.items():
        for root, _, fns in os.walk(cp):
            found += [(os.path.join(root, f), os.path.join(orig, os.path.relpath(os.path.join(root, f), cp)))
                      for f in fns if f.endswith(".jsonl")]
        included.add(orig)
    unreadable = [p for p in unreadable if os.path.realpath(p) not in copies]
    journals = {}
    for real, shown in [x for x in found if os.path.basename(x[0]) == "journal.jsonl"]:
        wf = next((part for part in shown.split("/") if part.startswith("wf_")), "?")
        entries, _ = read_jsonl(real)
        journals[wf] = Counter(str(e.get("type")) for e in entries)
        for p in (real, shown):
            included.add(os.path.realpath(p))
            journal_paths.add(os.path.realpath(p))
    found = [x for x in found if os.path.basename(x[0]) != "journal.jsonl"]
    groups = {}
    for real, shown in found:
        wf = next((part for part in shown.split("/") if part.startswith("wf_")), "subagents")
        groups.setdefault(wf, []).append((real, shown))
    records = {}
    for sd in plan["session_dirs"]:
        for rec in glob.glob(os.path.join(E(sd), "workflows", "wf_*.json")):
            try:
                records[os.path.basename(rec)[:-5]] = json.load(open(rec, encoding="utf-8"))
            except (OSError, ValueError):
                pass
    wf_checks = []
    for wf, logs in sorted(groups.items(), key=lambda kv: min(first_record(r)[0] or "" for r, _ in kv[1])):
        logs.sort(key=lambda rs: first_record(rs[0])[0] or "")
        rec = records.get(wf, {})
        name = rec.get("workflowName") or plan.get("workflow_names", {}).get(wf) or (
            "subagents" if wf == "subagents" else "workflow")
        folder = plan.get("workflow_phase", {}).get(wf) or ("subagents" if wf == "subagents" else safe_name(name))
        rel = f"{sub}/{folder}/{safe_name(name)}-{wf}.md" if wf != "subagents" else f"{sub}/subagents/subagents.md"
        n_rec = rec.get("agentCount")
        hdr = [f"# Workflow {name} ({wf})" if wf != "subagents" else "# Subagents", "",
               f"Started by the session in [{os.path.basename(main_rel)}]({link_to_main(rel)}) on {machine}."]
        if rec:
            hdr.append(f"Run record (as last written): status "
                       f"{rec.get('status') or ('killed' if rec.get('error') else 'completed')}, started "
                       f"{rec.get('timestamp')}, {n_rec} agents, {round((rec.get('durationMs') or 0) / 60000)} min. "
                       f"Agent logs found: {len(logs)}.")
        elif wf != "subagents":
            hdr.append(f"No run record yet (the run was in progress at export time). Agent logs found: {len(logs)}.")
        if wf in journals:
            j = journals[wf]
            hdr.append(f"Workflow journal: {j.get('launched', 0)} launched, {j.get('started', 0)} agents started, "
                       f"{j.get('result', 0)} results, {j.get('failed', 0)} failed.")
        if rec.get("summary"):
            hdr += ["", f"Summary: {R(str(rec['summary']))}"]
        if rec.get("logs"):
            hdr += ["", "Log lines the script wrote:", ""]
            hdr += [f"- {R(str(x.get('message', x) if isinstance(x, dict) else x))}" for x in rec["logs"]]
        script = rec.get("script")
        if not script and rec.get("scriptPath") and os.path.exists(E(rec["scriptPath"])):
            script = open(E(rec["scriptPath"]), encoding="utf-8").read()
        if script:
            hdr += ["", "<details><summary>Workflow script (verbatim)</summary>", "", "```js", R(script.rstrip()),
                    "```", "", "</details>"]
        elif rec.get("scriptPath"):
            hdr += ["", f"Workflow script: `{rec['scriptPath']}`"]
        if rec.get("result") is not None:
            res = rec["result"] if isinstance(rec["result"], str) else json.dumps(rec["result"], indent=2,
                                                                                  ensure_ascii=False)
            hdr += ["", "<details><summary>Result returned to the session (verbatim)</summary>", "", "```",
                    R(res.rstrip()), "```", "", "</details>"]
        if rec.get("error"):
            hdr += ["", f"Error: {clip(R(str(rec['error'])), 600)}"]
        add(rel, "\n".join(hdr) + "\n")
        for i, (real, shown) in enumerate(logs, 1):
            meta = agent_meta(real)
            au = Unit(real, R)
            label = " · ".join(x for x in (meta.get("description"), meta.get("workflowPhase") and
                                          f"phase {meta['workflowPhase']}", meta.get("model") and
                                          f"model {meta['model']}") if x) or os.path.basename(real)
            add(rel, f"\n\n## Agent {i} of {len(logs)}: {label}\n\n`{os.path.basename(real)}`\n\n" + au.text)
            rows.append((f"workflow agent ({wf})" if wf != "subagents" else "subagent", shown_path(shown), rel, [au]))
            included.add(os.path.realpath(real))
            included.add(os.path.realpath(shown))
        if wf != "subagents":
            j = journals.get(wf, Counter())
            wf_checks.append((wf, name, n_rec, len(logs), j.get("started", 0), j.get("result", 0), j.get("failed", 0)))

    # tool sessions
    for spec in plan.get("tool_sessions", []):
        paths = sorted({p for g in spec["globs"] for p in glob.glob(E(g), recursive=True) if os.path.isfile(p)})
        chosen = []
        for p in paths:
            if os.path.realpath(p) in included:
                continue
            ts, cwd, fmt, sid = first_record(p)
            t = parse_iso(ts) if ts else None
            if not spec.get("whole_glob") and (not t or t < since or (until and t >= until)):
                continue
            if spec.get("format") and fmt != spec["format"]:
                continue
            if spec.get("cwd_regex") and not re.search(spec["cwd_regex"], cwd or ""):
                continue
            chosen.append((ts or "", p, sid or p))
        named = [g for g in spec["globs"] if not any(ch in g for ch in "*?[")]
        if named and not chosen:
            sys.exit(f"refusing to write: tool-session file {named} for {spec['out']} is missing")
        chosen.sort()
        # identical copies render once; with group_by_session, a session's extra files render only if they add text
        by_hash = {}
        for ts, p, sid in chosen:
            by_hash.setdefault(hashlib.sha256(open(p, "rb").read()).hexdigest(), []).append((ts, p, sid))
        sessions = {}
        for h, copies_of in by_hash.items():
            key = copies_of[0][2] if spec.get("group_by_session") else h
            sessions.setdefault(key, []).append(copies_of)
        outs = {}
        for key, variants in sessions.items():
            p0 = variants[0][0][1]
            if spec.get("split_by_subdir_of"):
                base = E(spec["split_by_subdir_of"])
                part = os.path.relpath(p0, base).split("/")[0] if p0.startswith(base + "/") else "other"
                rel = f"{sub}/tool-sessions/{spec['out']}/{safe_name(part)}.md"
            else:
                rel = f"{sub}/tool-sessions/{spec['out']}"
            outs.setdefault(rel, []).append(variants)
        for rel, session_list in outs.items():
            session_list.sort(key=lambda v: min(c[0][0] or "" for c in v))
            add(rel, f"# {spec['title']}\n\n{spec.get('description', '')}\n\nTool sessions of the session tree in "
                     f"[{os.path.basename(main_rel)}]({link_to_main(rel)}). {len(session_list)} sessions.\n")
            for i, variants in enumerate(session_list, 1):
                units = {}
                for copies_of in variants:
                    units[copies_of[0][1]] = Unit(copies_of[0][1], R)
                # prefer the most complete file (session format, most lines); add others only for missing text
                order = sorted(variants, key=lambda c: (units[c[0][1]].st.get("pi_events", False),
                                                        -units[c[0][1]].st["lines"]))
                rendered, texts = [], ""
                for copies_of in order:
                    unit = units[copies_of[0][1]]
                    if rendered and all(R.quiet(x).strip() in texts for _, x in unit.expected) \
                            and unit.st["expected_tool_calls"] <= sum(units[c[0][1]].st["tool_calls"] for c in rendered):
                        continue
                    rendered.append(copies_of)
                    texts += unit.text
                ts0 = min(c[0][0] or "" for c in variants)
                u0 = units[rendered[0][0][1]]
                chunk = [f"\n\n## Session {i} of {len(session_list)}: {ts_short(ts0)} · cwd {u0.st.get('cwd')}"]
                for copies_of in rendered:
                    unit = units[copies_of[0][1]]
                    chunk.append(f"\n`{shown_path(copies_of[0][1])}`" + "".join(
                        f"\n(identical copy: `{shown_path(c[1])}`)" for c in copies_of[1:]) + "\n\n" + unit.text)
                skipped = [c for c in variants if c not in rendered]
                if skipped:
                    chunk.append("\nAlso logged in these files, whose prompts, replies and tool calls all appear "
                                 "above:\n" + "".join(f"\n- `{shown_path(c[1])}`" for copies_of in skipped
                                                      for c in copies_of))
                add(rel, "\n".join(chunk))
                for copies_of in variants:
                    for c in copies_of:
                        rows.append((spec.get("kind_label", "tool session"), shown_path(c[1]), rel,
                                     [units[copies_of[0][1]]]))
                        included.add(os.path.realpath(c[1]))

    # sweep: every session log written since the start is exported or excluded for a stated reason
    sweep_rows, unclassified, sweep_unreadable = Counter(), [], []
    sw = plan.get("sweep", {})
    rules = [(r["field"], re.compile(r["regex"]), r["why"]) for r in sw.get("rules", [])]
    candidates = []
    for cfg in sw.get("claude_configs", []):
        root = os.path.join(E(cfg), "projects")
        for dirpath, _, fns in os.walk(root, onerror=lambda e: sweep_unreadable.append(e.filename)):
            for f in fns:
                if f.endswith(".jsonl"):
                    p = os.path.join(dirpath, f)
                    candidates.append((p, os.path.relpath(p, root).split("/")[0], "claude " + os.path.basename(cfg)))
    for home in sw.get("codex_homes", []):
        candidates += [(p, "", "codex " + os.path.basename(home))
                       for p in glob.glob(os.path.join(E(home), "sessions", "*", "*", "*", "*.jsonl"))]
    for g in sw.get("pi_globs", []):
        for p in glob.glob(E(g), recursive=True):
            if os.path.isfile(p) and first_record(p)[2] == "pi":
                candidates.append((p, os.path.basename(os.path.dirname(p)), "pi"))
    sweep_unreadable = [p for p in sweep_unreadable if os.path.realpath(p) not in copies]
    seen = set()
    for p, project, src in candidates:
        if p in seen:
            continue
        seen.add(p)
        try:
            if datetime.fromtimestamp(os.stat(p).st_mtime, timezone.utc) < since:
                continue
        except OSError:
            continue
        ts0, cwd, _, _ = first_record(p)
        if until and ts0 and parse_iso(ts0) and parse_iso(ts0) >= until:
            continue
        real = os.path.realpath(p)
        if real in journal_paths:
            sweep_rows[("workflow journal of an exported run (run metadata, summarized in its workflow file)", src)] += 1
            continue
        if real in included:
            sweep_rows[("exported", src)] += 1
            continue
        fields = {"project": project, "cwd": cwd or "", "path": shown_path(p)}
        why = next((w for fld, rx, w in rules if rx.search(fields.get(fld, ""))), None)
        if why:
            sweep_rows[(why, src)] += 1
        else:
            unclassified.append((shown_path(p), project, cwd))
    unreadable += sweep_unreadable

    # checks, then write
    final = {rel: "".join(chunks) for rel, chunks in files.items()}
    leftovers = {rel: R.leftovers(text) for rel, text in final.items()}
    if any(leftovers.values()):
        sys.exit("refusing to write: credential-shaped text left after redaction in "
                 + ", ".join(r for r, n in leftovers.items() if n))
    checks = []
    for kind, shown, rel, units in rows:
        n, miss, tools = units[0].check(final[rel], R)
        checks.append((kind, shown, rel, units[0], n, miss, tools))
    total = sum(c[4] for c in checks)
    missing = sum(len(c[5]) for c in checks)
    tool_problems = [(c[1], c[6]) for c in checks if c[6]]
    unknown = Counter()
    for c in checks:
        unknown.update(c[3].st["unknown"])
    wf_mismatch = [w for w in wf_checks if w[2] is not None and w[2] != w[3]]
    lost = sorted(previous_sources(previous) - {r[1] for r in rows} - set(plan.get("retired", {}))) if previous else []
    markers = sum(text.count(REDACTED) for text in final.values())
    dropped = Counter()
    for c in {id(c[3]): c[3] for c in checks}.values():
        dropped.update(c.st["dropped"])

    m = [f"# Transcript export manifest: {plan['title']}", "",
         f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} on {machine} by "
         f"`export_transcript.py --tree` from the session logs written since {plan['since']}"
         + (f" and started before {plan['until']}" if plan.get("until") else "") + ".", "",
         "## Checks", "",
         f"- Source logs exported: {len(rows)} ({Counter(k.split(' (')[0] for k, *_ in rows).most_common()}).",
         f"- Verbatim check: {total - missing} of {total} prompts, replies, structured results, answers and "
         f"summaries found in their output file{'' if not missing else ' — MISSING ' + str(missing)}.",
         f"- Tool calls: every tool call has its line"
         + ("" if not tool_problems else " — PROBLEMS: " + "; ".join(f"`{p}` {t}" for p, t in tool_problems[:10]))
         + ".",
         f"- Credential values checked: {len(R.values)} from {len(R.sources)} files "
         f"({', '.join(f'{k}: {v}' for k, v in R.sources.most_common(8)) or 'none loaded'}"
         f"{', ...' if len(R.sources) > 8 else ''}), plus key-shaped patterns.",
         f"- Credentials: {sum(R.counts.values())} redactions applied before clipping "
         f"({', '.join(f'{k}: {v}' for k, v in sorted(R.counts.items())) or 'none'}); {markers} [REDACTED] markers "
         f"remain in the output; scan after redaction: 0 left.",
         f"- Unreadable directories: {len(unreadable)}" + "".join(f"\n  - `{shown_path(p)}`" for p in unreadable),
         f"- Log entry or block types the renderer does not know: {dict(unknown) or 'none'}.",
         f"- Session logs since the start that are neither exported nor excluded: {len(unclassified)}"
         + "".join(f"\n  - `{p}` (project {pr}, cwd {c})" for p, pr, c in unclassified),
         f"- Source logs of the previous export that are missing now: "
         + (("none" if not lost else str(len(lost)) + "".join(f"\n  - `{p}`" for p in lost)) if previous
            else "not checked (no previous manifest)"), ""]
    if plan.get("retired"):
        m += ["Retired sources (in an earlier export, no longer on disk):", ""] + \
             [f"- `{p}`: {why}" for p, why in plan["retired"].items()] + [""]
    if wf_checks:
        m += ["## Workflow runs", "", "| Run | Workflow | Agents in the run record | Journal: started / results / "
              "failed | Agent logs exported |", "|---|---|---:|---|---:|"]
        m += [f"| {wf} | {name} | {n if n is not None else 'no record yet'} | {js} / {jr} / {jf} | {k} |"
              for wf, name, n, k, js, jr, jf in wf_checks]
        if wf_mismatch:
            m += ["", "Runs whose agent count differs from the logs found: "
                  + ", ".join(f"{w[0]} ({w[2]} vs {w[3]})" for w in wf_mismatch)
                  + ". The run record counts the agents of the run's last launch; the journal counts every agent "
                    "started, including retries and agents a kill interrupted."]
        m.append("")
    m += ["## Sweep of session logs since the start", "", "| Outcome | Log store | Logs |", "|---|---|---:|"]
    m += [f"| {why} | {src} | {n} |" for (why, src), n in sorted(sweep_rows.items())]
    m += ["", "## Left out of the transcripts by design", ""]
    m += [f"- {k}: {v}" for k, v in sorted(dropped.items())]
    m += ["", "## Not exported", ""] + [f"- {x}" for x in plan.get("not_exported", [])] + [""]
    m += ["## Sources", "", "| Kind | Source log | Lines | Prompts | Replies | Results | Answers | Tool calls | "
          "Models | Output | Verbatim |", "|---|---|---:|---:|---:|---:|---:|---:|---|---|---|"]
    for kind, shown, rel, unit, n, miss, tools in checks:
        s = unit.st
        models = ", ".join(f"{k} ({v})" for k, v in s["models"].most_common())
        m.append(f"| {kind} | `{shown}` | {s['lines']} | {s['prompts']} | {s['replies']} | {s['results']} | "
                 f"{s['answers']} | {s['tool_calls']} | {models} | `{rel}` | {n - len(miss)}/{n} |")
    if missing:
        m += ["", "## Missing text", ""]
        for kind, shown, rel, unit, n, miss, tools in checks:
            m += [f"- `{shown}` {k}: {clip(R.quiet(x), 200)}" for k, x in miss[:10]]
    final[f"{sub}/MANIFEST.md"] = "\n".join(m) + "\n"
    if R.leftovers(final[f"{sub}/MANIFEST.md"]):
        sys.exit("refusing to write: credential-shaped text in the manifest")
    for rel, text in final.items():
        path = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, "w", encoding="utf-8").write(text)
    failed = bool(missing or unreadable or unclassified or tool_problems or unknown or lost)
    print(f"wrote {len(final)} files to {out_dir}: {len(rows)} logs, verbatim {total - missing}/{total}, "
          f"tool-line problems {len(tool_problems)}, redactions {sum(R.counts.values())} ({markers} markers left), "
          f"unreadable {len(unreadable)}, unclassified {len(unclassified)}, unknown types {dict(unknown) or 0}, "
          f"lost since previous {len(lost) if previous else 'n/a'}, workflow count mismatches {len(wf_mismatch)}"
          f"{' — FAILED' if failed else ''}", file=sys.stderr)
    return 1 if failed else 0


def main():
    argv = sys.argv[1:]
    R = Redactor(load_secrets(take(argv, "--secrets-from", True, many=True)))
    plan = take(argv, "--tree", True)
    if plan:
        return tree(plan, take(argv, "--out", True), R, take(argv, "--previous", True))
    pre_file = take(argv, "--preamble", True)
    agents_only = take(argv, "--agents-only", False)
    pre = open(pre_file, encoding="utf-8").read().rstrip("\n") + "\n\n" if pre_file else ""
    return single(argv, R, agents_only, pre)


if __name__ == "__main__":
    sys.exit(main())
