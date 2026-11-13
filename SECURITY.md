# Security Policy

Permission Delta is an alpha project. Do not rely on it as the sole security control for production systems.

## Reporting a vulnerability

Please do not publish credentials, private configuration files, or exploit details in a public issue. Contact the repository maintainer privately once a project security contact has been configured.

## Safe-use boundaries

The scanner must remain a read-only parser. It must not execute configured commands, contact configured endpoints, print environment-variable values, or upload repository contents. Detection rules are heuristics and must include tests for both positive and negative cases.
