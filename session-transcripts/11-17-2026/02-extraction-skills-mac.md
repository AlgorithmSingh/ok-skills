# Session and meeting extraction skills

This excerpt records the public skill additions. The feature commit is `fa2364a`. The two skills package the extraction guidance from the agent context essay and are linked from that essay and the repository README.

Codex session 01a1e9d4-fbe3-75a1-83bf-2549a9fc874d · codex-tui 0.169.0 · models unknown · cwd /Users/ankitsingh · 2026-11-17T14:10:46.792Z → 2026-11-17T23:01:29.201Z
3 prompts, 3 replies, 0 structured results, 0 answers, 0 tool calls; reasoning and injected context omitted.
--------------------------------------------------------------------------------

❯ [11-17 22:50Z] can you use skill-creator skill to create separate skill for session details and separate skill for meeting transcript/notes?


❯ [11-17 22:50Z] it would be https://github.com/anthropics/claude-plugins-official/blob/main/plugins/skill-creator/skills/skill-creator/SKILL.md right?

⏺ Yes, that’s Anthropic’s Skill Creator. I’d opened the bundled Codex version with the same name. I’ll use the Anthropic version you linked.


❯ [11-17 22:51Z] then add those skills also on ok-skill

⏺ I’ll add both skills to `ok-skills` as well. The skills will be self-contained so people can use them without access to the private research files.

⏺ The latest examples preserve ambiguous dates and leave unassigned follow-ups open. Some wording still assumes a cause the source hasn’t established, so I’ll flag that in the review. I’m pushing the two skills and the updated essay links now.

