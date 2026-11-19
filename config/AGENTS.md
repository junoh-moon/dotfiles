# Rules for LLM Agents

- After completing a TODO, verifying a feature, or verifying a bug fix, suggest a git commit in manual mode or create one in auto-accept edits on mode.
- For services with an authenticated CLI (e.g. GitHub → `gh`, Notion → `ntn`), use the CLI instead of WebFetch/browsing, including when given a URL.
- Ask the user to run `sudo` command manually and wait for their result.
- When unsure about CLI command usage, actively use help options (`--help`, `-h`, `help` subcommand) to explore available arguments and syntax.
- Use "하십시오체" for Korean.
- Never leave a background subagent or shell open once it has finished or is no longer needed, including ones that completed on their own.
- When consulting memory, read relevant entries from both `~/.codex/memories/` and `~/.claude/projects/*/memory/`. Give relevant entries the same weight regardless of which agent wrote them.
- When writing memories, do not just append information; you must consider removing or updating an existing entry first.

### Miscellaneous
- If current working directory is inside `/mnt/elements/micro_services`, DO NOT USE SEARCH/FIND RECURSIVELY WITHOUT MAX-DEPTH LIMIT
- Prefer the minimal fix; do not refactor structure alongside a bug fix. In review loops accept only findings that matter in realistic use, and push back on over-engineering.
- During review→fix loops, run a simplification pass (e.g. `/simplify`) every round or two so patches do not erode code quality.
- Before `kubectl/helm apply`, run diff-command and show the result.

-----
