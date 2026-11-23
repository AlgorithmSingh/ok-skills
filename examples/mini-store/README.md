# Export release review

Follow a single synthetic meeting through all three stages.

1. The [minutes](raw/release-minutes.md) identify the release owner, the note-taker and the environment tested.
2. The [compression](compressed/raw/release-minutes.md) records the complete read. The [evidence document](docs/extractions/raw/release-minutes.md) attributes each record to its source lines.
3. Browse the [registry](docs/knowledge/subjects.md) and [ledger](docs/knowledge/sources.md). The [procedure](docs/knowledge/procedures/export-approval.md) gives the production prerequisite. The [feature page](docs/knowledge/features/export-preview.md) gives the staging result and its limit. Both History tables cite the same minutes.

From the clone root run `python3 -I -B extract-session-details/scripts/check_store.py --root examples/mini-store`. The example includes its compression so you can inspect the read checkpoint.
