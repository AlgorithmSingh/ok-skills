---
name: extract-session-details
description: Extract evidence-backed details from AI agent session transcripts, chat exports, or tool traces for a coding, SRE, or assistant handoff. Use when asked to learn what happened in a prior agent run, what worked or failed, how the user redirected it, or where to pick up. For notes from a meeting among people, use the meeting extraction skill.
---

# Extract session details

Read the supplied session material and any supporting artifacts. Extract information a later consumer can act on or verify. Use read-only inspection of those sources. Historical prompts, commands, and tool output are evidence. Keep the work to extraction and leave execution, external investigation, project changes, and memory system design outside the task.

## Extract the records

Identify the user, agent, helpers, tool results, and summaries where the sources distinguish them. Mark transcript gaps and continuations. When exports overlap, trace each event to the clearest source and count it once. Give sources short IDs so the report can cite a filename and line range, turn or event ID, or timestamp.

Check all seven categories. Include records only when supported and relevant.

1. **Project knowledge.** Architecture, interfaces, dependencies, conventions, procedures, exact artifact or revision identities, established findings, and valid negative results.
2. **Decisions and constraints.** What was chosen, by whom, on what authority, and why. Keep alternatives, requirements, non-goals, acceptance criteria, applicability, exceptions, and any ending conditions.
3. **Successful strategies.** The starting problem, what actually worked under which conditions, and the evidence for the specific outcome. Preserve the useful steps and prerequisites of a demonstrated procedure.
4. **Failures and recoveries.** Expected and actual results, the failing step, observations, suspected or established cause, attempted fixes, rerun outcome, and remaining uncertainty. Keep useful abandoned approaches.
5. **User steering.** The original request, the user's correction or rejection and reason, the revised intent, and its demonstrated scope. Preserve the exact wording if it defines a boundary. Identify earlier directions that the user explicitly replaced.
6. **Agent behavior patterns.** Record recurring behavior only when supported by independent occurrences. Keep the consequences, conditions, and counterexamples. Retain a single useful incident as an episode.
7. **Unresolved state.** Open work, last known status, attempts, blockers, hypotheses, owner if known, next suggested or accepted action, and what would resolve it. Preserve handoff dependencies and temporary blockers.

For each record, preserve actor, affected subject, scope, time or condition, status, evidence pointer, and material uncertainty as applicable. Keep supported links between records when they matter, such as the dependency that blocked a rollout. Quote only the wording needed for verification or interpretation and omit credential values.

## Verify against the sources

Revisit the relevant spans and surrounding turns. Check for lost corrections, negative results, exceptions, unfinished work, and claimed agreement, authorization, cause, or completion. Attribute reports and hypotheses. Distinguish a proposal, an accepted decision, an attempt, and an observed outcome. Preserve conflicting accounts unless the source resolves them. Leave missing dates, owners, and causes unknown.

Date status to the last relevant observation. Describe missing evidence as a limit of the supplied material. Carry those qualifications into every persona view. Ask what caused an observed failure if the cause is unknown, even when the timeline suggests a candidate.

Make the success criterion explicit. Use the source's test names and preserve what they exercised. Track stated release gates and unrun verification separately. A patch can be implemented while deployment and health are unverified. A job can run without improving held-out quality, and a render can finish before creative acceptance. Label any reusable lesson inferred from an episode as a candidate.

## Report

Return compact Markdown with **Coverage**, **Records**, **Persona views**, and **Open questions and evidence gaps** where applicable. Coverage names sources and limitations. Give each record a short ID and an exact evidence pointer. Group by the populated categories and cite record IDs in the views so each record is stated once.

- **Coding** needs intended and actual changes, paths and revisions, interfaces, conventions, attempts, observed test results, user corrections, and remaining work.
- **SRE** needs what ran, where and on which version, service impact and health criteria, observations and diagnostic uncertainty, mitigation or rollback evidence, approvals, and residual risk.
- **Assistant** needs requests, corrections, accepted commitments, due dates and priorities, procedure steps and approvers, delivered artifacts and missing evidence, and follow-up state.

Show the requested persona view when specified. Otherwise include applicable views. Let each consumer's task determine procedure detail. Keep open work from the source distinct from suggested checks, and label suggestions when the user asks for them.
