---
name: boss-brief
description: Use when updating a non-technical owner on project status, results, or decisions. Give the big picture in plain words first, then one clear next step. Strip jargon, hashes, internal labels, and metrics unless the owner asks for them.
---

# Boss brief

Talk to the owner like a boss, not a spec. Big picture first, plain words, one decision at a time.

## Rules

1. Answer "what's going on" and "what do I do next" in the first two sentences. Plain English. No jargon.
2. Name the goal in everyday terms. Say "a model that stays in character as Napoleon," not "character-persistence under adversarial pressure."
3. Strip internal labels, hashes, manifest IDs, file paths, and metrics unless the owner asks. Say "twelve trained versions," not "S5/S1/M5/M1 by e1/e2/e3 adapters."
4. One decision per message. End by naming the single yes/no or action.
5. No em dashes, no nested acronyms, no "material technical failure" when "the test hiccuped on formatting" is true.
6. If the owner is frustrated or tired, drop everything except the goal, the status, and the one next step.

## Verbatim before and after

Before (jargon, details first):

> "Twelve adapters (S5/S1/M5/M1, three epochs each) are trained, preserved unmerged, and intact; the 375-pair set is fixed; the final and reserve pools are sealed. The GPU screen finished all 13 candidates against the 624-unit pool, then the paid Luna diagnostic screen ran and failed: 494 of 624 units passed, 130 exhausted their three attempts because evidence quotes changed Markdown, whitespace, or wording, so no checkpoint result can be declared."

After (big picture, plain):

> "You're trying to build a model that stays in character as Napoleon and doesn't crack when someone pressures it. That's the whole goal. Everything else is just machinery around that one question. Where you are: you trained twelve versions, all saved. The test that tells you if any of them actually works is about four-fifths done and got stuck on a formatting detail. No winner, no loser, just an unfinished count. To finish: approve one small fix, and the test tells you plainly whether any version beats doing nothing."
