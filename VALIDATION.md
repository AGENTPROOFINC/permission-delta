# Early public-config validation

Date: 2026-11-13

## Sample source

An initial local compatibility pass used five ready-to-paste Claude Desktop configuration examples from [`mcp-finder/claude-mcp-config-examples`](https://github.com/mcp-finder/claude-mcp-config-examples/tree/3dc619ee372361061ee379d46b6eeafe2afad441/configs), pinned to upstream commit `3dc619ee372361061ee379d46b6eeafe2afad441`:

- [`everything.json`](https://github.com/mcp-finder/claude-mcp-config-examples/blob/3dc619ee372361061ee379d46b6eeafe2afad441/configs/everything.json)
- [`filesystem.json`](https://github.com/mcp-finder/claude-mcp-config-examples/blob/3dc619ee372361061ee379d46b6eeafe2afad441/configs/filesystem.json)
- [`github.json`](https://github.com/mcp-finder/claude-mcp-config-examples/blob/3dc619ee372361061ee379d46b6eeafe2afad441/configs/github.json)
- [`postgres.json`](https://github.com/mcp-finder/claude-mcp-config-examples/blob/3dc619ee372361061ee379d46b6eeafe2afad441/configs/postgres.json)
- [`slack.json`](https://github.com/mcp-finder/claude-mcp-config-examples/blob/3dc619ee372361061ee379d46b6eeafe2afad441/configs/slack.json)

The source project describes these as ready-to-paste configuration examples. They are useful for checking parser compatibility; they are not customer repositories or observed pull-request histories.

## Method and result

- Retrieved each JSON example and confirmed it contains an `mcpServers` object.
- Replaced environment and header values with placeholders and reduced URL values to their origins before local processing. No source config values were added to this repository.
- Compared identical before/after copies of all five files with `permission-delta tree-diff`: **zero findings**, as expected.
- Made a temporary local mutation to a command in one sample: the scanner produced `MCP_COMMAND_CHANGED` and `MCP_SHELL_EXECUTABLE` as expected.

## Limits and next gate

This small compatibility pass does not estimate false-positive or false-negative rates and does not establish customer value. The sample source is curated documentation, not a representative set of active customer repositories. Expand the sample to 10–20 independently maintained public repositories, include real configuration history where available, and record review disagreements as regression cases. Keep the roadmap's user-validation gates separate from this technical compatibility check.
