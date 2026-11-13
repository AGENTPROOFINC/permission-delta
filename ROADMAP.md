# Roadmap

## v0.1 — local config diff

- [x] Compare two MCP JSON configs.
- [x] Detect server additions and removals.
- [x] Detect executable, arguments, endpoint, and environment changes.
- [x] Produce Markdown and JSON reports.
- [x] Include secret-value redaction and no-execution boundaries.
- [x] Add unit tests and sample files.

## v0.2 — repository validation

- [x] Initial compatibility pass across 17 public MCP configuration examples from five repositories; see [VALIDATION.md](VALIDATION.md).
- [ ] Validate against real repository history with maintainer permission; documentation examples do not establish user value or real-world detection quality.
- [ ] Add more config fixtures and regression tests.
- [ ] Improve discovery for nested and less common MCP config formats.
- [ ] Pin GitHub Actions dependencies to reviewed commit SHAs.
- [ ] Test pull requests from forks and deleted forks.
- [ ] Add SARIF output only after validating how findings map to source lines.

## v0.3 — developer workflow

- [ ] Add policy-as-code with explicit allowlists and exceptions.
- [ ] Add baseline management and explainable suppression.
- [ ] Measure false-positive rates with volunteer feedback.
- [ ] Add installation and upgrade tests.

## Later — only after user evidence

- [ ] Shared policy packs.
- [ ] Organization-wide policy and approval history.
- [ ] Cross-agent configuration normalization.
- [ ] Signed, verifiable policy snapshots.
- [ ] Enterprise audit exports.

Do not build later-stage features until repeated usage demonstrates that users need them.
