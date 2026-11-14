## Permission Delta configuration comparison

| Severity | Count |
|---|---:|
| High | 2 |
| Medium | 1 |
| Low | 0 |
| Info | 0 |

Findings are heuristic review prompts, not proof of a vulnerability.

### [HIGH] MCP_COMMAND_CHANGED
**Server:** `docs`  
The server executable changed.
**Suggested review:** Review the new executable and its provenance; command values are intentionally not echoed.

### [HIGH] MCP_SHELL_EXECUTABLE
**Server:** `docs`  
The server is configured to launch a shell executable.
**Suggested review:** Confirm that shell access is necessary, constrain permitted operations, and avoid broad filesystem or network access.

### [MEDIUM] MCP_ARGUMENTS_CHANGED
**Server:** `docs`  
The server argument list changed; argument values are not displayed.
**Suggested review:** Review the new arguments in the source configuration and check for paths, flags, or embedded credentials.

---
_Privacy: environment-variable values, command arguments, URL paths, URL queries and fragments are not included in this report._

