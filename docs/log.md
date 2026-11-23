# Documentation log

## 2026-11-22

- Split the extraction references by stage, documented replay and Git review, and added checker tests, a worked store and six public behavioral fixtures. Updated skill routing, essay guidance and repository-wide checks (`scripts/check_repo.py`).
- Added [evaluation prompts and checks](../well-defined-objectives/evals/evals.json) for turning vague requests into verifiable objectives.
- Added `AGENTS.md` requiring the repository to stay standalone and free of machine-local paths or private references. Added [Google Knowledge Catalog vs. ok-skills extraction](essays/knowledge-catalog-vs-extraction-skills.md) and linked it from `README.md` and `docs/essays/index.md`.
- Updated `extract-session-details` and `extract-meeting-notes` with workflow-scope checks, local-definition capture and linked rule-application rules.
- Updated `extract-session-details` and `extract-meeting-notes` with the three-stage knowledge store (`references/knowledge.md`, updated `references/store.md`, `scripts/check_store.py`) and contract fixes, keeping the captured-view and research-claim additions.

## 2026-11-19

- Added [well-defined-objectives](../well-defined-objectives/SKILL.md) for writing one-sentence objectives and pass-or-fail success criteria without prescribing a method.
- Updated the agent context essay's run section: the extraction skills now store every detail in per-source compressions and linked extraction documents instead of returning a brief.

## 2026-11-17

- Linked the separate session and meeting extraction skills from the agent context essay.
- Refocused the agent context essay on extraction content for coding, SRE and assistant personas.
- Added a working extraction brief and explicit use, borrow, defer and outside-scope tool decisions; removed retrieval, ranking and storage-system design.

## 2026-11-16

- Added `docs/` as an OKF v0.1 bundle with an essays section.
- Added the essay "Agent context strategy: extraction, memory and enrichment".
