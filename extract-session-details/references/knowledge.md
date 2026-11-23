# Knowledge: subject pages, registry, ledger and holding page

Stage 3 of the store. It turns the records in the evidence documents under `docs/extractions/` into maintained pages, one per subject, under `docs/knowledge/`. Stage 1 defines the [record format](store.md). Stage 2 builds the [evidence documents](evidence.md). Use the locations below unless the user or the project's instructions name others.

| File | Location | Holds |
|---|---|---|
| Subject page | `docs/knowledge/<type>s/<slug>.md` | The current state and history of one project, service, feature, procedure, decision or recurring problem, across every source. |
| Registry | `docs/knowledge/subjects.md` | One row per subject: ID, title, aliases, scope, status, page. |
| Ledger | `docs/knowledge/sources.md` | One row per distinct source: hash, dates, stage, evidence document and the subjects it touched. |
| Holding page | `docs/knowledge/unassigned.md` | Actionable records whose subject the evidence does not establish. |
| Indexes | `docs/knowledge/index.md` and one `index.md` in each type folder | Navigation in the format of [evidence.md](evidence.md) step 8, when the project uses indexes. `docs/knowledge/index.md` lists the three tables and the type folders. |

A subject page states each current specific once and links the source lines that establish it. Its History rows name the change and link the evidence. They do not restate the record. The evidence documents stay as they are: they say what one source said, with its status at the time. A subject page says what is established about the subject as of its latest evidence.

## Subject types

Pick the narrowest type the evidence supports. Link to broader scopes instead of copying their content.

| Type | Use for | Canonical home for |
|---|---|---|
| `project` | A program, repository or body of work with shared conventions | Project-wide constraints, conventions and owners |
| `service` | A system, component or repository with interfaces and operating rules | Service constraints, interfaces, environments |
| `feature` | A capability or change being built or maintained | Its requirements, design, local decisions, validation, ownership, open work |
| `procedure` | How something gets done: intake, approval, release, rollback | Trigger, prerequisites, steps, approvers, routing, completion evidence |
| `decision` | A choice that affects more than one subject, or that the source treats as an architecture decision | Question, decision, rationale, rejected alternatives, affected subjects |
| `problem` | A recurring problem with a cause hypothesis and attempts, possibly across features | Hypothesis, occurrences, attempts, predicted and observed outcomes, provenance |

Rules:

1. **One canonical home.** Each specific lives on one page. A shared procedure, a service constraint or a cross-feature decision lives on its own page. Each affected subject gets one line linking to it and saying how it applies, for example `- [Release approval](../procedures/release-approval.md): required before the export ships to production.` The matching line on the canonical page names the affected subject and how the rule applies to it, and nothing else; instance status (requested, submitted, approved) lives only on the affected subject's page.
2. **Decisions.** A decision that concerns one feature lives on that feature's page under Decisions. Create a `decision` page only when the choice affects more than one subject or the source calls it an architecture decision. Most facts need no decision page.
3. **Procedures.** A feature page never copies procedure steps. It links the procedure page and says when the procedure applies. A `procedure` page is created only when a source states steps or rules as a reusable procedure; a single operational episode, such as one on-call swap, stays an item on the broader subject or on the holding page. Procedure Steps hold only the general procedure, never one subject's instance history.
4. **Problems.** A feature is not a root cause. Use a `problem` page when a source calls a problem recurring, or when the evidence shows it in more than one occurrence or more than one subject. An occurrence is a dated observation of the same failure mode (the same component and kind of symptom) with its own evidence; two or more occurrences within one session count. A one-off failure and its fix stay on the feature page under Attempts and outcomes. A problem page states the problem and attempts as observed, and labels any cross-occurrence lesson inferred from an episode `candidate`; the page itself is not a lesson. One problem page can list several features. One feature can link several problems and decisions.

## Identity

- **ID.** `<type>/<slug>`, for example `feature/dataset-versioning`. The slug is lowercase words joined by hyphens, from the name the first source uses. Set the ID once and never recompute it, even after a rename.
- **Page path.** `docs/knowledge/<type>s/<slug>.md`: `projects/`, `services/`, `features/`, `procedures/`, `decisions/`, `problems/`.
- **Aliases.** Every name a source uses for the subject, each with a link to a line that uses it, listed in the page's Scope section. Front matter `aliases` and the registry's Aliases column list the names only.
- **Matching.** Compare a source's names with every ID slug, title and alias in the registry. Normalize both sides the same way: lowercase, replace each punctuation character with a space, collapse spaces. Treat an exact normalized name as a subject match when the record's scope is compatible. When its scope conflicts, use the other source evidence to determine the subject before routing or adding aliases. If the subject remains unclear, use the holding page. Never treat two subjects as one merely because their names look alike, share words or one contains the other. When no registered name matches exactly, check for a **candidate match** before creating a subject: a record that shares a literal, distinctive identifier with an existing subject's items (a test name, file path, ticket, branch, commit or exact error string), or where the source explicitly refers back to an earlier item or discussion ("last time", "the same failure as last week", or answering an open item from an earlier source). On a clear candidate match whose scope fits that subject, route to the existing subject, add the new name as an alias with its evidence link, and add a `revised` History row. If a name matches two active subjects, or a candidate match remains uncertain, use the record's scope and other names. When a possible duplicate remains unresolved, use the holding page with `possible duplicate of <id>` in Why unassigned.
- **New subject.** Create one only when a source names a distinct feature, service, procedure, decision or recurring problem, the evidence gives it state of its own to maintain beyond a single mention (such as a requirement, decision, owner, status or attempt), and neither exact matching nor candidate matching matches an existing subject. A sub-feature gets its own page only when a source treats it as separate work (for example with its own owner, estimate or ticket); otherwise it stays an item on the broader subject. If the scope of the thing is unclear, put the record on the holding page instead. To create a subject, write the page from the template for its type, add its registry row, and update the type index when the project uses one.
- **Rename.** Only when a source or the owner says it. Keep the ID. Change the title in front matter, the H1 and the registry. Add the old name as an alias. Add a History row with Change `revised`.
- **Merge and split.** Only on explicit evidence (including a later source or check showing a shared literal identifier or explicit back-reference between two separately created pages) or the owner's instruction. Move each item to its successor page with a `moved` History row there that cites each source supporting the item. The retired page keeps its History, gets a `moved` row, and becomes a short page pointing to its successor or successors. Its front matter `status` and registry Status read `merged into <id>` or `split into <id>, <id>`. Never delete a retired page.

## What to route

Route every actionable record in a new or changed evidence document. Actionable records are decisions, requirements, constraints, procedures, commitments, status reports, open items, attempts, outcomes and findings. Each one goes to at least one subject page, or to the holding page. A record whose specifics concern several subjects puts each specific on its canonical page.

Keep a material definition or scope boundary on the affected item in its canonical home, with its source link and attribution. It does not create a subject. Preserve any `(inferred)` label and any material uncertainty when routing.

Name each record's subjects from the evidence document's "Subjects it names" section and from the record itself. Documents written before Stage 3 existed have no such section; name the subjects from their records.

Do not route:

- records marked `illustrative`, including purely illustrative worked examples and hypotheticals;
- records explicitly labelled `background` in evidence, such as general definitions, explanations and reference notes of third-party material;
- records the evidence document does not hold. A Not held row means another document holds the passage; route it from the holder.

When a requested research claim or one material to a decision, design or comparison concerns a subject, route Claim, Support, Applies when and Limits together on its canonical item, preserving attribution. If actionable but scope is unclear, use the holding page. General reference material stays labelled background in evidence. For example, minutes choosing batches of 20 might cite a trial. On the batch-size decision keep **Claim** “median queue time fell from 8 s to 5 s”, **Support** “staging trial reported by Eli”, **Applies when** “batches of 20 on the trial dataset”, and **Limits** “peak load untested”. The decision and the reported measurement retain their own statuses.

Illustrative examples stay in evidence and cannot create or update live knowledge. Readers can follow a rule's existing evidence links to the source records and examples. If the source also establishes an applicability decision, observation, or outcome, route that fact under its own status, scope, and evidence.

A whole source that says it is invented, such as a test fixture, is not illustrative record by record. Route it only into a store the user named for it, never into the project's own `docs/knowledge/`.

Keep each record's status. A `second-hand` record can add provisional knowledge. A reproduction of an existing observation adds no independent corroboration. Second-hand records never supersede or resolve first-hand evidence.

## Dates and order

Keep three dates apart:

- **Event date:** when the thing was said, decided or observed. For a meeting, the meeting date. For a session, the date of the turn if stated, otherwise the session date. Write `YYYY-MM-DD`, or `YYYY-MM` or `YYYY` when the source gives only that, or `unknown`.
- **Effective dates:** what the source says about when something applies or ends, such as "until the migration is verified". Keep them as bullets on the item, worded as stated.
- **Ingested date:** the date of the run that wrote the row, `YYYY-MM-DD`, in the owner/project local time zone, or UTC when unknown.

`evidence_through` on a page is the latest event date applied to it, or `unknown` if every record it holds is undated.

Apply records in event-date order. On the same date, order by the time the source states, then by stated version or `Revises` relation, then by source path, then by first line. Records with an `unknown` event date come last. They can add, corroborate, refine, conflict or change status, and they can supersede only when they say so explicitly (rule 4). Ingestion order never decides what is current.

## Update rules

Before applying a record to an existing item, check that the source addresses the same question, object or workflow under compatible conditions. Check the environment, data, actor, time or version when material. A subject match permits routing to the page, but a different scope can establish a separate item on that page. Keep the earlier item and unresolved question as they were unless evidence addresses their scope. If item scope remains uncertain, preserve what is established and the uncertainty without corroborating, refining, superseding, changing status or resolving the item.

For each routed record, in event-date order:

1. **Add.** A new specific becomes a current item with its status, event date and evidence links. History: `added`.
2. **Corroborate.** Independent evidence for the same specifics add that source's evidence links to the item. No second item. History: `corroborated`.
3. **Refine.** Compatible added detail amends the item. Both sources stay linked. History: `revised`.
4. **Supersede.** A source states that it replaces, changes or withdraws an earlier position, and its speaker has authority over that choice in the evidence. Move the old item to Superseded and withdrawn with what replaced it, when and by whom. History: `superseded`, or `withdrawn` when the proposer drops their own proposal. Observations and occurrences are never superseded by later observations or measurements; they stay as dated occurrences, while a later observation adds an occurrence or updates the Status item. Only a source correction (Source edit) or an explicit retraction by the observer moves an observation to Superseded and withdrawn.
5. **Later decision, no explicit reference.** The same decider, or someone the evidence shows has authority, makes a different choice on the same question at a later event date. Move the earlier item to Superseded and withdrawn and mark it `(inferred from date order)`. History: `superseded`, with `(inferred from date order)` in What changed.
6. **Conflict.** Anything else that disagrees. Both items stay current with their own status. Add the conflict under Open items and conflicts. A later assistant proposal does not replace an owner's decision. More confident wording does not either. History: `conflict`.
7. **Status change.** Requested, submitted, approved, rejected, completed and verified are separate states, each with its own date and evidence. So are assigned and accepted. Submitted never implies approved. Assigned never implies accepted. Update the status line and keep each earlier state as a bullet with its date and evidence. History: `status`.
8. **Resolve.** A source that settles an open item or conflict marks it resolved with evidence. Delete the resolved item from Open items and conflicts; History keeps it, and do not move it to Superseded and withdrawn. History: `resolved`.

**Late evidence.** A record whose event date is earlier than the page's `evidence_through` uses the same rules. Insert its History row at its own date. Then re-apply, in event-date order, every later record on the same item. If one of them now applies differently, change that row's Change and What changed to match and fix the item. Do not add rows for those later records. With candidate matching and the subject-creation threshold, the store reaches the same active subject pages, current specifics and statuses whichever order the sources arrived in; a page's ID slug comes from the first source that creates it, while later names become aliases.

**Idempotency.** Reconcile each effect by source hash, underlying statement or observation, target item and effect on that item. Compare provenance and meaning as well as lines. A single span can supersede one item and add another. On retry apply only missing effects. When re-extraction shifts a span or renames a heading, repair locators on existing rows, including holding rows, and preserve Ingested. Replay later records when an effect changes. Never use a hash/span match as a reason to skip the remaining effects.

**Owner edits.** Append each owner rule, clarification, retirement or curated worked example verbatim to `docs/knowledge/owner-instructions.md` with a stable entry heading, event date, subject ID, target item, scope and requested effect. Link supporting evidence and identify the owner. Link the entry in the History Lines cell with Source `owner instruction`. Replay these entries alongside evidence in event-date order. Before replacing a page with legacy owner History or manual edits, reconcile its reviewed text into this journal. Preserve unresolved edits for the owner when attribution or scope is unclear.

## Recurring problems and attempts

A `problem` page holds:

- **Hypothesis.** The cause as the source states it, who states it, and whether it is a hypothesis or established by evidence. If no source gives a cause, write `Cause unknown: no source states one.` Never infer a cause from timing, for example from a change that came just before the failure.
- **Occurrences.** One item per dated symptom, with its evidence and setting.
- **Attempts,** in event order, each in the attempt format below. Keep failed, regressed and replaced attempts. A replaced attempt stays after the implementation changes.
- **Affects** and **Related problems.** Links with one line each. No forced parent.

Attempt format, used on problem pages and under Attempts and outcomes on feature pages:

```markdown
#### Attempt: <intervention, stated as a sentence> (<event date>)
<status> · since <event date> · <evidence links>
- Rationale: <why, as the source gives it>
- Predicted outcome: <as stated before the outcome was known, with its link>
- Observed outcome: <result, with its link, and exactly what it covers>
- Setting: <repository, service, environment, version, model, dataset, date>
- Later: <kept, revised, replaced or reverted, with link and date>
```

- Write `Predicted outcome: not stated` unless a source states the prediction before the outcome is known. Never derive a prediction from an observed outcome.
- Write `Observed outcome: not stated` when no source reports one. Say what the evidence covers and what it does not, for example "unit tests passed; not run in staging".
- Write each setting field the source gives and leave out the others.
- Write `Later: not stated` until a source says what happened to the change.
- A reader reusing an attempt checks its setting first, and gives it less weight when the environment and the version both changed.

A problem page is evidence for whoever improves a harness, skill or procedure. It authorizes no change to a harness, policy, skill or model.

## Subject page format

Every subject page uses this front matter:

```markdown
---
type: <type>
title: "<current name>"
description: "<one sentence>"
timestamp: <ISO 8601 with offset, last update>
id: <type>/<slug>
aliases: ["<name as a source uses it>"]
status: active
scope: [<broader subject id>]
evidence_through: <latest event date applied>
---

# <title>
```

`scope` lists the IDs of broader subjects, such as the service a feature belongs to, or `[]`. Then use the sections for the page's type, in this order. Omit an empty section. Never write "none".

**`feature`**

```markdown
## Scope
## Current state
### Requirements and acceptance
### Design and interfaces
### Decisions
### Constraints and procedures that apply
### Validation
### Ownership, handoffs and work status
### Open items and conflicts
## Attempts and outcomes
## Superseded and withdrawn
## History
```

**`service` and `project`**

```markdown
## Scope
## Current state
### Interfaces and environments
### Constraints and conventions
### Decisions
### Owners
### Open items and conflicts
## Applies to
## Superseded and withdrawn
## History
```

**`procedure`**

```markdown
## Scope
## Current procedure
### Prerequisites
### Steps
### Required fields and artifacts
### Actors, approvers and routing
### Escalation and exceptions
### Completion evidence
### Authority and version
## Applies to
## Open items and conflicts
## Superseded and withdrawn
## History
```

The procedure's Scope states its trigger and where it applies. Steps hold one item whose bullets are the numbered steps in order. Give each step its evidence link when steps come from different sources. If two sources disagree on a step, it is a conflict.

**`decision`**

```markdown
## Question
## Decision
## Rationale
## Alternatives and why rejected
## Conditions and ending conditions
## Affects
## Open items and conflicts
## Superseded and withdrawn
## History
```

The Decision item's status line names the status, who decided and the date, for example `decided by Priya Raman · since 2026-02-23 · ...`.

**`problem`**

```markdown
## Hypothesis
## Occurrences
## Attempts
## Status
## Affects
## Related problems
## Superseded and withdrawn
## History
```

### Scope section

One or two sentences on what the subject covers and excludes, then:

```markdown
- Also called: "<name as a source uses it>" ([L12](<link to source>#L12))
- Part of: [<title>](<link to page>)
- Access: <restriction as the source states it>, with its evidence links
```

Leave out a line that has nothing to hold. Record access restrictions that sources state. Never write a credential value; name the credential or where it is kept instead.

### Current items

Each current item is a `####` heading stating the point, one status line, then bullets with every specific: names, numbers, versions, paths, conditions, effective dates, rationale, rejected alternatives and their reasons.

Put each item in the section its kind names: requirements and acceptance criteria under Requirements and acceptance, decisions under Decisions, owners, assignments and work status under Ownership, handoffs and work status or Owners, open items and conflicts under Open items and conflicts, attempts under Attempts and outcomes or Attempts. A finding goes in the section it concerns, usually Validation or Design and interfaces.

```markdown
#### <the point, stated as a sentence>
<status> · since <event date> · <evidence links>
- <every specific, stated once>
```

- **Status.** Use the Stage 1 [status vocabulary](store.md), including `candidate` for an inferred lesson. Decisions explicitly recorded in attributed minutes carry the decider and note-taker in their status. Apply the same authority and supersession rules as for other decisions by that decider.
- **Inferences.** Inferred details, such as a calendar date calculated from a relative weekday (`Friday is 2026-02-27 (inferred)`), are allowed on a subject page only when tagged `(inferred)` beside the source's exact words. Never replace the source's words with an untagged inference.
- **Since.** The event date of the evidence that set the current status.
- **Evidence links.** For each supporting record, a link to the raw source lines and a link to the evidence document, separated by `; ` between sources:

  ```markdown
  [<source label> L41-L52](<link to source>#L41-L52) ([evidence](<link to evidence document>))
  ```

  `<source label>` is the evidence document's file name without `.md`. From a subject page, a raw source at the repository root is `../../../<repository-relative path>`, and an evidence document is `../../extractions/<path>`. Write spaces as `%20`, `(` as `%28` and `)` as `%29`.
- **Applicability line.** On an affected subject, a link to the canonical page with one line on how it applies, as in rule 1 of Subject types. It goes under Constraints and procedures that apply, Applies to or Affects, whichever the page type has. Add the matching line on the canonical page under Applies to or Affects, naming only the affected subject and how the rule applies to it; never copy the affected subject's instance status onto the canonical page. Each new line is a page change: give it a History row with Change `added` that cites the source.

Open items and conflicts use the same format. A conflict names each side, its status, who holds it and its evidence, and whether anyone accepted either side:

```markdown
#### Conflict: <the question, stated as a sentence>
open · since <event date> · <evidence links>
- <side>: <status>, <who>, <evidence links>
- <side>: <status>, <who>, <evidence links>
- Accepted by: <who, with link, or "no one in the evidence">
```

Superseded and withdrawn items keep their specifics and say what replaced them:

```markdown
#### <the point, stated as a sentence>
superseded · <event date> to <event date> · <evidence links>
- Replaced by: <current item heading>, <who>, <event date>, <evidence links>
```

Use `withdrawn by <who>` in place of `superseded` when the proposer dropped it. Add `(inferred from date order)` after `superseded` under rule 5.

### History

History is one table, kept in event-date order, with the same order rules as above:

```markdown
| Event date | Source | Lines | Change | What changed | Ingested |
|---|---|---|---|---|---|
| <event date> | [<source label>](<link to evidence document>) `<sha12>` | [L41-L52](<link to source>#L41-L52) | <change> | <what changed> | <ingested date> |
```

- **Source.** A link to the evidence document and the first 12 hex characters of the source's sha256 in a code span. For a change made on the owner's direct instruction in the run, write `owner instruction` and link the replayable journal entry in Lines.
- **Lines.** One link per line range of the record. When held records share the same spans, link the Source cell to the specific record heading in the evidence document or include its heading in What changed (Record on the holding page). Repair that reference if the heading changes.
- **Change.** Exactly one of `added`, `corroborated`, `revised`, `superseded`, `conflict`, `resolved`, `status`, `corrected`, `withdrawn`, `moved`, `evidence removed`.
- **What changed.** One short clause naming the item and the change, for example `Row limit 50,000 per export added` or `Nightly batch decision superseded by streaming (inferred from date order)`. Do not restate the record.
- A record usually gives one row per page. A record with two effects on one page, such as superseding one item and adding another, gives one row per effect.

## Routine ingestion

1. Follow [Stage 1](store.md) and [Stage 2](evidence.md). Stage 2 writes the ledger row as `extracted`.
2. Read the registry, the holding page, and the new evidence document's records and Subjects it names section.
3. For each actionable record, name its subjects, match them against the registry, and decide: an existing subject, a new subject, or the holding page.
4. Group the routed records by subject. For each subject, read only its page, apply its records in event-date order with the update rules, and write the page once. Set `evidence_through` to the latest event date applied, and update `timestamp` and `aliases`.
5. Update the registry, the holding page and any project-required indexes. On each existing subject type folder's `index.md`, copy every page's front matter `description` word for word whenever the page is created or its `description` changes. Set the ledger row to `routed` and fill its Subjects.
6. If the target uses `docs/log.md`, add one bullet under today's `## YYYY-MM-DD` heading naming the sources routed and the subject pages created or changed.
7. Run the finish checklist.

See the [table templates](tables.md) for the registry, ledger and holding page. Use [maintenance.md](maintenance.md) for replays, edits, migrations, backfills or retirement.

## Consumers

Coding agents use requirements, interfaces and validation on feature pages. SREs use service constraints, attempts and recovery evidence. Assistants use procedure steps, accepted ownership and open work. All three follow canonical links and the repository’s access permissions.

## Finish

Check each routed record against page History or the holding page, including each effect on each item. Check the ledger and registry and update any project-required indexes and changelog. Run the loaded skill’s own [scripts/check_store.py](../scripts/check_store.py) with Python 3 and `--root` pointing to the target repository. Fix errors and review warnings.

Leave `docs/extractions/` and `docs/knowledge/` uncommitted for human `git diff` review unless the user explicitly asks to commit. Report `git diff --stat HEAD -- docs/knowledge/` and list new untracked files separately with `git ls-files --others --exclude-standard -- docs/extractions/ docs/knowledge/`. Report sources, relations, subject and holding-page changes, stage counts and remaining gaps.
