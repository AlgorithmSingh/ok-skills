# ok-skills

Markdown skills, prompts and rules for working with coding assistants.

## Setup and use

In Claude Code, Codex or Gemini CLI, open this clone as a workspace. Ask the assistant to read the linked `SKILL.md` and apply it to a specific task or source. For example, “Read `extract-meeting-notes/SKILL.md` and extract the supplied minutes into my project.” Give the target repository explicitly when it differs from the current workspace. Each extraction skill includes its own references and checker.

For project-level discovery, copy the complete skill folder to the appropriate directory under the target project's root.

| Tool | Project skills directory | Documentation |
|---|---|---|
| Claude Code | `.claude/skills/` | [Claude Code skills](https://code.claude.com/docs/en/skills) |
| Codex | `.agents/skills/` | [Codex local skills](https://developers.openai.com/codex/skills/) |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | [Gemini CLI skills](https://geminicli.com/docs/cli/skills/) |

Paste a decision prompt into an existing conversation. Supply the rule pack as reading material for Java or Spring Boot work. The checkers need Git and Python 3 with the standard library. From the clone root run `python3 -I -B scripts/check_repo.py` and `python3 -I -B -m unittest discover`. Try the extraction checker on the [worked store](examples/mini-store/README.md) or use the [synthetic fixtures](fixtures/README.md) for a behavioral review.

## Which skill to use

| When you need to… | Use |
|---|---|
| Diagnose a problem or judge whether a result transfers to your setup | [Answer the actual question](answer-the-actual-question/SKILL.md) |
| Shorten or clarify an established answer | [Direct answers](direct-answers/SKILL.md) |
| Give a non-technical owner a status update | [Boss brief](boss-brief/SKILL.md) |
| Define a verifiable outcome for a task | [Well-defined objectives](well-defined-objectives/SKILL.md) |
| Track or audit a substantial assignment requirement by requirement | [Task contract](task-contract/SKILL.md) |
| Build a knowledge store from agent transcripts and supporting documents | [Extract session details](extract-session-details/SKILL.md) |
| Build the same store from human meeting notes or minutes | [Extract meeting notes](extract-meeting-notes/SKILL.md) |
| Draft a project-specific assignment for later session-history research | [Project memory investigation prompt](project-memory-investigation-prompt/SKILL.md) |
| Map a conversation’s branches and recover open threads | [Session forks](session-forks/SKILL.md) |

## Prompts and rule pack

- [Decision handoff](decision-handoff/PROMPT.md) takes outstanding choices to the owner and returns their answers to the working agent.
- [Decision recap](decision-recap/PROMPT.md) summarizes completed work, decisions and alternatives.
- The Spring Boot rule pack contains [Java language rules](springboot-rules/java.md) and [Spring Boot rules](springboot-rules/spring-boot.md), with examples for implementation and review.

## Guides

- [LangGraph from primitives to production](docs/guides/langgraph-from-primitives-to-production.md) explains LangGraph's runtime primitives and the enterprise essentials: loop bounds, checkpointing, human approval, idempotent retries, streaming with secret injection and PII redaction, and cross-thread memory.

## Essays

- [Agent context strategy](docs/essays/agent-context-strategy.md) explains what coding, SRE and assistant readers need from meetings and agent sessions.
- [Google Knowledge Catalog vs. ok-skills extraction](docs/essays/knowledge-catalog-vs-extraction-skills.md) compares the evidence model, authority, review and downstream evaluation of the two systems.
