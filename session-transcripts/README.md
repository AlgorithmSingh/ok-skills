# Session transcripts

Save sessions in `session-transcripts/<MM-DD-YYYY>/NN-<topic>-<machine>.md`, numbered within the date folder. Use `mac`, `windows`, or the remote host name. Later captures of the same session add `-part-2`, `-part-3`. Helper transcripts go in `NN-<topic>-subagents/` next to their parent.

The exporter preserves prompts and replies, condenses tool activity, drops hidden thinking, and redacts credential-shaped strings. It is copied from [semgrep-joern-signals](https://github.com/AlgorithmSingh/semgrep-joern-signals/tree/main/session-transcripts).

```sh
python3 session-transcripts/export_transcript.py \
  session-transcripts/<MM-DD-YYYY>/NN-<topic>-mac.md \
  "$PI_SESSION_FILE"
```

Add `--secrets-from <file>` when a session handled credentials. Review the export for private material before publishing. Commit only transcript paths for transcript saves, then pull with rebase and push to `main`.
