# Store: compressions and extraction documents

Both extraction skills write the same two stores, so sessions, chats, documents and meeting notes end up in one place. The raw sources stay unchanged and remain the complete copy. Use the locations below unless the user or the project's instructions name others.

| Store | Location | What it is |
|---|---|---|
| Compressions | `compressed/` at the repository root, mirroring each source's path: `session-transcripts/11-17-2026/01-setup-mac.md` becomes `compressed/session-transcripts/11-17-2026/01-setup-mac.md`. | Stage 1. One file per distinct source, written from that source alone. Keep them: later runs read them. Commit them only if the user asks. |
| Extraction documents | `docs/extractions/`, mirroring each source's folder. When sources sit under a folder whose only job is to hold raw material, such as `source-material/extracted/`, the mirror starts below it. | Stage 2. One document per distinct source, built from the compressions, with shared material held once and the sources linked to each other. |

Run stage 1 for every source in the request, then stage 2 once over the new or changed compressions.

## Stage 1: compress each source

1. Take the sha256 of every file. Same bytes under several paths are one source: compress it once, at the mirror of the first path in sorted order, and list every path. If a compression with that sha256 already exists, add any new path to its `source` list and stop. Skip archives whose entries are all present unpacked, and tooling or instruction files that are not sessions, conversations, meetings or research material.
2. Read the whole source, in windows for a long file. If you must stop early, write what you have and record how far you read; the next run continues from there.
3. Write the compression. It uses only this source: no comparisons with other files.

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

## Not held here

| Lines | Why |
|---|---|
| 67-81 | Restates L23-53 in prose; held in "<record heading>" |
```

Omit a section that would be empty. Never write "none".

### Records

- **Order.** Follow the source. When a later line says it changes or withdraws an earlier position, mark the earlier record `replaced by L..` and keep it. If you only judge that a later line moved on, link it as `see L..` instead.
- **One record per point.** A point repeated in the source is one record carrying every line link.
- **Specifics.** Keep every name, identifier, number, date, version, path, command, test name, error text, URL, table row, procedure step and reason. Hold a table as a table, row by row. Hold a diagram as its nodes and edges. Mark worked examples and hypotheticals `illustrative`.
- **Quote** the user's own words verbatim and in full (every prompt, typos kept), exact strings, and wording that defines a boundary. Put quoted Markdown links and other exact strings in code spans, so they do not render as live links. State everything else in your own words, with all its specifics, in fewer words than the source. A table whose rows are the specifics may be copied once as a table; do not also restate it in prose. If a record is as long as the passage it covers, you are re-quoting: cut it to the specifics.
- **Links.** Relative path from the file you are writing to the source, with spaces written as `%20`, `(` as `%28` and `)` as `%29`, and a line anchor `#L12` or `#L12-L30`. A record that cites several ranges gives one link per range.
- **Your own additions.** Keep hedging words from the source inside paraphrases ("automatically", "may", "for now"). Label arithmetic, inference or a pattern you draw yourself `(inferred)`.
- **Who.** The speaker as the source labels them (`user`, `assistant`, `agent`, a named person), or `tool`, `document` (text written as a document, with its author if known), `exporter` (notes added by the export), or `pasted by <who>` (material someone pasted from elsewhere; it is not their own words unless they say they wrote it). When one fact in a record comes from another speaker, tag that bullet, for example `(user, L172)`.
- **Status.** One short phrase:
  - `proposed`.
  - `decided by <who>`, `accepted by <who>` or `rejected by <who>`: only when that person's own words, linked in the record, make, accept or reject this specific choice. Keep their hedges: `rejected by user, tentatively ("feel free to correct me", L290)`. A blanket go-ahead to a plan of many items accepts none of them singly; write `proposed; <who> replied "ok proceed" (L459)`. An objection, complaint or correction is not a decision.
  - `stated by <who>`: a position the person gives as their current understanding while still asking for comment.
  - `requested by <who>`: an instruction or request.
  - `withdrawn` (the proposer dropped it), `deferred`.
  - `open`: unresolved as of the last relevant line. Before writing an open item, check the later turns for the user's reaction and for a change of plan.
  - `replaced by L..`.
  - `observed` (the source shows the result) or `reported` (someone says it happened).
  - `illustrative`, or `second-hand` (restates another source or a recollection).
  - `claimed by <who>`: a research or method claim the source asserts. It says who asserts it, not that it is established.
- **Research and method claims.** When the user asks for research or method knowledge, give each claim its own record with four labelled bullets: `Claim` (as stated, with numbers and scope), `Support` (the experiment, data, citation or argument the source gives, with its exact locator), `Applies when` (stated assumptions and conditions) and `Limits` (stated limitations, negative results and counterevidence). Write `not stated` for a bullet the source leaves empty. Status is `claimed by <who>`, or `second-hand` when the source reports another work it does not contain; `observed` and `decided by` keep their meanings and are not used for a claim merely because the source sounds certain. Do not merge a source's claim with a later result that tests it: link them with `see L..`.
- **Parts.** Material with other speakers or dates inside the source, such as a pasted transcript, gets its own `## Records: <part>` section.
- **Captured source views.** A tool read or pasted excerpt of an older session inside a new hook-captured session is a view of that earlier source, not a new occurrence. In About, identify the containing session and the earlier source/session where available. In Records, distinguish the tool or person presenting the text from its original speakers. Keep the event's original date and status. Record the containing source's exact span without pretending it is the original's line range. Preserve new analysis, corrections, decisions, actions and outcomes from the containing session; do not discard the whole session just because some text repeats. If only the captured view is available, say so and leave original-source coverage unknown.
- **Leave out** formatting, headings, progress chatter, tool noise with no content, and repeats. Give one Not held row per kind of material left out, listing its line ranges, not one row per span.
- **Credentials.** Omit their values.

### Reference notes

Notes of third-party material, such as course or product lecture notes with no records of the user's work, get a short compression. When the user asks to keep the research or method knowledge itself, this short form is not enough for the parts that carry it: write those claims as records under "Research and method claims" above, and keep the section map for the rest. About gives the identity (course or product, author, how the notes were made, their date), caveats such as unexecuted code, locked parts, stated gaps and the note-taker's own reservations, and Read. Records holds one record: a section map, a table with columns `Lines | Section | Main terms and claims`, with every row filled. The teaching itself is one Not held row, held in the source.

## Stage 2: build the extraction documents

Take every compression with no extraction document of the same sha256 under `docs/extractions/` (search front matter for `sha256: <hash>`), and every compression rewritten since its document was built.

1. **Place and name.** Put the document at the mirrored folder. Session and meeting transcripts keep their file name. Other sources take a short lowercase-hyphen slug of their title, plus the version if they state one, because raw file names often mislead: `Model_Training (4).md` may be the newer revision, and unrelated files can share one name. A name is set once and never recomputed.
2. **Find related sources.** Search `docs/extractions/` and the other new compressions for the sha256; for each name under "Files it names", with copy counters such as `(1)` or `(2)(1)` stripped; for the title; for a distinctive sentence from each user prompt, which re-exports of one conversation share; and for each sentence the source quotes, which leads to the source it was quoted from. Matching finds copies but not rewordings, so also read the About section and record headings of every other source in the same folder and of every source this one names, and ask of each pair: does one restate, revise, adapt, continue, contradict or judge the other? Documents revised or adapted from the same base are compared with each other too: list every pair first, siblings included, then compare each pair responsibility by responsibility (each component, owner, tool or choice that either names); every disagreement is a conflict. Read two tables on the same subject row by row: a reworded table is a restatement. A document that names its base only vaguely ("the reference document") is matched by its structure and subject, not left as an unknown name.
Before deduplicating, also inspect tool-read and pasted-source passages in hook-captured sessions. Use their original paths/session IDs and actual matching content to locate earlier holders, even when the containing files have different hashes. A captured view gets a `Quotes` relation to the original when available and a Not held row for repeated specifics; keep its genuinely new records. If a view repeats another view, follow the provenance to the available original without inventing a missing link. Never count those copies as independent events, agreement, recurrence or corroboration.

3. **Hold once, by specifics.** When a passage has the same specifics as one already held (a verbatim copy, containment, a re-export, a quotation, a second-hand summary, or a light rewording in another version), one document holds it and the other gets a Not held row: both line ranges, a link to the holder, and only what differs. When the specifics differ, both documents hold their own, and the later one adds `Restates <link> L..` with what it dropped, added or changed. The holder is the document already written. Within one run it is the fuller copy, or the earlier one if they are equal. A holder never changes. A quotation is held by the source it was quoted from; the quoting document keeps its `Quotes` line and a Not held row. Hold-once applies inside a changed section too: rows and lines that are word for word another version's are Not held. A table that repeats another document's rows and adds some holds only the added rows, with one Not held row for the repeated ones. When nothing differs, the Not held row says only where the passage is held. When a whole source is contained in another, such as an earlier cumulative export of one session, its document keeps About, the relation line and one Not held row for the whole range, and drops its own Files it names list.
4. **Relations.** Write these in both documents, because otherwise the earlier page reads as current, unjudged or complete:
   - `Revises` / `Revised by`: a later version of the same document.
   - `Supersedes` / `Superseded by`: a different source replaces it.
   - `Adapted from` / `Adapted by`: a separate document written from it as a base.
   - `Another export of`: two exports of the same conversation or session, including cumulative exports.
   - `Continues` / `Continued in`: a later part of the same session or conversation.
   - `Conflicts with`: name each point of disagreement.
   - `Quotes`: copies a passage of the other, including a pasted excerpt or appendix.
   - `Produced in` / `Produced`, `Judged in` / `Judges`: a source made the other or gives a verdict on it. Link the words of the person whose verdict it is.

   Give both line ranges and one clause of evidence. When you name turns or sections, use the sources' own headings and check the numbers in both sources. A `Conflicts with` line, in both documents, keeps each side's status (`decided by user`, `proposed`) and says whether anyone accepted either side. `Quotes`, `Restates` and `Mentions` are written once, by the source that makes them. Leave out names that occur only in lines held elsewhere. Names that match nothing held become `Names, not held at extraction: <name> (L..)`; that line stays true when the file arrives later.
5. **Write the document.** OKF front matter: `type: source-extraction`, `title`, `description`, `timestamp` (ISO 8601 with offset), `source`, `sha256`. Sections: About this source; Related sources (the relations, then the Mentions and Names lines made from the compression's Files it names); Records; Not held here. Copy the records from the compression with links rewritten for the new location, and rewrite references to compression sections ("Files it names", "this file") to fit the document. Give several exports of one session distinct titles, for example by adding the part. Replace records held elsewhere with Not held rows that link the holder. Add a `Held at` column to the Not held table: a link to the holding document, `this document`, or `source` when the material is held only in the raw source. Every cross-document reference is a working relative link: before finishing, search the documents you wrote for placeholders or shorthand and for links whose file does not exist, and fix them.
6. **Reverse lines.** Add the matching line to each earlier document a relation touches. Do not rewrite its records: they still describe their unchanged source.
7. **Navigation.** Every folder under `docs/` has an `index.md` (no front matter) listing only its immediate children as `- [Title](file.md): <description>`, with subfolders linked to their `index.md`. Create missing indexes up the tree, including the `docs/index.md` entry for `extractions/`. Add one bullet to `docs/log.md` under today's `## YYYY-MM-DD` heading, newest first, naming the sources added or re-extracted, the skill used, any documents that got reverse lines, and any sources left out on purpose (for example an archive whose entries are unpacked, or helper transcripts the user did not ask for) with the reason.

### Re-extraction

When a source is compressed again with an improved skill, rewrite its compression and its document in place; git keeps the old text. Keep the holders and the relation lines, re-checking them against the new records. Log the re-extraction.
