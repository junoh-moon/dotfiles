# Rules for LLM Agents

- When you cannot implement the code immediately, explicitly indicate that it has not been implemented. For example, use `NotImplementedError` in Python or `TODO` in Kotlin. Do not hardcode to hide the problem.
- Create a todo list first when working on complex tasks to track progress and remain on track.
- For database access tasks (schema analysis, sample data, etc.):
    - Use official Docker client images (postgres, mysql, mongo) for direct connection
    - For K8s cluster databases: either port-forward + local access or temporary client pods
    - For multiple queries: consider keeping containers running and using docker exec, then cleanup
    - Choose appropriate client versions based on target database version
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

## Commit Message Convention

Based on the following git diff of staged changes, generate a conventional commit message with a clear subject line (max 72 chars) and body (wrapped at 72 chars).
The message should clearly explain what changed and why.
To create a commit message, focus on staged files ONLY. Run `git diff --cached` to see the changes.
Sometimes, you have to `git add` files by yourself -- pre-commit fail, unstaged files, or manual edit by a user. In this case, NEVER USE `git add -u` or `git add -A`; instead, add each file.

Format the commit message as plain text (no markdown):
- First line: conventional commit format (feat:, fix:, docs:, etc.) under 72 chars in English
- Empty line
- Body: wrapped at 72 chars, explaining what and why in Korean
- Use heredoc syntax for multi-line commit messages to preserve formatting
- Examples:
  ```bash
  git commit -m "$(cat <<'EOF'
fix: correct regex escaping for JetBrains IDE bundle identifiers

Karabiner 설정에서 JetBrains IDE 애플리케이션 번들 식별자의 정규식
이스케이프를 수정했습니다. 기존의 `^com\.jetbrains\\..*$` 패턴이
백슬래시를 잘못 이스케이프하여 정규식이 의도대로 작동하지 않았던
문제를 해결했습니다. 이제 `^com\\.jetbrains\\..*$`로 올바르게
수정되어 JetBrains IDE 제품군이 Karabiner 키 매핑 예외 목록에서
정상적으로 인식됩니다.
EOF
)"

  git commit -m "$(cat <<'EOF'
feat(karabiner): add JetBrains IDE exception to PC-Style mappings

JetBrains IDE 제품군을 Karabiner 키 매핑 예외에 추가하여
IDE 내장 단축키가 정상 작동하도록 함 (특히 Copy/Paste와 Reload)

- PC-Style Copy/Paste/Cut (Ctrl+C/V/X)에 예외 추가
- PC-Style Reload (Ctrl+R, F5)에 예외 추가
- 들여쓰기 일관성 수정 (탭 → 공백)
EOF
)"
  ```

## Pull Request Rules

- Use `gh` command to create, read, and edit pull requests (PRs).
- When creating or editing a Github pull request (PR), write body in Korean and omit the "Test plan" section.
- Do not just list a series of commit messages in a PR body; instead, group commits by context.
- When you create a PR request on `bucketplace` organization, add `PR-by-AI` label.

### Miscellaneous
- If current working directory is inside `/mnt/elements/micro_services`, DO NOT USE SEARCH/FIND RECURSIVELY WITHOUT MAX-DEPTH LIMIT

