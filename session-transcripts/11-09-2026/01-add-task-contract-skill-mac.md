opencode session ses_e40f6d7d0ffeQkHi1rgYohH7hw · opencode 1.19.3 · models opencode-go/deepseek-v4.1-flash (23) · cwd /Users/ankitsingh · 2026-11-09T06:40:10.857000Z → 2026-11-09T06:43:12.074000Z
2 prompts, 0 replies, 0 structured results, 0 answers, 27 tool calls; hidden thinking omitted, tool calls summarized.
--------------------------------------------------------------------------------

❯ [11-09 06:40Z] commit to main here https://github.com/AlgorithmSingh/ok-skills/tree/main , a new directory/skill : These are the two steering prompts I'd use for Claude Code, Codex, Pi, or any autonomous coding agent. They incorporate the key safeguards from the research: binding requirements, preservation of decisions, independent verification, and persistent memory across sessions.

## 1. Existing session — Reconstruct and enforce

Use this when an agent is already working, especially when it has been running for hours or days.

## Task Contract — Reconstruct and Enforce

Reconstruct the complete Task Contract from everything discussed, requested, decided, and implemented so far.

**1. Recover the original intent**

- Review my original requests, subsequent instructions, corrections, project files, and relevant session transcripts.
- Extract every explicit requirement and assign a stable ID (R001, R002, etc.).
- Preserve exact requirements, constraints, methods, deliverables, and acceptance criteria.
- Distinguish my approved decisions from your own suggestions or assumptions. Do not treat unapproved suggestions as binding decisions.
- Do not silently omit, reinterpret, weaken, or substitute anything.

**2. Audit the current implementation**

- Compare actual work against every requirement.
- Identify what is implemented, independently verified, incomplete, incorrect, or merely claimed.
- Reconcile contradictory instructions using my latest explicit decisions. Surface unresolved conflicts rather than inventing resolutions.
- Preserve valid work. Do not restart unnecessarily.

**3. Establish the authoritative contract**

- Record the requirements, established decisions, boundaries, deliverables, and verification criteria in a durable project specification.
- Treat this specification as binding. Only my explicit instructions can change its requirements.
- You may independently choose implementation details, but you cannot change what success means.
- Maintain a requirement ledger with statuses: PENDING, IMPLEMENTED, VERIFIED, FAILED, or BLOCKED.

**4. Continue execution**

- Follow the contract, not an independently invented alternative goal.
- Work through milestones while keeping every requirement accounted for.
- Before major actions, check for conflicts with binding requirements and decisions.
- Do not introduce unnecessary architecture, tooling, approvals, or scope changes.
- Delegation, planning, simulations, and partial implementations do not count as delivery.

**5. Verify independently**

- Define concrete acceptance checks for every requirement.
- Prefer real execution, tests, runtime inspection, and reproducible evidence.
- Use an independent reviewer where available for semantic requirements.
- Never treat your own implementation claims as verification.
- Mark VERIFIED only when the required evidence exists and the designated verification passes.
- Repair failures and repeat verification.

**6. Preserve continuity**\
For long-running work, maintain persistent specification, decisions, progress, verification evidence, and the next-action handoff in the repository. Refresh these before context compaction, restart, or delegation.

A fresh agent must reconstruct its work from these authoritative artifacts, not an incomplete conversation summary.

**7. Completion rule**\
Do not declare COMPLETE until every binding requirement is VERIFIED.

If something cannot be completed, report the precise blocker, the evidence, and the remaining work. Never represent partial completion as full success.

**Now reconstruct the contract, audit the current state, and continue executing the original task without unnecessary interruption.**

## 2. New session — Rewrite first, then execute

Use this immediately after describing a new task in natural language.

## Task Contract — Compile Before Execution

Before beginning implementation, rewrite my natural-language request into an authoritative Task Contract.

Your responsibility is to preserve and fulfill my intent, not replace it with a solution you independently prefer.

**Phase 1 — Understand and compile**

Examine my request and relevant project context. Produce a Task Contract with:

1. **Objective:** The exact outcome I want.
2. **Binding requirements:** Every explicit instruction, assigned a stable requirement ID (R001, R002, etc.).
3. **Existing decisions:** Previously approved decisions that apply to this task, clearly distinguished from assumptions.
4. **Constraints and boundaries:** Required technologies, methods, restrictions, non-goals, budgets, and prohibited changes.
5. **Agent autonomy:** Implementation details you may decide independently, without changing binding requirements.
6. **Deliverables:** The exact files, functionality, artifacts, outputs, and destinations I expect.
7. **Acceptance criteria:** A concrete, observable verification method for each requirement.
8. **Milestones:** The simplest reasonable implementation sequence, with requirement IDs mapped to milestones.

Check the contract against my original request to ensure nothing was lost or invented.

Do not silently reinterpret ambiguous requirements. Resolve them from available context where possible; surface only genuinely blocking ambiguities.

**Phase 2 — Freeze the specification**

Save the contract as the authoritative project specification for substantial coding tasks.

Do not modify binding requirements without my explicit instruction.

Keep implementation plans separate from the specification. You may improve your plan without changing my objectives, constraints, or definition of success.

**Phase 3 — Execute**

- Implement the milestones in order, adjusting implementation details as necessary.
- Maintain requirement statuses: PENDING, IMPLEMENTED, VERIFIED, FAILED, or BLOCKED.
- Check your actions against binding requirements before major steps.
- Do not substitute goals, omit constraints, invent unnecessary work, or silently defer deliverables.
- Continue autonomously wherever the contract provides sufficient authority.
- If blocked, preserve the original requirement and report the blocker rather than redefining success.

**Phase 4 — Verify**

After implementation, verify every requirement against its acceptance criteria.

Prefer deterministic tests and real execution over self-assessment. Use independent review where available for requirements needing judgment.

A generated file, passing unrelated tests, a simulated run, or a confident explanation is not proof of completion.

Do not grant yourself final verification authority merely because you implemented the work.

**Phase 5 — Persist and hand off**

For long-running tasks, maintain durable project state containing:

- The authoritative specification
- Approved decisions
- Current milestone and requirement statuses
- Verification evidence
- Known blockers and the exact next action

Update this state before context resets, session changes, and delegation. New agents must read it before continuing.

**Phase 6 — Completion**

Completion requires evidence that every binding requirement is VERIFIED.

At the end, report what was delivered, where it exists, the evidence for each requirement, and any unresolved work.

Never claim COMPLETE while requirements remain pending, implemented but unverified, failed, or blocked.

**Now rewrite my request into this contract, check its completeness, and execute it. Do not pause for routine approval when my instructions already authorize the work.**

The most important rule in both is:

The user defines success. The agent implements. Evidence and independent verification establish completion.

One caveat: these prompts guide agent behavior but cannot technically prevent an agent from falsely marking itself verified. For stronger enforcement, your deterministic supervisor should own that final completion decision instead of the coding agent.

  ⎿ bash: ls -d ~/ok-skills ~/Documents/ok-skills ~/Documents/Documents-MacBook-Air/ok-skills 2>/dev/null; gh repo view AlgorithmSingh/ok-skills --json name,defaultBranch… (179 chars)
  ⎿ bash: mdfind -name ok-skills 2>/dev/null | head -20
    → result: {"defaultBranchRef":{"name":"main"},"name":"ok-skills","url":"https://github.com/AlgorithmSingh/ok-skills"}
    → result: /Users/ankitsingh/code/ok-skills
  ⎿ bash: git -C /Users/ankitsingh/code/ok-skills status --short; git -C /Users/ankitsingh/code/ok-skills branch --show-current; git -C /Users/ankitsingh/code/ok-skills l… (212 chars)
    → result: main ⏎ c77b370 Save direct-answers publishing session transcript ⏎ e17f936 Add direct-answers skill
  ⎿ bash: find /Users/ankitsingh/code/ok-skills -maxdepth 2 -not -path '*/.git*' | head -40; echo ---; cat /Users/ankitsingh/code/ok-skills/README.md
    → result: /Users/ankitsingh/code/ok-skills ⏎ /Users/ankitsingh/code/ok-skills/session-transcripts ⏎ /Users/ankitsingh/code/ok-skills/session-transcripts/10-06-2026
  ⎿ bash: cat /Users/ankitsingh/code/ok-skills/direct-answers/SKILL.md; echo ===; cat /Users/ankitsingh/code/ok-skills/boss-brief/SKILL.md
    → result: --- ⏎ name: direct-answers ⏎ description: Answer agent questions directly and stop once they are answered. Cut repetition, unsolicited expansion, and implementation clutter while keeping details that change the answer. Combines concise explanation with boss-brief's decision-level framing. Use for st… (479 chars)
  ⎿ read: /Users/ankitsingh/code/ok-skills/boss-brief/SKILL.md
    → result: <path>/Users/ankitsingh/code/ok-skills/boss-brief/SKILL.md</path> ⏎ <type>file</type> ⏎ <content>
  ⎿ bash: ls /Users/ankitsingh/code/ok-skills/session-transcripts/10-06-2026/; cat /Users/ankitsingh/code/ok-skills/session-transcripts/README.md
    → result: 01-publish-direct-answers-mac.md ⏎ # Session transcripts ⏎
  ⎿ bash: head -60 /Users/ankitsingh/code/ok-skills/session-transcripts/export_transcript.py; echo ---; env | grep -i -E 'session|pi_' | head
    → result: #!/usr/bin/env python3 ⏎ """Render Claude Code, Codex and pi session logs as Markdown transcripts, with credentials redacted. ⏎
  ⎿ bash: grep -n -i 'opencode' /Users/ankitsingh/code/ok-skills/session-transcripts/export_transcript.py | head; ls ~/.local/share/opencode 2>/dev/null | head
    → result: auth.json ⏎ log ⏎ mcp-auth.json
  ⎿ bash: git -C /Users/ankitsingh/code/ok-skills pull --rebase origin main
  ⎿ bash: opencode --help 2>&1 | head -40; echo ---; opencode export --help 2>&1 | head -20
    → result: From https://github.com/AlgorithmSingh/ok-skills ⏎  * branch            main       -> FETCH_HEAD ⏎    c77b370..c8f9aef  main       -> origin/main
    → result: ⠀                                ▄      ⏎ █▀▀█ █▀▀█ █▀▀█ █▀▀▄ █▀▀▀ █▀▀█ █▀▀█ █▀▀█ ⏎ █  █ █  █ █▀▀▀ █  █ █    █  █ █  █ █▀▀▀

❯ [11-09 06:41Z] Add a readme in that directory that this happens: First, goal substitution. An agent interprets your overall goal, develops its own implementation strategy, and then treats that strategy as more important than individual requirements. This can look like initiative, but it becomes a failure when the agent silently drops constraints.

Second, premature success judgments. The agent sees substantial progress and concludes the task is finished without independently checking every requirement. Anthropic has documented this exact failure mode in its research on long-running agents: agents sometimes see an implementation that looks substantially complete and declare the job done. 
Anthropic


Third, context degradation. Over long sessions, earlier instructions can become less influential, particularly after conversation compaction. Anthropic explicitly acknowledges that compaction can lose information and cause task drift. 
Claude by Anthropic  .

  ⎿ websearch: Anthropic research long-running agents agent sees implementation looks complete declares done
  ⎿ websearch: Anthropic Claude Code compaction loses information task drift long sessions
    → result: { ⏎   "search_id": "search_f6017ce1938fc820821d174b670801aa", ⏎   "results": [
    → result: { ⏎   "search_id": "search_cf442cdaca6179a57af94532268c1cb9", ⏎   "results": [
  ⎿ bash: cat /Users/ankitsingh/code/ok-skills/README.md; echo ---DECISION-HANDOFF---; cat /Users/ankitsingh/code/ok-skills/decision-handoff/PROMPT.md; echo ---DECISION-R… (230 chars)
    → result: # ok-skills ⏎  ⏎ Reusable skills and prompts for coding assistants.
  ⎿ bash: grep -ril 'opencode' ~/code/*/session-transcripts/*.py 2>/dev/null | head; opencode session --help 2>&1 | head -30; opencode session list 2>/dev/null | head -20
    → result: opencode session ⏎  ⏎ manage sessions
  ⎿ write: /Users/ankitsingh/code/ok-skills/task-contract/SKILL.md
  ⎿ write: /Users/ankitsingh/code/ok-skills/task-contract/README.md
    → result: Wrote file successfully.
    → result: Wrote file successfully.
  ⎿ edit: /Users/ankitsingh/code/ok-skills/README.md
    → result: Edit applied successfully.
  ⎿ bash: git -C /Users/ankitsingh/code/ok-skills status --short; git -C /Users/ankitsingh/code/ok-skills diff --stat; git -C /Users/ankitsingh/code/ok-skills diff -- REA… (166 chars)
    → result: M README.md ⏎ ?? task-contract/ ⏎  README.md | 1 +
  ⎿ bash: git -C /Users/ankitsingh/code/ok-skills add README.md task-contract && git -C /Users/ankitsingh/code/ok-skills commit -m "Add task-contract skill" && git -C /Us… (275 chars)
    → result: [main b6748c3] Add task-contract skill ⏎  3 files changed, 187 insertions(+) ⏎  create mode 100644 task-contract/README.md
  ⎿ bash: grep -n -E 'opencode|claude|codex|pi|jsonl|def main|def render|sys.argv' /Users/ankitsingh/code/ok-skills/session-transcripts/export_transcript.py | head -60
    → result: 2:"""Render Claude Code, Codex and pi session logs as Markdown transcripts, with credentials redacted. ⏎ 5:  export_transcript.py <out.md> <session.jsonl> [<agent.jsonl> ...] [--agents-only] [--preamble <file>] ⏎ 37:    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END … (327 chars)
  ⎿ bash: opencode export ses_e40f6d7d0ffeQkHi1rgYohH7hw --sanitize > /var/folders/mg/k26ks8r93bz0hhjyc590trm80000gn/T/opencode/session-export.json 2>/dev/null; python3 -… (775 chars)
    → result: <class 'dict'> ['info', 'messages'] ⏎ ['info', 'messages'] ⏎   info:
  ⎿ bash: python3 - <<'PY'
import json
p='/var/folders/mg/k26ks8r93bz0hhjyc590trm80000gn/T/opencode/session-export.json'
d=json.load(open(p))
print(d['info']['title'])
fo… (353 chars)
    → result: [redacted:session-title:ses_e40f6d7d0ffeQkHi1rgYohH7hw] ⏎ 0 user msg_1bf092867001w7fMK9UVtq7jKt parts: [('text', 46)] ⏎ 1 assistant msg_1bf092889001ksPK20uWKKFxu8 parts: [('step-start', 0), ('reasoning', 51), ('tool', 0), ('tool', 0), ('step-finish', 0)]
  ⎿ bash: python3 - <<'PY'
import json
p='/var/folders/mg/k26ks8r93bz0hhjyc590trm80000gn/T/opencode/session-export.json'
d=json.load(open(p))
for i in (0,1,9,10):
    m=d… (270 chars)
    → result: === 0 user ⏎ [ ⏎  {
  ⎿ bash: sed -n 205,270p /Users/ankitsingh/code/ok-skills/session-transcripts/export_transcript.py; sed -n 349,485p /Users/ankitsingh/code/ok-skills/session-transcripts/… (180 chars)
    → result: def ts_short(ts): ⏎     t = parse_iso(ts) if ts else None ⏎     return t.strftime("%m-%d %H:%MZ") if t else ""
  ⎿ bash: cat /Users/ankitsingh/code/ok-skills/session-transcripts/10-21-2026/01-publish-springboot-rules-mac.md
    → result: pi session 01a16121-eae3-70ff-b5ea-2258a6ca1f67 (session v3) · models openai-codex/gpt-6.1-sol (17) · cwd /Users/ankitsingh · 2026-10-22T01:02:55.203Z → 2026-10-22T01:43:40.060Z ⏎ 2 prompts, 5 replies, 0 structured results, 0 answers, 27 tool calls; thinking omitted. ⏎ ------------------------------… (350 chars)
  ⎿ bash: opencode export ses_e40f6d7d0ffeQkHi1rgYohH7hw > /var/folders/mg/k26ks8r93bz0hhjyc590trm80000gn/T/opencode/session-raw.json 2>/dev/null; python3 - <<'PY'
import… (758 chars)
    → result: null

⏺ Added `task-contract/SKILL.md` with both steering prompts, `task-contract/README.md` covering the three failure modes with Anthropic sources, and a root README entry. Committed as `b6748c3` and pushed to `main`.
