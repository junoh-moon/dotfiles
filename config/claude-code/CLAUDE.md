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
- When creating or editing a Github pull request (PR), write body in Korean and omit the "Test plan" section.
- Do not attempt to run the `sudo` command yourself; instead, ask the user to run it manually and wait for their result.
- Always use context7 for up-to-date documentation on third party code.




## JIRA Ticket Creation (MCP Tools)

### Tool Name Format
- Correct: `mcp__mcp-jira__jira_create_issue` (jira_ prefix required!)
- Wrong: `mcp__mcp-jira__create_issue` ❌
- All JIRA tools follow this pattern: `mcp__mcp-jira__jira_[action]`

### Strategy: Create then Update
For complex fields, create ticket first then update separately:
1. Create with basic info (project_key, summary, issue_type, description)
2. Update Epic Link: `{"customfield_10014": "EPIC-KEY"}`
3. Update Assignee: `{"assignee": "user@email.com"}`
4. Update Sprint: `{"customfield_10020": 5383}` (numeric ID only!)

### Sprint Configuration
- Find board: `jira_get_agile_boards(project_key="COREPL")`
- Find sprint ID: `jira_get_sprints_from_board(board_id="367", state="active")`
- Use numeric ID only (not array, not string)
- Example: `{"customfield_10020": 5383}` ✅
- Wrong: `{"customfield_10020": [5383]}` ❌ or `{"customfield_10020": "25Y 3Q-3"}` ❌

### Batch Creation
Use `jira_batch_create_issues` for multiple tickets, but Epic Link and Sprint require individual updates

### Common Field IDs
- Epic Link: `customfield_10014`
- Sprint: `customfield_10020`
- Story Points: `customfield_10016`
- Issue Types: "Task", "Story", "Bug", "Epic", "Subtask" (varies by project)

### Debugging
- Check existing ticket structure: `jira_get_issue(issue_key="KEY", fields="*all")`
- Check sprint info via board API: `jira_get_board_issues(board_id="367", jql="key=KEY", fields="customfield_10020")`

