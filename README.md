# Permission Delta

**Working project name. Not a trademark-cleared public brand.**

Review changes to Model Context Protocol (MCP) server configuration before they enter a repository.

Permission Delta compares two JSON configuration snapshots, identifies changes to `mcpServers`, and creates a sanitized review report. It is intended to help developers notice configuration changes that deserve a human review.

> **Important:** This is an early heuristic tool, not a security certification, complete MCP validator, runtime monitor, or enforcement gateway. A warning is not proof of a vulnerability, and no finding is not proof that a configuration is safe.

## Fastest trial: GitHub Actions

If you already have a `pull_request` workflow, add this step and set the workflow permission to `contents: read`:

```yaml
- uses: AGENTPROOFINC/permission-delta@v0.1.0
```

No separate checkout step, Python installation, or repository secret is required. The action compares the pull request's base and proposed snapshots and writes an advisory report to the Actions workflow summary. `fail-on` defaults to `never`, so findings do not fail the check.

For a first run, create `.github/workflows/permission-delta.yml` with this complete workflow:

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

Then open a pull request that changes an MCP configuration file. [See a concrete command-change example](examples/command-shift/README.md) or the one-page [maintainer trial guide](TRIAL.md).

## Safety and privacy boundaries

- Reads JSON files only.
- Does not execute server commands, scripts, or MCP servers.
- Does not make network requests.
- Does not upload repository contents.
- Does not print environment-variable values.
- Does not print command arguments.
- For URL findings, reports only the host; credentials, path, query, and fragment are omitted.
- Uses local SHA-256 fingerprints internally to notice environment value changes; the values and fingerprints are not included in reports.
- Limits individual JSON files to 1 MB and tree scans to 2,000 JSON files.

Treat reports as review aids. Review the underlying configuration and apply your organization's security process before approving changes.

## Requirements

- Python 3.10 or newer
- macOS, Linux, or Windows

No runtime third-party Python dependencies are required.

## Install locally

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

## Compare two files

```bash
permission-delta compare examples/before.json examples/after.json
```

JSON output:

```bash
permission-delta compare examples/before.json examples/after.json --format json
```

Write a report to a file:

```bash
permission-delta compare examples/before.json examples/after.json --output report.md
```

By default, findings do not fail the command. To use a severity threshold:

```bash
permission-delta compare examples/before.json examples/after.json --fail-on high
```

## Compare repository snapshots

The tree scanner finds `mcp.json`, `claude_desktop_config.json`, `*.mcp.json`, and other JSON files containing an `mcpServers` object.

```bash
permission-delta tree-diff --before-dir ./baseline --after-dir ./proposed
```

Directories such as `.git`, `.venv`, `node_modules`, `dist`, and `build` are excluded.

## GitHub Action details

The public [`v0.1.0` release](https://github.com/AGENTPROOFINC/permission-delta/releases/tag/v0.1.0) is ready to use. For stricter supply-chain pinning, replace the tag in the workflow above with the full commit SHA shown on the release page.

The default `fail-on` mode is `never`, so findings appear as an advisory summary without failing the check. Set it to `low`, `medium`, or `high` to fail when the report contains findings at or above that severity.

The action checks out the pull request base and proposed snapshots separately, runs the scanner from the trusted action source, and adds a sanitized report to the workflow summary. It does not execute code from the proposed revision. Its workflow token only needs `contents: read`; it does not approve, reject, or merge pull requests. Do not use `pull_request_target`.

The repository workflows at `.github/workflows/permission-delta.yml` and `.github/workflows/tests.yml` demonstrate the configuration-review and test checks. Both third-party actions are pinned to full commit SHAs.

## Initial detection coverage

- Added and removed MCP servers.
- Changed server executable, arguments, or URL host.
- Added, removed, or changed environment variables (values are never displayed).
- Shell executable names such as `bash`, `sh`, `zsh`, `cmd`, and `powershell`.
- Common network utilities such as `curl`, `wget`, `ssh`, and `nc`.
- Wildcard-like values in recognized permission-related fields.
- Remote HTTP(S) endpoints.

These checks are intentionally narrow. They do not establish whether a server is trustworthy, whether a URL is safe, what tools a server exposes at runtime, or whether an agent can escape its sandbox.

See [VALIDATION.md](VALIDATION.md) for the initial public-config compatibility pass and its limits.

## Development

Run the test suite:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Contributions should include tests and must not add command execution, network access, secret-value output, or unreviewed auto-blocking behavior.
