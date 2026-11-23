# Store: compressions, extraction documents and subject pages

Both extraction skills write the same stores, so sessions, chats, documents and meeting notes end up in one place. The raw sources stay unchanged and remain the complete copy. Work in three stages: Stage 1 compresses each source on its own, Stage 2 builds one evidence document per source, and Stage 3 routes the records into subject pages. This file covers intake and Stage 1. Open [evidence.md](evidence.md) at Stage 2. [knowledge.md](knowledge.md) covers Stage 3, the registry, the ledger and the holding page. Use the locations below unless the user or the project's instructions name others.

| Store | Location | What it is |
|---|---|---|
| Compressions | `compressed/` at the repository root, mirroring each source's path: `session-transcripts/11-17-2026/01-setup-mac.md` becomes `compressed/session-transcripts/11-17-2026/01-setup-mac.md`. | Stage 1. One file per distinct source, written from that source alone. Keep them: later runs read them. Commit them only if the user asks. |
| Extraction documents | `docs/extractions/`, mirroring each source's folder. When sources sit under a folder whose only job is to hold raw material, such as `source-material/extracted/`, the mirror starts below it. | Stage 2. One evidence document per distinct source, built from the compressions, with shared material held once and the sources linked to each other. |
| Subject pages | `docs/knowledge/<type>s/<slug>.md` | Stage 3. The maintained knowledge for one project, service, feature, procedure, decision or recurring problem, across every source. See [knowledge.md](knowledge.md). |
| Registry | `docs/knowledge/subjects.md` | Stage 3. Subject IDs, titles, aliases, scope and status. |
| Ledger | `docs/knowledge/sources.md` | Stages 1 to 3. Every source, its sha256, event date, stage, evidence document and the subjects it touched. |
| Holding page | `docs/knowledge/unassigned.md` | Stage 3. Actionable records whose subject the evidence does not establish. |

## Intake and resume

Use a stable, repository-relative raw source. For an external chat or JSONL log, save an authorized, readable redacted export in the target repository, then hash and cite that export. If storage is restricted, report the gap. Keep compressions across runs. In a fresh clone without an uncommitted compression, regenerate it from the same raw bytes before using it. Track compressions in Git only on explicit request.

Look up the supplied paths and full hashes, then create a `listed` ledger row for each new byte sequence using the [table templates](tables.md). Use the source event date (or `unknown`) and the owner/project time zone for ingestion dates, falling back to UTC. A changed path follows the [source-edit rule](maintenance.md) before any duplicate shortcut. If an existing evidence document lacks a ledger row, use the migration procedure there. Update directory indexes and the documentation log only where the target repository uses those conventions.

## Stage 1: compress each source

1. Group byte-identical paths and write one compression, mirroring the first sorted path under `compressed/`. Keep all aliases in the ledger and in each existing document’s `source` list. Skip unpacked duplicate archives and out-of-scope tooling with a ledger stage of `skipped: <reason>`.
2. Read in order. On interruption, save the contiguous coverage as `Read: lines 1-N of M (unfinished)` and leave the row `listed`. A matching hash, even at another path, resumes the unread lines. Check the hash again on resume.
3. Build the records from this source alone. Only when the recorded coverage reaches the last line and the unfinished marker is cleared may the coordinator advance the row to `compressed`. A verified complete duplicate updates aliases and resumes any pending stage. A `routed` duplicate with complete coverage needs no new routing. Resume `compressed` rows at Stage 2 and `extracted` rows at Stage 3. If an advanced row points to an unfinished read, return it to `listed` and reconcile any premature outputs before proceeding.
4. Advance only after each stage’s files are durable. Serialize ledger, registry, relation and subject updates across concurrent runs. Parallel readers may write distinct Stage 1 compressions.

### Compression format

```markdown
---
title: "<the source's own title, plus its version if it states one>"
description: "<one sentence: what kind of source it is, its date, and what it covers>"
source:
  - <repository-relative path>
sha256: <64 hex characters>
---

# <title>

## About this source

- What it is, who speaks, and how each speaker is labelled. Which parts the user wrote.
- Dates and their basis (stated in the text, export date, file name, or unknown).
- What the source says is missing or condensed.
- Read: lines 1-N of M (add "unfinished" until N = M).

## Records

### <the point, stated as a sentence>
[L121-L131](<relative link to the source>#L121-L131) · <who> · <status>
- <every specific, stated once>

## Files it names

- `<exact file or source name>` (L13): <what the source says about it>

## Subjects it names

- <name as the source states it> (L13, L40-L52): <feature, service, project, procedure, decision or recurring problem>; records: "<record heading>", "<record heading>"

## Not held here

| Lines | Why |
|---|---|
| 67-81 | Restates L23-53 in prose; held in "<record heading>" |
```

Omit a section that would be empty. Never write "none".

### Subjects it names

List each feature, service, project, procedure, decision or recurring problem the source names, under the name the source uses, with its lines and the headings of the records that concern it. Name each subject the way this source does; do not look it up anywhere else. Several names for one thing in this source go on one line when the source itself says they are the same. Leave out things named only in background, illustrative or held-elsewhere material. Stage 3 uses this list to route the records.

### Records

- **Order.** Follow the source. When a later line says it changes or withdraws an earlier position, mark the earlier record `replaced by L..` and keep it. If you only judge that a later line moved on, link it as `see L..` instead.
- **One record per point.** Reproductions of one statement or observation are one record carrying every line link. Keep independent observations as distinct records, even within one source.
- **Specifics.** Keep every name, identifier, number, date, version, path, command, test name, error text, URL, table row, procedure step and reason. Hold a table as a table, row by row. Hold a diagram as its nodes and edges. Mark purely illustrative worked examples and hypotheticals `illustrative`.
- **Workflow meaning.** Keep a workflow-specific definition or boundary with the decision, requirement, procedure, correction, or other record it qualifies whenever it changes how the record is understood or applied. Preserve the source's term, its meaning, who stated it or what showed it, and the conditions under which it applies. Label inferred meanings `(inferred)` beside the source's words or observation and keep any unresolved scope visible.
- **Applications.** When a source provides a useful example of applying a rule, link the example to the rule in the evidence document using the existing record text and links. Keep the question or task, the material conditions, the stated expected or observed result, what the linked evidence establishes, and any material unknowns exposed by the source. Distinguish an answer confirmed by the authority for the rule from a demonstrated or reported outcome. Preserve the scope of the confirmation or observation, including what was left untested. Use an example as authority for a rule only if the source establishes that authority.
- **Quote** the user's own words verbatim and in full (every prompt, typos kept), exact strings, and wording that defines a boundary. Put quoted Markdown links and other exact strings in code spans, so they do not render as live links. State everything else in your own words, with all its specifics, in fewer words than the source. A table whose rows are the specifics may be copied once as a table; do not also restate it in prose. If a record is as long as the passage it covers, you are re-quoting: cut it to the specifics.
- **Links.** Relative path from the file you are writing to the source, with spaces written as `%20`, `(` as `%28` and `)` as `%29`, and a line anchor `#L12` or `#L12-L30`. A record that cites several ranges gives one link per range. Place a verbatim quotation or exact backticked snippet directly beside its line link. Use ordinary unquoted prose for paraphrases. Separate unrelated inline identifiers from citations with explanatory text.
- **Your own additions.** Keep hedging words from the source inside paraphrases ("automatically", "may", "for now"). Label arithmetic, inference or a pattern you draw yourself `(inferred)`.
- **Who.** The speaker as the source labels them (`user`, `assistant`, `agent`, a named person), or `tool`, `document` (text written as a document, with its author if known), `exporter` (notes added by the export), or `pasted by <who>` (material someone pasted from elsewhere; it is not their own words unless they say they wrote it). When one fact in a record comes from another speaker, tag that bullet, for example `(user, L172)`.
- **Status.** One short phrase from this list (any other phrase on a subject page is an error):
  - `proposed`, or `proposed by <who>`.
  - `decided by <who>`, `accepted by <who>` or `rejected by <who>`: only when that person's own words, linked in the record, make, accept or reject this specific choice. `decided by <who>` also covers a rule or constraint set by someone the evidence shows owns that service, procedure or domain. Keep their hedges: `rejected by user, tentatively ("feel free to correct me", L290)`. A blanket go-ahead to a plan of many items accepts none of them singly; write `proposed; <who> replied "ok proceed" (L459)`. An objection, complaint or correction is not a decision. Minutes that identify the decision maker, their authority and the specific choice use `decided by <who> (per minutes by <note-taker>)`. A suggestion or unattributed recollection stays proposed or reported.
  - `stated by <who>`: a position the person gives as their current understanding while still asking for comment.
  - `requested by <who>`: an instruction or request.
  - `withdrawn` or `withdrawn by <who>` (the proposer dropped it), `deferred` or `deferred by <who>`.
  - `open`: unresolved as of the last relevant line. Before writing an open item, check the later turns for the user's reaction and for a change of plan.
  - `replaced by L..` (in evidence documents), or `superseded` / `superseded (inferred from date order)` (on subject pages).
  - `observed` (the source shows the result) or `reported` (someone says it happened), optionally with `by <who>`.
  - State transitions: `requested`, `submitted`, `approved`, `rejected`, `completed`, `verified`, `assigned` or `accepted`, each optionally with `by <who>` when known, or combined with `, reported` / `, reported by <who>` (for example `completed, reported by <who>`).
  - `illustrative` and `background` are evidence-only labels for examples and general reference material. Use `second-hand` (restates another source or a recollection, optionally `second-hand and reported` with optional `by <who>`, or `second-hand, reported by <who>`).
  - `candidate`: a reusable lesson inferred from an episode. Keep the supporting observations separate.
  - `claimed by <who>`: a research or method claim the source asserts. It says who asserts it, not that it is established.
- **Research and method claims.** When requested or when a research or method claim materially informs a decision, design or comparison, give each claim its own record with four labelled bullets: `Claim` (as stated, with numbers and scope), `Support` (the experiment, data, citation or argument the source gives, with its exact locator), `Applies when` (stated assumptions and conditions) and `Limits` (stated limitations, negative results and counterevidence). Write `not stated` for a bullet the source leaves empty. Status is `claimed by <who>`, or `second-hand` when the source reports another work it does not contain; `observed` and `decided by` keep their meanings and are not used for a claim merely because the source sounds certain. Do not merge a source's claim with a later result that tests it: link them with `see L..`.
- **Parts.** Material with other speakers or dates inside the source, such as a pasted transcript, gets its own `## Records: <part>` section.
- **Captured source views.** A tool read or pasted excerpt of an older session inside a new hook-captured session is a view of that earlier source, not a new occurrence. In About, identify the containing session and the earlier source/session where available. In Records, distinguish the tool or person presenting the text from its original speakers. Keep the event's original date and status. Record the containing source's exact span without pretending it is the original's line range. Preserve new analysis, corrections, decisions, actions and outcomes from the containing session; do not discard the whole session just because some text repeats. If only the captured view is available, say so and leave original-source coverage unknown.
- **Leave out** formatting, headings, progress chatter, tool noise with no content, and repeats. Give one Not held row per kind of material left out, listing its line ranges, not one row per span.
- **Credentials.** Omit their values.

### Reference notes

Notes of third-party material, such as course or product lecture notes with no records of the user's work, get a short compression. When either research-claim trigger applies, this short form is not enough for the parts that carry it: write those claims as records under "Research and method claims" above, and keep the section map for the rest. About gives the identity (course or product, author, how the notes were made, their date), caveats such as unexecuted code, locked parts, stated gaps and the note-taker's own reservations, and Read. Records holds one record: a section map, a table with columns `Lines | Section | Main terms and claims`, with every row filled. The teaching itself is one Not held row, held in the source.
