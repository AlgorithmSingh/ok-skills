# Why task contracts

Autonomous coding agents fail in three predictable ways, especially on long tasks. Each one looks like normal progress until the result is checked against the original request.

## 1. Goal substitution

An agent interprets your overall goal, develops its own implementation strategy, and then treats that strategy as more important than individual requirements. This can look like initiative, but it becomes a failure when the agent silently drops constraints.

## 2. Premature success judgments

The agent sees substantial progress and concludes the task is finished without independently checking every requirement. Anthropic documented this exact failure mode in its research on long-running agents: agents sometimes see an implementation that looks substantially complete and declare the job done ([Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), Anthropic, November 2025).

## 3. Context degradation

Over long sessions, earlier instructions can become less influential, particularly after conversation compaction. Anthropic acknowledges that compaction can lose information and cause task drift ([Using Claude Code: session management and 1M context](https://claude.com/resources/articles/using-claude-code-session-management-and-1m-context), Claude by Anthropic, April 2026).

## What the prompts do

Both prompts in [SKILL.md](SKILL.md) address all three:

- **Goal substitution:** Compile every requirement into a stable, binding contract with IDs. The agent may choose implementation details, but it cannot redefine success.
- **Premature success judgments:** Require concrete acceptance checks and independent evidence for every requirement. Never treat the implementer's own claim as verification.
- **Context degradation:** Persist the contract, decisions, statuses, evidence, and next action in the repository. Rebuild from those artifacts after compaction, a restart, or a fresh session.

The prompts cannot technically prevent an agent from falsely marking itself verified. For stronger enforcement, a deterministic supervisor should own the final completion decision instead of the coding agent.

## Sources

- [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), Anthropic, November 26, 2025.
- [Using Claude Code: session management and 1M context](https://claude.com/resources/articles/using-claude-code-session-management-and-1m-context), Claude by Anthropic, April 15, 2026.
