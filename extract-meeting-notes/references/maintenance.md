# Store maintenance

## Migration

Find evidence documents whose hash has no ledger row. Use their source paths, sha256 prefix, event date and date basis to create rows, with today as Ingested. For verified complete reads, set Stage to `extracted` and link the existing evidence document. For incomplete or unknown coverage, keep the row `listed` and resume Stage 1 before rebuilding evidence.

## Backfill of many sources

1. List every file under the given roots with its sha256 and event date. Add a ledger row for each as `listed`. Record skipped files as `skipped: <reason>`.
2. Run Stage 1 on every `listed` row. Many sources can run in parallel. Only the agent running the backfill writes the ledger: it advances a row only after full coverage is recorded. Serialize Stage 2 relation edits and Stage 3 shared writes under a single coordinator.
3. Run Stage 2 per source in event-date order, setting each row to `extracted`.
4. Run Stage 3 per subject, not per source. First route every record of every `extracted` source to its subjects or to the holding page. Then update each subject page once, applying all of its new records in event-date order. Set each source's row to `routed` once all of its records are applied.
5. If the run stops, the next run resumes from the ledger.

### Duplicate ingestion

Use the alias and full-read checks in [store.md](store.md). An unfinished duplicate resumes Stage 1. For complete duplicates, repair alias lists and resume any pending stage.

### Source edit

Re-hash every alias on the old row before updating it. If unchanged aliases remain, keep the old row active with those paths, retain its records and History, and repair raw citations to an unchanged alias. Remove only the edited path from the old compression and evidence source lists. Move a compression occupying the edited path’s mirror to the remaining alias’s mirror and recalculate its relative links from that location. Give the edited path its own row, compression and collision-safe evidence path (or join an existing row with those bytes). Route its changes on their evidence. Do not mark the unchanged aliases superseded. When several aliases changed, group the changed paths by their actual new hashes. Use the following whole-source replacement only when no alias retains the old bytes.

1. Set the old row's Stage to `superseded by <sha12>`, replace its Evidence link with plain text `<path> (rewritten for <sha12>; earlier text in git)` so the old row does not link the rewritten document, and add a row for the new hash as `listed`.
2. Re-run Stages 1 and 2 in place.
3. For each subject in the old row's Subjects, re-check every item that cites the old hash. Point its line links at the new text; re-pointing line links without changing any specific needs no History row. Revise changed specifics with a `corrected` History row that cites the new hash. Move items that lost their only support to Superseded and withdrawn with a `corrected` row.
4. In History rows that cite the old hash, replace each line link with its plain text, such as `L120-L130`. The links would now point into the edited text.
5. Route new records as in routine ingestion.

Git retains previously committed versions. When the earlier bytes were never committed or retained, say `earlier version not retained` in the old row’s Date basis and its rewritten Evidence note.

### Source deletion

Only on the owner's explicit request naming the source.

1. Set the ledger row's Stage to `removed <date>`.
2. For each subject in its Subjects, remove from the current state every item whose only support was that source, with an `evidence removed` History row. Remove that source's evidence links from items that keep other support.
3. If the reason is privacy, also delete its compression and evidence document, and write What changed without restating the removed content.
4. Replace each link to a deleted file with its plain text, in History rows, the holding page, the ledger and other evidence documents. `check_store.py` lists the links that no longer resolve.
5. If a removed file was committed, tell the owner that Git history retains it and that erasing history requires separate authorization. Check the owner journal for quotations covered by the deletion request before any rebuild.

### Rebuild of one subject

1. Gather the subject’s active evidence, retained historical versions, existing History and journal entries. Reconcile legacy manual edits into the owner journal before replacing the page.
2. Read their records from the evidence documents, apply them to an empty page of the same ID in event-date order with the update rules, interleaved with the full dated owner instructions, clarifications and curated examples. Preserve historical rows, including those for retired sources, and their original Ingested dates.
3. Keep the Ingested date of each History row that already existed with the same source, item and effect, even if the cited span shifted.
4. Write the rebuilt page in place and report the differences against the old page, especially specifics that one version has and the other lacks.

A rebuild never touches raw sources or evidence documents. A rebuilt page is current as of its latest evidence, not a timeless truth.

### As-of reconstruction

There is no query service. To find what was current on a date, read History up to that date with the Superseded and withdrawn section. To find what the knowledge base said on a date, use `git log` and `git show` on the page.

## Re-extraction

When a source is compressed again with an improved skill, rewrite its compression and its document in place; Git retains any committed versions. Keep the holders and the relation lines, re-checking them against the new records. Log the re-extraction. Set its ledger row back to `extracted`. In Stage 3, re-check every item that cites its hash using the source-edit checks above, then route its records; use the per-effect [idempotency rule](knowledge.md), repairing shifted locators.

## Retired page

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
