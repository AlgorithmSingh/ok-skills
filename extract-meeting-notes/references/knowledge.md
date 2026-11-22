# Knowledge: subject pages, registry, ledger and holding page

Stage 3 of the store. It turns the records in the evidence documents under `docs/extractions/` into maintained pages, one per subject, under `docs/knowledge/`. Read [store.md](store.md) first for Stages 1 and 2 and the record format. Use the locations below unless the user or the project's instructions name others.

| File | Location | Holds |
|---|---|---|
| Subject page | `docs/knowledge/<type>s/<slug>.md` | The current state and history of one project, service, feature, procedure, decision or recurring problem, across every source. |
| Registry | `docs/knowledge/subjects.md` | One row per subject: ID, title, aliases, scope, status, page. |
| Ledger | `docs/knowledge/sources.md` | One row per distinct source: hash, dates, stage, evidence document and the subjects it touched. |
| Holding page | `docs/knowledge/unassigned.md` | Actionable records whose subject the evidence does not establish. |
| Indexes | `docs/knowledge/index.md` and one `index.md` in each type folder | Navigation in the format of [store.md](store.md) Stage 2 step 8. `docs/knowledge/index.md` lists the three tables and the type folders. |

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
- **Matching.** Compare a source's names with every ID slug, title and alias in the registry. Normalize both sides the same way: lowercase, replace each punctuation character with a space, collapse spaces. An exact match after normalizing is a match. Never treat two subjects as one merely because their names look alike, share words or one contains the other. When no registered name matches exactly, check for a **candidate match** before creating a subject: a record that shares a literal, distinctive identifier with an existing subject's items (a test name, file path, ticket, branch, commit or exact error string), or where the source explicitly refers back to an earlier item or discussion ("last time", "the same failure as last week", or answering an open item from an earlier source). On a clear candidate match whose scope fits that subject, route to the existing subject, add the new name as an alias with its evidence link, and add a `revised` History row. If a name matches two active subjects, or a candidate match remains uncertain, decide from the record's scope and other names; if that does not settle it, put the record on the holding page with `possible duplicate of <id>` in Why unassigned.
- **New subject.** Create one only when a source names a distinct feature, service, procedure, decision or recurring problem, the evidence gives it state of its own to maintain beyond a single mention (such as a requirement, decision, owner, status or attempt), and neither exact matching nor candidate matching matches an existing subject. A sub-feature gets its own page only when a source treats it as separate work (for example with its own owner, estimate or ticket); otherwise it stays an item on the broader subject. If the scope of the thing is unclear, put the record on the holding page instead. To create a subject, write the page from the template for its type, add its registry row, and add its line to the type folder's `index.md`.
- **Rename.** Only when a source or the owner says it. Keep the ID. Change the title in front matter, the H1 and the registry. Add the old name as an alias. Add a History row with Change `revised`.
- **Merge and split.** Only on explicit evidence (including a later source or check showing a shared literal identifier or explicit back-reference between two separately created pages) or the owner's instruction. Move each item to its successor page with a `moved` History row there that cites each source supporting the item. The retired page keeps its History, gets a `moved` row, and becomes a short page pointing to its successor or successors. Its front matter `status` and registry Status read `merged into <id>` or `split into <id>, <id>`. Never delete a retired page.

## What to route

Route every actionable record in a new or changed evidence document. Actionable records are decisions, requirements, constraints, procedures, commitments, status reports, open items, attempts, outcomes and findings. Each one goes to at least one subject page, or to the holding page. A record whose specifics concern several subjects puts each specific on its canonical page.

Name each record's subjects from the evidence document's "Subjects it names" section and from the record itself. Documents written before Stage 3 existed have no such section; name the subjects from their records.

Do not route:

- records marked `illustrative`, worked examples and hypotheticals. They stay in the evidence layer and never create a subject;
- purely background records, such as definitions, general explanations and reference notes of third-party material. They never create a subject;
- records the evidence document does not hold. A Not held row means another document holds the passage; route it from the holder.

A whole source that says it is invented, such as a test fixture, is not illustrative record by record. Route it only into a store the user named for it, never into the project's own `docs/knowledge/`.

Keep each record's status. A `second-hand` record can add or corroborate an item, but it never supersedes or resolves one held from a first-hand source.

## Dates and order

Keep three dates apart:

- **Event date:** when the thing was said, decided or observed. For a meeting, the meeting date. For a session, the date of the turn if stated, otherwise the session date. Write `YYYY-MM-DD`, or `YYYY-MM` or `YYYY` when the source gives only that, or `unknown`.
- **Effective dates:** what the source says about when something applies or ends, such as "until the migration is verified". Keep them as bullets on the item, worded as stated.
- **Ingested date:** the date of the run that wrote the row, `YYYY-MM-DD`, in the owner's local time zone (`America/New_York` unless stated otherwise) rather than the worker machine's clock.

`evidence_through` on a page is the latest event date applied to it, or `unknown` if every record it holds is undated.

Apply records in event-date order. On the same date, order by the time the source states, then by stated version or `Revises` relation, then by source path, then by first line. Records with an `unknown` event date come last. They can add, corroborate, refine, conflict or change status, and they can supersede only when they say so explicitly (rule 4). Ingestion order never decides what is current.

## Update rules

For each routed record, in event-date order:

1. **Add.** A new specific becomes a current item with its status, event date and evidence links. History: `added`.
2. **Corroborate.** The same specifics from another source add that source's evidence links to the item. No second item. History: `corroborated`.
3. **Refine.** Compatible added detail amends the item. Both sources stay linked. History: `revised`.
4. **Supersede.** A source states that it replaces, changes or withdraws an earlier position, and its speaker has authority over that choice in the evidence. Move the old item to Superseded and withdrawn with what replaced it, when and by whom. History: `superseded`, or `withdrawn` when the proposer drops their own proposal. Observations and occurrences are never superseded by later observations or measurements; they stay as dated occurrences, while a later observation adds an occurrence or updates the Status item. Only a source correction (Source edit) or an explicit retraction by the observer moves an observation to Superseded and withdrawn.
5. **Later decision, no explicit reference.** The same decider, or someone the evidence shows has authority, makes a different choice on the same question at a later event date. Move the earlier item to Superseded and withdrawn and mark it `(inferred from date order)`. History: `superseded`, with `(inferred from date order)` in What changed.
6. **Conflict.** Anything else that disagrees. Both items stay current with their own status. Add the conflict under Open items and conflicts. A later assistant proposal does not replace an owner's decision. More confident wording does not either. History: `conflict`.
7. **Status change.** Requested, submitted, approved, rejected, completed and verified are separate states, each with its own date and evidence. So are assigned and accepted. Submitted never implies approved. Assigned never implies accepted. Update the status line and keep each earlier state as a bullet with its date and evidence. History: `status`.
8. **Resolve.** A source that settles an open item or conflict marks it resolved with evidence. Delete the resolved item from Open items and conflicts; History keeps it, and do not move it to Superseded and withdrawn. History: `resolved`.

**Late evidence.** A record whose event date is earlier than the page's `evidence_through` uses the same rules. Insert its History row at its own date. Then re-apply, in event-date order, every later record on the same item. If one of them now applies differently, change that row's Change and What changed to match and fix the item. Do not add rows for those later records. With candidate matching and the subject-creation threshold, the store reaches the same active subject pages, current specifics and statuses whichever order the sources arrived in; a page's ID slug comes from the first source that creates it, while later names become aliases.

**Idempotency.** If a page's History already has a row with the record's source sha256 prefix and the same line range, the record changes nothing on that page. The holding page works the same way.

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

- **Status.** The record's status phrase from the allowed vocabulary in [store.md](store.md): `decided by <who>` (which also covers a rule or constraint set by someone the evidence shows owns that service, procedure or domain), `proposed` (or `proposed by <who>`, or `proposed; <who> replied ...`), `stated by <who>`, `requested by <who>`, `accepted by <who>`, `rejected by <who>`, `claimed by <who>`, `withdrawn` (or `withdrawn by <who>`), `deferred` (or `deferred by <who>`), `observed` (or `observed by <who>`), `reported` (or `reported by <who>`), `open`, or `second-hand` (or `second-hand and reported` / `second-hand, reported by <who>`). For a state transition, use the single current state: `requested`, `submitted`, `approved`, `rejected`, `completed`, `verified`, `assigned` or `accepted`, optionally with `by <who>` when known, or combined with `, reported` / `, reported by <who>` (for example `completed, reported by <who>`). Any other status phrase is an error checked by `check_store.py`.
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

- **Source.** A link to the evidence document and the first 12 hex characters of the source's sha256 in a code span. For a change made on the owner's direct instruction in the run, write `owner instruction` and put `-` in Lines.
- **Lines.** One link per line range of the record.
- **Change.** Exactly one of `added`, `corroborated`, `revised`, `superseded`, `conflict`, `resolved`, `status`, `corrected`, `withdrawn`, `moved`, `evidence removed`.
- **What changed.** One short clause naming the item and the change, for example `Row limit 50,000 per export added` or `Nightly batch decision superseded by streaming (inferred from date order)`. Do not restate the record.
- A record usually gives one row per page. A record with two effects on one page, such as superseding one item and adding another, gives one row per effect.

### Retired page

```markdown
---
type: <type>
title: "<current name>"
description: "Merged into <id> on <event date>."
timestamp: <ISO 8601 with offset, last update>
id: <type>/<slug>
aliases: ["<name as a source uses it>"]
status: merged into <id>
scope: []
evidence_through: <latest event date applied>
---

# <title>

Merged into [<title>](<link to page>) on <event date>, <evidence links or "owner instruction">. Its items moved there.

## History
```

For a split, write `split into <id>, <id>` and link each successor.

## Registry, ledger and holding page

Create each file from its template when it is first needed. Keep the front matter and update `timestamp` on every change.

`docs/knowledge/subjects.md`, one row per subject, sorted by ID:

```markdown
---
type: subject-registry
title: "Subject registry"
description: "Every subject page in this knowledge store, with its ID, aliases, scope and status."
timestamp: <ISO 8601 with offset, last update>
---

# Subject registry

| ID | Type | Title | Aliases | Scope | Status | Page |
|---|---|---|---|---|---|---|
| <type>/<slug> | <type> | <title> | <name as a source uses it>; <name as a source uses it> | <broader subject id> | active | [<slug>](<type>s/<slug>.md) |
```

Separate aliases with `; ` and scope IDs with `, `. Write `-` in an empty cell. Status is `active`, `merged into <id>` or `split into <id>, <id>`.

`docs/knowledge/sources.md`, one row per distinct source, sorted by event date, then path, with `unknown` dates last:

```markdown
---
type: source-ledger
title: "Source ledger"
description: "Every source the extraction skills have listed, its stage, its evidence document and the subjects it touched."
timestamp: <ISO 8601 with offset, last update>
---

# Source ledger

| Source | sha256 (first 12) | Event date | Date basis | Ingested | Stage | Evidence | Subjects |
|---|---|---|---|---|---|---|---|
| `<repository-relative path>` | `<sha12>` | <event date> | <date basis> | <ingested date> | <stage> | [<source label>](<link to evidence document>) | <subject ids> |
```

- **Source.** Every path with these bytes, each in a code span, separated by `; `.
- **Date basis.** Where the event date comes from: `stated in text (L4)`, `file name`, `export date` or `unknown`.
- **Ingested.** The date the source was first listed.
- **Stage.** `listed`, `compressed`, `extracted`, `routed`, `superseded by <sha12>`, `removed <date>` or `skipped: <reason>`.
- **Evidence.** A link to the evidence document from here (`../extractions/<path>`), or `-` before Stage 2.
- **Subjects.** Every subject ID whose page History cites this source, separated by `, `, plus `unassigned` if the holding page holds one of its records. `-` if none.

`docs/knowledge/unassigned.md`:

```markdown
---
type: holding-page
title: "Unassigned records"
description: "Actionable records whose subject the evidence does not yet establish."
timestamp: <ISO 8601 with offset, last update>
---

# Unassigned records

| Added | Source | Lines | Record | Candidate subjects | Why unassigned |
|---|---|---|---|---|---|
| <ingested date> | [<source label>](<link to evidence document>) `<sha12>` | [L41-L52](<link to source>#L41-L52) | <record heading> | <subject ids or names> | <reason> |
```

From these three files, an evidence document is `../extractions/<path>` and a raw source is `../../<repository-relative path>`. On every run, check each holding row against the new evidence. When a source establishes the subject, apply the record to that page at its own event date with Change `added`, delete the holding row, and update the ledger row's Subjects.

## Runs

### Before any run

1. Read the ledger, the registry and the holding page if they exist.
2. **Migration.** Find every evidence document under `docs/extractions/` whose sha256 has no ledger row. Add a row with the paths from its front matter `source`, the first 12 characters of its front matter `sha256`, its event date and date basis from its About section, today as Ingested, Stage `extracted`, and its Evidence link. Do not rewrite the document.
3. **Resume.** A row in `listed` needs Stage 1. A row in `compressed` needs Stage 2. A row in `extracted` needs Stage 3. Continue each from its stage. Before Stage 1, check `compressed/` for a compression with that sha256; if one exists and its Read line is complete, set the row to `compressed`.

### Routine ingestion of one new source

1. Stage 1 and Stage 2 as in [store.md](store.md). Stage 2 writes the ledger row as `extracted`.
2. Read the registry, the holding page, and the new evidence document's records and Subjects it names section.
3. For each actionable record, name its subjects, match them against the registry, and decide: an existing subject, a new subject, or the holding page.
4. Group the routed records by subject. For each subject, read only its page, apply its records in event-date order with the update rules, and write the page once. Set `evidence_through` to the latest event date applied, and update `timestamp` and `aliases`.
5. Update the registry, the holding page and the indexes. On each subject type folder's `index.md`, copy every page's front matter `description` word for word whenever the page is created or its `description` changes. Set the ledger row to `routed` and fill its Subjects.
6. Add one bullet to `docs/log.md` under today's `## YYYY-MM-DD` heading naming the sources routed and the subject pages created or changed.
7. Run the finish checklist.

### Backfill of many sources

1. List every file under the given roots with its sha256 and event date. Add a ledger row for each as `listed`. Record skipped files as `skipped: <reason>`.
2. Run Stage 1 on every `listed` row. Many sources can run in parallel. Only the agent running the backfill writes the ledger: after each compression is written, it sets that row to `compressed`.
3. Run Stage 2 per source in event-date order, setting each row to `extracted`.
4. Run Stage 3 per subject, not per source. First route every record of every `extracted` source to its subjects or to the holding page. Then update each subject page once, applying all of its new records in event-date order. Set each source's row to `routed` once all of its records are applied.
5. If the run stops, the next run resumes from the ledger.

### Duplicate ingestion

The same bytes under a new path are one source. Add the path to the ledger row's Source cell, to the compression's `source` list, and to the evidence document's front matter `source` list, and add a `docs/log.md` bullet `Duplicate of <sha12> at <path>`. Nothing else changes. A record whose source hash and line range already appear in a page's History changes nothing.

### Source edit

The ledger shows a known path with a new hash.

1. Set the old row's Stage to `superseded by <sha12>`, replace its Evidence link with plain text `<path> (rewritten for <sha12>; earlier text in git)` so the old row does not link the rewritten document, and add a row for the new hash as `listed`.
2. Re-run Stages 1 and 2 in place.
3. For each subject in the old row's Subjects, re-check every item that cites the old hash. Point its line links at the new text; re-pointing line links without changing any specific needs no History row. Revise changed specifics with a `corrected` History row that cites the new hash. Move items that lost their only support to Superseded and withdrawn with a `corrected` row.
4. In History rows that cite the old hash, replace each line link with its plain text, such as `L120-L130`. The links would now point into the edited text.
5. Route new records as in routine ingestion.

Git keeps the earlier text when the source is committed. If it is not committed, add `earlier version not retained` to the old row's Date basis.

### Source deletion

Only on the owner's explicit request naming the source.

1. Set the ledger row's Stage to `removed <date>`.
2. For each subject in its Subjects, remove from the current state every item whose only support was that source, with an `evidence removed` History row. Remove that source's evidence links from items that keep other support.
3. If the reason is privacy, also delete its compression and evidence document, and write What changed without restating the removed content.
4. Replace each link to a deleted file with its plain text, in History rows, the holding page, the ledger and other evidence documents. `check_store.py` lists the links that no longer resolve.
5. Tell the owner that git history still holds the old text, and that erasing it needs a separate history rewrite they authorize.

### Rebuild of one subject

1. Take every source whose ledger Subjects include the subject.
2. Read their records from the evidence documents, apply them to an empty page of the same ID in event-date order with the update rules, and carry over the `owner instruction` rows from the old History.
3. Keep the Ingested date of each History row that already existed with the same source and lines.
4. Write the rebuilt page in place and report the differences against the old page, especially specifics that one version has and the other lacks.

A rebuild never touches raw sources or evidence documents. A rebuilt page is current as of its latest evidence, not a timeless truth.

### As-of reconstruction

There is no query service. To find what was current on a date, read History up to that date with the Superseded and withdrawn section. To find what the knowledge base said on a date, use `git log` and `git show` on the page.

## Consumers

Coding and enterprise-automation agents read the same pages. Do not write a copy per role.

- A coding agent starts at a feature page: Current state, Constraints and procedures that apply, Validation, and Open items and conflicts. It follows a procedure link only when its task includes that procedure.
- An enterprise-automation agent starts at a procedure page and the Ownership, handoffs and work status section of the features it serves.
- Neither role owns a subject. Relevance does not grant access. The store records access restrictions that sources state. The repository's own permissions are the only enforcement.

## Finish checklist

1. Every routed record is on a subject page or the holding page, and every page you changed has a History row for each change.
2. The registry, the ledger and the indexes list every page and source you added or changed. `docs/index.md` links `knowledge/index.md`.
3. Run the checker in this skill's `scripts/` folder from the repository root, for example `python3 -I .claude/skills/extract-meeting-notes/scripts/check_store.py --root .`, and fix every error it reports. Read each warning and fix it or say why it stays.
4. Report the sources processed, the subject pages created or updated, the items left on the holding page, and the ledger's counts by stage.
