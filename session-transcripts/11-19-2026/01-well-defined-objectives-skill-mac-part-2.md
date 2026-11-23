# Well-defined objectives skill, part 2

This excerpt records the test run of the public skill with Anthropic's skill-creator. The commit that added the test prompts is `9a0a2b1`. Three prompts were each answered with and without the skill and graded by separate agents: 21 of 22 checks passed with the skill and 9 of 22 without. The skill text was not changed. Prompts and replies about other work are left out, and the rest of the session is saved elsewhere.

Claude Code session 87cd3e56-ad05-4add-9eaa-884d6a4399ba · Claude Code 2.1.328 · models claude-fable-5-2 (172) · title "GPT-6.2 Astra well-defined objectives" · cwd [local path] · 2026-11-19T05:07:01.203Z → 2026-11-22T20:23:43.666Z
12 prompts, 24 replies, 0 structured results, 0 answers, 91 tool calls; hidden thinking omitted, tool calls summarized.
--------------------------------------------------------------------------------

❯ [11-22 20:09Z] 1) Use https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md on that skill to make sure it was created right,  2)Next, can you write in the root level Agents.md to whenever you delegate work to subagent, do it like ok-skills/well-defined-objectives/SKILL.md  ?

⏺ The skill passes the upstream validator. Now launching the six test runs skill-creator calls for: three prompts, each with the skill and without it.

⏺ Two of the six test runs have finished (both without the skill). I'm waiting on the other four, then I'll have them graded and build the comparison page.

⏺ Three of six test runs are in. Still waiting on the other three before grading.

⏺ Four of six test runs are in. Two are still running: the Playwright prompt without the skill, and the API docs prompt with it.

⏺ Five of six test runs are in. The last one, the Playwright prompt without the skill, is still running; grading starts when it lands.

⏺ All six test runs are done and three graders are scoring them. I've held off writing the delegation rule into `[local path]` until the test runs are completely finished, because the runs without the skill load that file and the rule would point them at the skill.

⏺ Graded the API docs prompt: 6 of 7 checks passed with the skill and 3 of 7 without it. Two graders are still working on the other prompts.

⏺ Two of three prompts are graded. The flaky-test brief passed 7 of 7 checks with the skill and 2 of 7 without it. One grader, for the Playwright prompt, is still running.

⏺ Grading is done: 21 of 22 checks passed with the skill, 9 of 22 without it. Writing up the per-check patterns and building the review page now.
