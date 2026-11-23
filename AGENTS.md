# Repository instructions

This repository is public and standalone. Anyone cloning it onto a new machine must be able to read every document and use every skill or prompt without local files, private context, or setup from the author's laptop.

## Keep the repository self-contained

- Never commit machine-local paths such as `/Users/<name>/...`, `/home/<name>/...`, `~/...` pointing to personal folders, or references to local `Downloads` or `Desktop` directories.
- Never commit references to private sibling repositories, local document folders, private server hostnames, local scratch directories, or unshared conversations as dependencies or citations.
- Every link in a skill, prompt, essay, script, or `README.md` must resolve either to a file inside this repository by relative path or to a public URL.
- Write every skill, prompt, and essay so a reader who only has this clone understands what it covers, what it depends on, and how to use it.
- Keep scratch work and untracked session artifacts such as `.sessions/` out of commits.

## Documentation and checks

- Keep `README.md`, `docs/index.md`, `docs/essays/index.md`, and `docs/log.md` updated when adding or changing skills, prompts, or essays.
- Before committing, run `python3 -I -B scripts/check_repo.py` and `python3 -I -B -m unittest discover` to verify YAML frontmatter, relative Markdown links, README coverage, mirror byte-identity, and the absence of machine-local paths, private repository names, hostnames, and credentials.
- If a change touches `extract-meeting-notes` or `extract-session-details`, keep their shared `references/` and `scripts/` files identical across both skills.
