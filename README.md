# ok-skills

Reusable skills and prompts for coding assistants.

## Skills

- [well-defined-objectives](well-defined-objectives/SKILL.md): Turn a vague request into a one-sentence objective with success criteria anyone can check, with the method left open. Includes coding examples and the pattern for "find out" tasks.
- [extract-session-details](extract-session-details/SKILL.md): Extract prior agent work, user steering, verified outcomes and handoff state from session transcripts and tool traces.
- [extract-meeting-notes](extract-meeting-notes/SKILL.md): Extract decisions, commitments, procedures and open work from meeting notes or transcripts.
- [project-memory-investigation-prompt](project-memory-investigation-prompt/SKILL.md): Prepare an evidence-backed session-history investigation for any project, using three memory types and seven categories. Includes a portable template and initial/update modes. Analysis is committed in the target project's own repository; preparation does not launch extraction.
- [boss-brief](boss-brief/SKILL.md): Give a non-technical owner a plain-English status update and one clear next step.
- [direct-answers](direct-answers/SKILL.md): Answer the question directly, preserve details that matter, and stop when it is answered.
- [task-contract](task-contract/SKILL.md): Compile a request or audit a running session into a binding contract with requirement IDs, independent verification, and durable handoff state.

## Prompts

- [Decision handoff](decision-handoff/PROMPT.md): Review owner decisions one at a time, record answers, and hand them back to the working agent.
- [Decision recap](decision-recap/PROMPT.md): Summarize delegated work as bullet points: what was asked, what was done, the decisions made, and the alternatives.

## Essays

- [Agent context strategy](docs/essays/agent-context-strategy.md): What to extract from meeting notes and agent sessions for coding, SRE and assistant personas, including what to use, borrow, defer or leave outside scope.
