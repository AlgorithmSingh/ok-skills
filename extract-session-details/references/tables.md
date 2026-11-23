# Registry, ledger and holding page

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
