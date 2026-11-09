---
name: task-contract
description: Turn a request or a running agent session into a binding Task Contract with stable requirement IDs, preserved decisions, independent verification, and durable handoff state. Use when starting a substantial coding task, auditing work after hours or days, recovering from compaction or a new session, or when an agent has drifted from the user's requirements.
---

# Task contract

Steering prompts for Claude Code, Codex, Pi, or any autonomous coding agent. They turn a request or a running session into a binding Task Contract: stable requirement IDs, preserved decisions, independent verification, and durable state across context resets.

Use the prompt that fits the moment:

- **Existing session** when work is already underway, especially after hours or days. Paste the prompt to reconstruct intent, audit progress, and continue against the recovered contract.
- **New session** immediately after describing a new task in natural language. Paste the prompt to compile the request into a contract before implementation starts.

The most important rule in both: **The user defines success. The agent implements. Evidence and independent verification establish completion.**

Caveat: these prompts guide agent behavior but cannot technically prevent an agent from falsely marking itself verified. For stronger enforcement, a deterministic supervisor should own the final completion decision instead of the coding agent.

## Prompt 1 — Existing session: Reconstruct and enforce

```markdown
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

**6. Preserve continuity**
For long-running work, maintain persistent specification, decisions, progress, verification evidence, and the next-action handoff in the repository. Refresh these before context compaction, restart, or delegation.

A fresh agent must reconstruct its work from these authoritative artifacts, not an incomplete conversation summary.

**7. Completion rule**
Do not declare COMPLETE until every binding requirement is VERIFIED.

If something cannot be completed, report the precise blocker, the evidence, and the remaining work. Never represent partial completion as full success.

**Now reconstruct the contract, audit the current state, and continue executing the original task without unnecessary interruption.**
```

## Prompt 2 — New session: Compile before execution

```markdown
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
```

## The rule both prompts enforce

The user defines success. The agent implements. Evidence and independent verification establish completion.
