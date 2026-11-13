# Product thesis — Permission Delta (working codename)

## One-sentence promise

Show developers exactly which MCP server configuration capabilities changed in a pull request, with enough context to decide what deserves human review.

## Initial user

A software developer or platform engineer maintaining repositories that configure Model Context Protocol (MCP) servers.

## User problem to validate

A configuration change can introduce or expand an agent's access to local commands, remote endpoints, environment variables, or declared tool permissions. Ordinary code review may not make those changes obvious.

This is a hypothesis. We must verify that developers experience the problem frequently enough to install and keep a dedicated tool.

## Narrow initial solution

1. Discover JSON files containing an `mcpServers` object.
2. Compare baseline and proposed configuration snapshots.
3. Identify server additions/removals and changes to executable, arguments, endpoint, environment variable names and environment values.
4. Apply a small, transparent set of deterministic heuristics.
5. Produce a sanitized Markdown and JSON report.
6. Run as a read-only GitHub Actions pull-request check.

## Non-goals for the first release

- Runtime monitoring or enforcement.
- Executing MCP servers or agent tools.
- Claiming an MCP server is trustworthy or safe.
- Certifying compliance with a standard.
- Uploading source code or configuration to an AI model.
- Automatically approving, rejecting, or merging pull requests.
- Supporting every agent framework or every configuration format.

## Why open source first

A developer tool needs trust and low-friction evaluation. A local scanner with no account, paid API, or code upload makes the first trial easier. The first objective is repeat use, not monetization.

## Validation questions

Ask developers to show, rather than speculate about:

1. The last time an agent/MCP configuration changed in a repository.
2. How they reviewed that change.
3. Whether they would install a pull-request check for it.
4. Which findings they would trust, ignore, or want explained.
5. Whether the workflow would remain enabled after a two-week trial.

## Evidence required before expanding scope

- At least five independent developers try the prototype.
- At least three run it on a real repository.
- At least two keep it enabled for repeated pull requests.
- False-positive and false-negative examples are recorded and turned into regression tests.
- Users can explain the product's value without being coached by the founder.

These are early validation gates, not evidence of product-market fit.

## Long-term direction (unproven)

If the initial workflow becomes habit-forming, explore shared policy files, policy versioning, approval evidence, cross-platform configuration normalization, and organization-level governance. Expand into identity or runtime controls only after customers demonstrate that need.
