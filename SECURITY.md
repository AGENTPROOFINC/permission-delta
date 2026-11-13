# Security Policy

Permission Delta is an alpha project. Do not rely on it as the sole security control for production systems.

## Reporting a vulnerability

Please do not publish credentials, private configuration files, or exploit details in a public issue.

Use GitHub's **Report a vulnerability** option on this repository's Security tab to submit a private advisory. Repository maintainers should keep GitHub private vulnerability reporting enabled. If the private reporting option is unavailable, open a public issue asking for a private contact channel and do not include vulnerability details.

## Safe-use boundaries

The scanner must remain a read-only parser. It must not execute configured commands, contact configured endpoints, print environment-variable values, or upload repository contents. Detection rules are heuristics and must include tests for both positive and negative cases.
