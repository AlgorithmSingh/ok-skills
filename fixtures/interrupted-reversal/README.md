# Interrupted ingestion and a late reversal

Route initial.md and later.md first. During Stage 1 of amendment.md pause after line 2. Supply a byte-identical alias of amendment.md before resuming. Inspect the checkpoint, then finish and rerun.

- [initial.md](initial.md)
- [amendment.md](amendment.md)
- [later.md](later.md)

## Pass/fail checks

- Pass if the partial read records 2 of 4, stays listed under one hash, and has no evidence document. Fail if the alias bypasses the unread tail.
- Pass if the resumed run processes lines 3–4, keeps both paths on one row and inserts the June 3 decision before the June 5 proposal. Fail if the later proposal replaces the seven-day decision.
- Pass if a rerun preserves one History row per effect and all original ingestion dates. Fail if it duplicates the reversal.

### Editing an alias after routing

In a copy of the finished store, edit only the alias, changing seven days to five and the event date to June 4. Pass if the original path still resolves to a seven-day record on its existing hash and the edited path has its own hash and five-day record. Fail if editing the alias rewrites the original’s evidence, redirects its citations to changed bytes or leaves both paths on a stale row.

## Consumer questions

For the original, unedited run, answer from the resulting `docs/knowledge/` alone.

**What retention is authorized for pilot exports?** Seven days. Thirty was replaced and fourteen remains a proposal.

**Has the deployed value been verified?** No. The June 3 source says it was not checked.
