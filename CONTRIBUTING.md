# Contributing to Permission Delta

Permission Delta is an early, read-only configuration review tool. Keep changes small, explainable, and safe for untrusted repository content.

## Before proposing a change

1. Read `AGENTS.md`, `SECURITY.md`, and the relevant implementation and tests.
2. Describe the behavior and the smallest useful change.
3. Keep runtime dependencies at zero unless a maintainer approves a clear need.

## Requirements for changes

- Never execute commands, scripts, MCP servers, or URLs found in scanned configuration.
- Keep the scanner offline and local. Do not upload source or configuration.
- Never include environment-variable values, credentials, command arguments, or URL secrets in output.
- Escape untrusted content in Markdown and JSON reports.
- Keep scan limits bounded and document supported formats and blind spots.
- Add regression coverage for new rules, including benign cases and redaction where relevant.
- Treat findings as review prompts, not proof of vulnerabilities.
- Keep GitHub Actions permissions read-only. Never use `pull_request_target` for untrusted PR content.
- Do not add auto-approval, auto-blocking, telemetry, accounts, paid services, or external AI calls without explicit review.

## Local checks

From the repository root on macOS, Linux, or Windows:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m permission_delta compare examples/before.json examples/after.json
```

State the exact commands and results in your pull request. Do not claim checks passed unless they ran successfully.
