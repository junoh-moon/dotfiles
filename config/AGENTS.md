# Rules for LLM Agents

- When you cannot implement the code immediately, explicitly indicate that it has not been implemented. For example, use `NotImplementedError` in Python or `TODO` in Kotlin. Do not hardcode to hide the problem.
- Create a todo list first when working on complex tasks to track progress and remain on track.
- When completing a logical unit of work (e.g., finishing a TODO item, completing a feature without bugs), establish a checkpoint:
    - In manual mode: suggest to the user to create a git commit
    - In `auto-accept edits on` mode: proactively create a git commit with appropriate message
    - Consider a checkpoint complete when: a TODO is fully implemented, a feature works without errors, or a bug fix is verified
- Do not attempt to run the `sudo` command yourself; instead, ask the user to run it manually and wait for their result.
- Prefer `jq` for JSON and `yq` for YAML file operations (these tools are pre-installed). Use Python only for complex transformations that these tools cannot handle.
- When unsure about CLI command usage, actively use help options (`--help`, `-h`, `help` subcommand) to explore available arguments and syntax.
- To access Github information, do not use the WebFetch tool; use `gh` to reuse the existing authenticated session.
- Use "하십시오체" for Korean.
- Never leave a background subagent or shell open once it has finished or is no longer needed, including ones that completed on their own.
- Allowed to read other agents' memories; `~/.codex/memories/`, `~/.claude/projects/*/memory/`.
- When writing memories, do not just append information; you must consider remove or update existing memories first.

### Miscellaneous
- If current working directory is inside `/mnt/elements/micro_services`, DO NOT USE SEARCH/FIND RECURSIVELY WITHOUT MAX-DEPTH LIMIT
- Prefer the minimal fix; do not refactor structure alongside a bug fix. In review loops accept only findings that matter in realistic use, and push back on over-engineering.
- During review→fix loops, run a simplification pass (e.g. `/simplify`) every round or two so patches do not erode code quality.
- Before deleting or cleaning up, verify what would be lost, and make and verify a backup first. Never force-remove a dirty git worktree.
- Before `kubectl apply`, run `kubectl diff -f <file>` and show the result.
- On the home server, check `free -h` right before a memory-heavy job; RAM is shared with live k3s services.

-----
