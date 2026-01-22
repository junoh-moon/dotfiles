# Rules for LLM Agents

- When you cannot implement the code immediately, explicitly indicate that it has not been implemented. For example, use `NotImplementedError` in Python or `TODO` in Kotlin. Do not hardcode to hide the problem.
- Create a todo list first when working on complex tasks to track progress and remain on track.
- When completing a logical unit of work (e.g., finishing a TODO item, completing a feature without bugs), establish a checkpoint:
    - In manual mode: suggest to the user to create a git commit
    - In `auto-accept edits on` mode: proactively create a git commit with appropriate message
    - Consider a checkpoint complete when: a TODO is fully implemented, a feature works without errors, or a bug fix is verified
- Do not attempt to run the `sudo` command yourself; instead, ask the user to run it manually and wait for their result.
- Always use context7 for up-to-date documentation on third party code.
- Prefer `jq` for JSON and `yq` for YAML file operations (these tools are pre-installed). Use Python only for complex transformations that these tools cannot handle.
- When unsure about CLI command usage, actively use help options (`--help`, `-h`, `help` subcommand) to explore available arguments and syntax.
- To access Github information, do not use the WebFetch tool; use `gh` to reuse the existing authenticated session.
- At the start of each session, before running any shell commands, check the $SHELL environment variable once to determine the current shell.

### Miscellaneous
- If current working directory is inside `/mnt/elements/micro_services`, DO NOT USE SEARCH/FIND RECURSIVELY WITHOUT MAX-DEPTH LIMIT

-----
