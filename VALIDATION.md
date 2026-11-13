# Early public-config validation

Date: 2026-11-13

## Sample set

I checked 17 JSON configuration samples from five public GitHub repositories. Five samples are checked-in JSON files; twelve are valid JSON configuration blocks in public setup documentation. Sources were read-only and pinned at the individual file blob SHAs listed below.

| Public repository | Source file(s) | Samples | File blob SHA(s) |
|---|---|---:|---|
| [mcp-finder/claude-mcp-config-examples](https://github.com/mcp-finder/claude-mcp-config-examples) | `configs/everything.json`, `configs/filesystem.json`, `configs/github.json`, `configs/postgres.json`, `configs/slack.json` | 5 | `51aa85df2d9b8ae8197fc2e99990eeab9ee52753`, `dbbb7be5339c83cbb335e1cf11178dff1612a7ba`, `2891f6172c397130fb913ec048953562858f1136`, `116e3bf770320425ae0f3b94c35fa429e6e38e9e`, `da721265e86263f0f663781b4e439b993d0a1635` |
| [microsoft/mcp-for-beginners](https://github.com/microsoft/mcp-for-beginners) | `03-GettingStarted/12-mcp-hosts/README.md` | 3 | `fb30e789b7e41bf348d1472faef5fa67a1cf480b` |
| [github/github-mcp-server](https://github.com/github/github-mcp-server) | `docs/installation-guides/install-claude.md` | 5 | `04658c45205debe6a35da55ff092e76b7930bbe8` |
| [confluentinc/mcp-confluent](https://github.com/confluentinc/mcp-confluent) | `docs/configuring-claude-desktop.md` | 2 | `148fea6223b7b9318998bf30aaba423eb9eff214` |
| [griddynamics/rosetta](https://github.com/griddynamics/rosetta) | `MCPs.md` | 2 | `6d576a3ca79e9492f7e1d3ac51c5d25a1c002e20` |

These are public install examples, not customer repositories or observed pull-request histories. The sample corpus was kept local and was not added to the product repository.

## Method and result

- Extracted JSON objects containing an `mcpServers` map and confirmed the 17 samples parse.
- Replaced environment and header values with placeholders, replaced secret-like values, and reduced URL strings to their origins before local processing.
- Ran `permission-delta tree-diff` over identical before/after snapshots containing the 17 samples: **zero findings**, as expected.
- Made a temporary local mutation to a command in one sample: the scanner returned `MCP_COMMAND_CHANGED` and `MCP_SHELL_EXECUTABLE` as expected.
- The repository's 12 unit tests pass locally; GitHub Actions also runs them on pushes and pull requests.

## Limits and next gate

This is an initial compatibility check, not an estimate of false-positive or false-negative rates. Documentation examples do not represent the variety of active team repositories, and the synthetic change is not an observed pull request. Next, validate against real repository history with maintainers' permission, test fork and deleted-fork pull requests, then measure whether teams keep the Action enabled. The 10-active-repository milestone remains unproven until external repositories install and retain the check.
