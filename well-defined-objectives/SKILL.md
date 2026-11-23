---
name: well-defined-objectives
description: Turn a vague request into a well-defined objective with verifiable success criteria. Write one sentence saying what must be true at the end, then the checks that prove it, and leave the method open. Use whenever you write a task, prompt or brief for another model or agent (including GPT-6.2 and later), whenever a request names activities or a resemblance instead of an end state ("make this like that", "clean up", "look into", "find out what is covered"), and whenever the user asks for a target, objective, acceptance criteria, success criteria or definition of done, especially for coding tasks. Also use it on your own work before starting when you could not say how the result would be checked.
---

# Well-defined objectives

Give the worker a target it can verify: what must be true at the end, and how anyone can check it. Leave the method to the worker. The worker may be another model, another agent or you.

A request that names activities ("look at the code, then crawl the site") or a resemblance ("make the child pages like the parent page") is not a target yet. The worker picks one meaning, satisfies it and reports that it is done. Nothing can come back pass or fail, because nobody said what passing is.

## The three parts

- **Result.** What must be true when the work is done.
- **Conditions.** What it must hold under, and what must not change.
- **Evidence.** What counts as proof, ideally a check the worker can run itself.

Two of the Navier–Stokes prize statements show the shape:

| Target | What must be established |
|---|---|
| A | Prove that every qualifying smooth flow in unbounded 3D space stays smooth forever when no external force is applied. |
| C | Find one smooth starting flow in unbounded 3D space that breaks down in finite time. A smooth external force is allowed. |

Each row fixes the result and the conditions, and the evidence is a proof. Neither says how to get there, and neither is a number. A target does not need a number. It needs to be precise enough that two people would agree on whether it was met.

## Write the target

1. **Find the end state.** Ask what would be true if the work succeeded. Wording about an activity or a method ("look at", "crawl", "refactor", "use X") is at most a condition. It is never the objective.
2. **Write the objective as one sentence.**
3. **Write the conditions, if there are any.** These are what the result must hold under, such as which input, environment or login, and what must not change, such as the tests, the public interface, the output or the data. Say what must not change whenever a check could pass while the problem remains.
4. **Write two to four success criteria.** Each is a check with a pass or fail result that the worker can run without you. A worker that can run the check finds and fixes its own mistakes. Otherwise every mistake waits until you notice it.
5. **Leave the method out.** Routine decisions about how to do the work belong to the worker. Prescribing them does not make the result easier to check, and it removes the room a capable worker needs to find a better route.
6. **Name the reading you chose.** If the request could mean two different end states, choose the one the request and the project best support, and say which in one line above the target so the user can correct it. "Coverage" by page and "coverage" by line of code are different objectives.

Use this shape:

```
Objective: <one sentence: what must be true at the end>
Conditions: <what it must hold under, and what must not change; leave out if none>
Success criteria:
- <check with a pass or fail result>
- <check with a pass or fail result>
```

Keep it this short. An objective that grows into steps, roles and decisions has become a plan, and a plan fixes the method again.

Do not invent thresholds or facts about the project. If the target needs something only the user knows, such as a time limit or the list of points that must match, propose it and mark it as yours to confirm.

Keep notes to the user outside the block, such as the reading you chose or a value you proposed. The block can then be handed to the worker as it is.

If the user asked only what the objective and success criteria would be, give them that and stop. Do not offer to run the task or expand it into a brief. If the user asked for the prompt or brief itself, the target is its core. Add only what the worker cannot find out on its own, such as where the code lives and how to run it.

## Evidence that works for code

- A test that fails before the change and passes after it.
- The same output as a reference: saved input and output pairs, or the old version.
- A timing script with a stated limit, together with a check that the output is unchanged.
- A build, type check or linter that exits cleanly.
- For findings, a citation for each claim (file and line) and counts that add up.

## Examples

| Vague request | Objective | Success criteria |
|---|---|---|
| "Fix the login bug" | Logging in with an email that contains a plus sign succeeds. | A new test fails on the current commit and passes after the fix. The rest of the suite still passes. |
| "Make the export faster" | Exporting the 50,000-row fixture takes under 2 seconds, and the output file is byte-identical to today's. | A timing script, and a diff against the saved output. |
| "Clean up the payments module" | No file is over 300 lines, and public function signatures are unchanged. | Count lines in every file in the payments module and verify each has at most 300. Compare the exported function names, parameters, defaults and return types with the starting revision. The signature diff is empty and the unchanged tests pass. |
| "Port this script to TypeScript" | The new version gives the same output as the old one on every recorded input. | A comparison script over the saved input and output pairs. |
| "Add CSV import" | Six example files, written before any code, each import with a stated result or error message. Importing the same file twice creates no duplicates. | Tests that encode those six cases. |
| "Find out what our Playwright browser tests cover: look at the code, then crawl the website" | For every page a crawl of the site finds, say whether a test checks it, only passes through it, or never opens it. | One row per crawled page, and the row count matches the crawl. Every row marked checked or passed through cites the test file and line. Every row marked never opened shows the search that found nothing. |

## "Find out" tasks

"Find out", "audit" and "see what is covered" name an activity. Give the task a fixed list to measure against, taken from a named source: every page a crawl finds, every route in the router, every public function. The criteria are then that every item on the list has an answer with evidence, and that the counts add up. Without the list, the result is a summary of what was looked at, and nobody can see what was missed.

## When no check can be written

- For visual or taste-driven work, use a reviewed example as the reference. If none exists, have one made and correct it until it is right. Then name the points that must match.
- Do not add a number just to have one. "Write five steps" lets the worker hit the number and miss the point.
- Ask only when you cannot choose a reading at all. Then ask the one question that settles what success means.

## Check the target before handing it over

- Would two people agree on whether it was met?
- Can the worker run every check itself?
- Could a check pass while the problem remains? Then add what must not change to the conditions.
- Is a resemblance or taste word still in it ("like", "consistent", "better", "clean", "properly")? Replace it with the property that must hold.
- Does it prescribe a method? Remove that unless it is a real constraint.

For a long task with many requirements, use [task-contract](../task-contract/SKILL.md) and write each requirement this way.

## Why this works

The model makers give the same advice for their current models.

- OpenAI, [Prompting GPT-6.2 in Codex](https://learn.chatgpt.com/guides/prompting-gpt-6-2-astra): "Describe what you need the way you'd ask a colleague who knows the project, then tell Codex what you'll look for when you review the work." And: "Leave routine decisions about how to do the work to Codex."
- Anthropic, [Claude Code best practices](https://code.claude.com/docs/en/best-practices): "Give Claude something it can run that comes back pass or fail."
- The Clay Mathematics Institute's [official Navier–Stokes problem description](https://www.claymath.org/wp-content/uploads/2022/06/navierstokes.pdf) introduces its four statements this way: "To give reasonable leeway to solvers while retaining the heart of the problem, we ask for a proof of one of the following four statements."
