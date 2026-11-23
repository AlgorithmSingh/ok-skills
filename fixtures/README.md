# Public extraction fixtures

Each case supplies synthetic sources, an ingestion order, behavioral assertions and expected answers. Copy only the named source files into an empty target repository for each run. Keep this oracle outside the extractor’s input. Use the named extraction skill with its bundled checker. Then give a fresh reader only the resulting `docs/knowledge/` tree and the questions, withholding the expected answers. Compare each answer and its qualifications with the oracle. A missing fact and an unsupported upgrade both fail the case.

- [Plan approval and individual acceptance](plan-acceptance/README.md)
- [One term in two workflows](scope-collision/README.md)
- [A hook captures an older session](captured-view/README.md)
- [Interrupted ingestion and a late reversal](interrupted-reversal/README.md)
- [Decision authority in minutes](minutes-authority/README.md)
- [Original, quotation and independent evidence](reverse-arrival/README.md)

For an already populated store with working line citations, see the [release review](../examples/mini-store/README.md).
