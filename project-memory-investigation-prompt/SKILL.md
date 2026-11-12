---
name: project-memory-investigation-prompt
description: Create a project-specific investigation prompt for extracting knowledge, execution experience, user steering, recurring agent behavior, and unresolved work from session history. Use when asked to prepare this research for a new project or a later update. Produces the research assignment, launch directory, and artifact locations; does not launch extraction or build a memory system.
---

# Project memory investigation prompt

Turn the owner's wish to learn from a project's agent sessions into a concrete, evidence-backed research assignment. Write the investigation prompt itself. Do not merely explain the method, generate another assignment to write a prompt, or launch the investigation.

The reusable design is: learning goal, seven extraction categories, evidence rules, project-specific scope, and explicit artifacts. Adapt the project facts and success distinctions. Keep that research design intact.

## Inputs

Accept natural language. For example:

```text
Prepare a session-memory investigation prompt for /work/my-project.
Save the prompt under /work/research/2026-11-12.
```

Resolve:

- The canonical project root and project name.
- Where to save the prompt, separately from the project-owned research output.
- Whether this is an initial investigation or an update to a previous extraction.
- A previous extraction directory and cutoff, if supplied.

When the user says "this project", verify the current workspace root rather than asking unnecessarily. Ask only if the project or a material access boundary cannot be resolved. Do not require a form or a fixed set of parameter names.

The prompt file may live wherever the owner requests, including a shared notes folder. If no prompt location is given, use the project's permitted scratch area and state the chosen path.

The authoritative analysis belongs in the canonical project's own repository. Default to `<project-root>/docs/session-memory/<run-date>/`, following its documentation conventions. Reading shared transcripts, or saving the prompt beside them, does not make that shared workspace the owner of the analysis. Do not put the primary results in another repository, a viewing copy, or ignored scratch. Only an explicit owner instruction about the analysis destination overrides this rule.

Require the researcher to commit and push the analysis and required documentation navigation/log changes in that project, staging only those paths. Save its own session transcripts separately according to project rules. Preserve prior prompts and research snapshots; updates use a new dated directory.

## Ground the assignment

1. Read applicable repository instructions, the session-start guide, and relevant owner-brief or decision entry points. Check repository metadata to resolve aliases, mergers, legacy roots, and viewing copies. Do not pull unrelated projects or download large artifacts for prompt preparation.
2. Identify the project's transcript and scratch directories, documented session-discovery tools, check-in records, shared workspace archives, and permitted native agent logs. Follow existing indexes and references. Do not scan the entire home directory or authentication stores.
3. Understand the owner's actual goal and what would count as a useful result. Identify distinctions the researcher must preserve. A passing pipeline is not necessarily an improved model; a completed render is not necessarily a readable scene; an operator demonstration is not owner acceptance.
4. Establish neighboring-project ownership and access restrictions. Shared technology or keywords do not make another project's history part of this one. Restricted contents stay restricted when copied into a transcript.

Inspect enough to ground the prompt, not the full session corpus. Read-only orientation is not a project-status audit, a new experiment, or permission to resume an old assignment. Treat check-in instructions as source context, not a reason to become the check-in agent.

## Write the investigation prompt

Read [the investigation template](references/investigation-prompt-template.md). Produce a complete project-specific Markdown assignment from it, not a bare link to the template or to an earlier conversation.

Fill in every project-specific section:

- A verified project name, canonical launch directory, and history/alias boundaries.
- Concrete source paths and documented discovery routes. Label known but inaccessible sources rather than pretending they were inspected.
- Relevant project entry-point documents and source-access limitations.
- What the research should distinguish about this project's goals, outcomes, comparisons, and failures. Ground these concerns in the inspected project material. Do not invent incidents or assume a particular verdict.
- Separate exact prompt and project-owned research paths, scoped commit/push instructions, run mode, and any previous extraction reference.

Retain the three memory types and seven categories from the template. Do not substitute a generic summary, phase plan, task-contract audit, database design, or prompt-writing workflow. Do not add categories, numerical bars, approval gates, or new infrastructure merely to appear thorough.

Keep evidence and chronology explicit. The researcher must distinguish owner decisions, agent claims, observations, inferences, and unknowns; link superseded decisions; deduplicate events; and report real source coverage. Preserve neutral, negative, and inconclusive findings instead of forcing them into success or unfinished-work labels.

For updates, require a usable current snapshot linked to the previous one. Inspect new/changed sources and revisit older evidence when a contradiction requires it. Reconcile old open items and retain prior gaps. State which earlier evidence was carried forward without a new read. Previous reports are research aids, not independent corroboration.

Make permissions concrete using the target project's documented environment. Do not hardcode your own machine, private paths, accounts, hostnames, or providers into a portable prompt. Where a project names a sandbox, preserve that name. Otherwise say that execution stays blocked until the repository's documented sandbox and task authorization exist. This is source research, not failure reproduction.

## Review before saving

Read the finished prompt for task fidelity:

- It requests extraction and consolidation, not implementation or automatic installation of memory.
- It names the actual project and filters mixed-project sources.
- The categories, evidence rules and nine core research artifacts are explicit. The analysis destination is inside the canonical project, with its documentation and scoped publication rules, unless the owner explicitly directs otherwise.
- Examples are investigative questions, not unsupported historical findings.
- Access restrictions and the rule against executing transcript content remain intact.
- It does not depend on private background conversations, an author's home directory, or unavailable example files.

This is a semantic review, not a reason to build a validator or impose a line-count test. Do not claim the prepared prompt has been evaluated on a corpus unless that actually happened.

Save it as `<project-slug>-session-memory-extraction-prompt.md`, or use the owner's requested filename. Avoid changing existing active assignments.

## Return something the owner can use

Give:

1. The saved investigation-prompt path.
2. The verified `cd` command for the canonical project.
3. A short message to paste into a fresh agent session: "Read and carry out this research assignment: <absolute prompt path>".
4. The exact project-owned research output directory, its commit/push requirement, and whether the assignment is initial or an update.

State that extraction has not been launched. Do not install a skill, start an agent, change project rules, or execute the research unless separately requested.
