"""Core comparison and heuristic checks.

This module deliberately avoids network access, shell execution, and printing
configuration values. Findings are review prompts, not proof of a vulnerability.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit
import json
import re

MAX_CONFIG_BYTES = 1_000_000
MAX_TREE_JSON_FILES = 2_000
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".tox", "dist", "build"}
SHELL_COMMANDS = {"sh", "bash", "zsh", "fish", "cmd", "cmd.exe", "powershell", "pwsh"}
NETWORK_COMMANDS = {"curl", "wget", "nc", "ncat", "netcat", "socat", "ssh", "scp", "ftp"}
SECRET_NAME_RE = re.compile(r"(SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL|PRIVATE.?KEY|API.?KEY|AUTH)", re.I)
WILDCARD_KEYS = {"allow", "allowed", "allowlist", "allowedtools", "permissions", "scopes", "scope", "tools"}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule_id: str
    server: str
    message: str
    recommendation: str
    file: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Server:
    name: str
    command: str | None
    args: tuple[str, ...]
    url: str | None
    url_fingerprint: str | None
    env_names: tuple[str, ...]
    env_fingerprint: tuple[tuple[str, str], ...]
    raw: dict[str, Any]


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON MCP config with size and shape checks."""
    config_path = Path(path)
    try:
        size = config_path.stat().st_size
    except OSError as exc:
        raise ValueError(f"Cannot read configuration file: {config_path}") from exc
    if size > MAX_CONFIG_BYTES:
        raise ValueError(f"Configuration exceeds the {MAX_CONFIG_BYTES:,}-byte safety limit: {config_path}")
    try:
        text = config_path.read_text(encoding="utf-8")
        data = json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid or unreadable JSON configuration: {config_path}") from exc
    if not isinstance(data, dict):
        raise ValueError("Configuration root must be a JSON object")
    return data


def _safe_command(value: Any) -> str | None:
    """Return a command token only; never retain or print command arguments."""
    if not isinstance(value, str) or not value.strip():
        return None
    # Some configs store a command as a simple executable; avoid shlex parsing
    # arbitrary shell-like strings because command values are untrusted input.
    first = value.strip().split()[0]
    return Path(first).name.lower() or None


def _safe_url_host(value: Any) -> str | None:
    """Expose only a URL host, dropping credentials, path, query and fragment."""
    if not isinstance(value, str):
        return None
    try:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
            return None
        host = parsed.hostname.lower()
        if parsed.port:
            host = f"{host}:{parsed.port}"
        return host
    except ValueError:
        return None


def _fingerprint_value(value: Any) -> str:
    """Stable internal digest input. The value itself is never included in output."""
    import hashlib

    try:
        serialized = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    except (TypeError, ValueError):
        serialized = repr(type(value).__name__)
    return hashlib.sha256(serialized.encode("utf-8", errors="replace")).hexdigest()


def _servers(config: dict[str, Any]) -> dict[str, Server]:
    raw_servers = config.get("mcpServers", {})
    if raw_servers is None:
        raw_servers = {}
    if not isinstance(raw_servers, dict):
        raise ValueError("The 'mcpServers' field must be a JSON object")
    result: dict[str, Server] = {}
    for name, raw in raw_servers.items():
        if not isinstance(name, str) or not isinstance(raw, dict):
            continue
        command = _safe_command(raw.get("command"))
        args_raw = raw.get("args", [])
        args = tuple(str(x) for x in args_raw) if isinstance(args_raw, list) else ()
        env = raw.get("env", {})
        if not isinstance(env, dict):
            env = {}
        env_names = tuple(sorted(str(k) for k in env.keys()))
        env_fingerprint = tuple(sorted((str(k), _fingerprint_value(v)) for k, v in env.items()))
        raw_url = raw.get("url")
        url_fingerprint = _fingerprint_value(raw_url) if isinstance(raw_url, str) else None
        result[name] = Server(
            name=name,
            command=command,
            args=args,
            url=_safe_url_host(raw_url),
            url_fingerprint=url_fingerprint,
            env_names=env_names,
            env_fingerprint=env_fingerprint,
            raw=raw,
        )
    return result


def _has_wildcard_permission(value: Any, parent_key: str = "") -> bool:
    key = parent_key.lower().replace("_", "")
    if isinstance(value, dict):
        for child_key, child_value in value.items():
            normalized = str(child_key).lower().replace("_", "")
            if normalized in WILDCARD_KEYS and _contains_wildcard(child_value):
                return True
            if _has_wildcard_permission(child_value, normalized):
                return True
    elif isinstance(value, list):
        return any(_has_wildcard_permission(item, key) for item in value)
    return False


def _contains_wildcard(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip() in {"*", "*:*", "all", "ALL"}
    if isinstance(value, list):
        return any(_contains_wildcard(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_wildcard(k) or _contains_wildcard(v) for k, v in value.items())
    return False


def compare_configs(before: dict[str, Any], after: dict[str, Any], file: str | None = None) -> list[Finding]:
    """Compare two MCP JSON objects and return sanitized, review-oriented findings."""
    old_servers = _servers(before)
    new_servers = _servers(after)
    findings: list[Finding] = []

    for name in sorted(new_servers.keys() - old_servers.keys()):
        server = new_servers[name]
        findings.append(Finding(
            "medium", "MCP_SERVER_ADDED", name,
            "A new MCP server was added.",
            "Verify the server's publisher, source, intended tools, and required access before approving.", file,
        ))
        findings.extend(_server_risk_findings(server, file))

    for name in sorted(old_servers.keys() - new_servers.keys()):
        findings.append(Finding(
            "info", "MCP_SERVER_REMOVED", name,
            "An MCP server was removed.",
            "Confirm that no workflow still depends on this server.", file,
        ))

    for name in sorted(old_servers.keys() & new_servers.keys()):
        old, new = old_servers[name], new_servers[name]
        if old.command != new.command:
            findings.append(Finding(
                "high", "MCP_COMMAND_CHANGED", name,
                "The server executable changed.",
                "Review the new executable and its provenance; command values are intentionally not echoed.", file,
            ))
            findings.extend(_server_risk_findings(new, file))
        if old.args != new.args:
            findings.append(Finding(
                "medium", "MCP_ARGUMENTS_CHANGED", name,
                "The server argument list changed; argument values are not displayed.",
                "Review the new arguments in the source configuration and check for paths, flags, or embedded credentials.", file,
            ))
        if old.url_fingerprint != new.url_fingerprint:
            findings.append(Finding(
                "high", "MCP_ENDPOINT_CHANGED", name,
                "The server endpoint host changed.",
                "Verify the new endpoint and transport security before approving.", file,
            ))
            findings.extend(_server_risk_findings(new, file))
        old_names, new_names = set(old.env_names), set(new.env_names)
        for env_name in sorted(new_names - old_names):
            sensitive = bool(SECRET_NAME_RE.search(env_name))
            findings.append(Finding(
                "medium" if sensitive else "low",
                "MCP_SENSITIVE_ENV_ADDED" if sensitive else "MCP_ENV_ADDED",
                name,
                f"A new environment variable name was added: {env_name}. Its value is never displayed.",
                "Confirm that the variable is required and that its value is supplied through a secret manager, not committed to the repository.", file,
            ))
        for env_name in sorted(old_names - new_names):
            findings.append(Finding(
                "info", "MCP_ENV_REMOVED", name,
                f"An environment variable was removed: {env_name}.",
                "Confirm that removing this variable does not break the server.", file,
            ))
        old_fp, new_fp = dict(old.env_fingerprint), dict(new.env_fingerprint)
        for env_name in sorted(old_names & new_names):
            if old_fp.get(env_name) != new_fp.get(env_name):
                findings.append(Finding(
                    "medium", "MCP_ENV_VALUE_CHANGED", name,
                    f"The value for environment variable '{env_name}' changed; both values are redacted.",
                    "Verify the change through your approved secret-management process. Do not place secret values in configuration files.", file,
                ))
        if _has_wildcard_permission(new.raw) and not _has_wildcard_permission(old.raw):
            findings.append(Finding(
                "high", "MCP_WILDCARD_PERMISSION", name,
                "A wildcard or 'all' value appeared in a recognized permission-related field.",
                "Replace broad access with an explicit allowlist. This heuristic only checks recognized field names.", file,
            ))

    # Stable ordering helps produce repeatable CI output and tests.
    severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}
    unique = {(f.severity, f.rule_id, f.server, f.message, f.recommendation, f.file): f for f in findings}
    return sorted(unique.values(), key=lambda f: (severity_order.get(f.severity, 9), f.file or "", f.server, f.rule_id))


def _server_risk_findings(server: Server, file: str | None) -> list[Finding]:
    findings: list[Finding] = []
    if server.command in SHELL_COMMANDS:
        findings.append(Finding(
            "high", "MCP_SHELL_EXECUTABLE", server.name,
            "The server is configured to launch a shell executable.",
            "Confirm that shell access is necessary, constrain permitted operations, and avoid broad filesystem or network access.", file,
        ))
    elif server.command in NETWORK_COMMANDS:
        findings.append(Finding(
            "medium", "MCP_NETWORK_UTILITY", server.name,
            "The server is configured to launch a network-capable utility.",
            "Confirm the expected destinations and constrain network access where possible.", file,
        ))
    if server.url:
        findings.append(Finding(
            "medium", "MCP_REMOTE_ENDPOINT", server.name,
            f"The server uses a remote HTTP(S) endpoint host: {server.url}.",
            "Verify ownership, transport security, authentication, and data-handling terms for this endpoint.", file,
        ))
    if _has_wildcard_permission(server.raw):
        findings.append(Finding(
            "high", "MCP_WILDCARD_PERMISSION", server.name,
            "A wildcard or 'all' value appears in a recognized permission-related field.",
            "Replace broad access with an explicit allowlist. This heuristic only checks recognized field names.", file,
        ))
    return findings


def _is_candidate_config(path: Path) -> bool:
    name = path.name.lower()
    return name in {"mcp.json", "claude_desktop_config.json"} or name.endswith(".mcp.json")


def _candidate_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    count = 0
    for path in root.rglob("*.json"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        count += 1
        if count > MAX_TREE_JSON_FILES:
            raise ValueError(f"Repository contains more than {MAX_TREE_JSON_FILES:,} JSON files; refusing an unbounded scan")
        if not path.is_file() or path.is_symlink() or path.stat().st_size > MAX_CONFIG_BYTES:
            continue
        if _is_candidate_config(path):
            rel = path.relative_to(root).as_posix()
            files[rel] = path
            continue
        # Also discover custom filenames that actually contain an MCP server map.
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("mcpServers"), dict):
                rel = path.relative_to(root).as_posix()
                files[rel] = path
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
    return files


def compare_trees(before_dir: str | Path, after_dir: str | Path) -> list[Finding]:
    """Compare MCP config files across two repository directory snapshots."""
    before_root, after_root = Path(before_dir), Path(after_dir)
    if not before_root.is_dir() or not after_root.is_dir():
        raise ValueError("Both before and after paths must be directories")
    old_files = _candidate_files(before_root)
    new_files = _candidate_files(after_root)
    findings: list[Finding] = []
    for rel in sorted(old_files.keys() | new_files.keys()):
        old_data = load_config(old_files[rel]) if rel in old_files else {"mcpServers": {}}
        new_data = load_config(new_files[rel]) if rel in new_files else {"mcpServers": {}}
        # Skip known-named files that do not contain MCP configuration.
        if not isinstance(old_data.get("mcpServers", {}), dict) or not isinstance(new_data.get("mcpServers", {}), dict):
            continue
        findings.extend(compare_configs(old_data, new_data, file=rel))
    return findings


def _md_escape(value: str) -> str:
    """Escape untrusted labels/messages before placing them in a Markdown report."""
    text = re.sub(r"[\r\n\t]+", " ", str(value))
    for char in ("\\", "`", "*", "_", "[", "]", "|", "<", ">"):
        text = text.replace(char, "\\" + char)
    return text


def render_markdown(findings: list[Finding], title: str = "Permission Delta report") -> str:
    counts = {level: sum(1 for finding in findings if finding.severity == level) for level in ("high", "medium", "low", "info")}
    lines = [f"## {_md_escape(title)}", "", "| Severity | Count |", "|---|---:|"]
    lines.extend(f"| {level.title()} | {count} |" for level, count in counts.items())
    lines.append("")
    if not findings:
        lines.append("No MCP configuration changes requiring review were detected in the scanned files.")
    else:
        lines.append("Findings are heuristic review prompts, not proof of a vulnerability.")
        lines.append("")
        for finding in findings:
            prefix = f"`{_md_escape(finding.file)}` · " if finding.file else ""
            lines.extend([
                f"### [{finding.severity.upper()}] {prefix}{finding.rule_id}",
                f"**Server:** `{_md_escape(finding.server)}`  ",
                _md_escape(finding.message),
                f"**Suggested review:** {_md_escape(finding.recommendation)}",
                "",
            ])
    lines.extend([
        "---",
        "_Privacy: environment-variable values, command arguments, URL paths, URL queries and fragments are not included in this report._",
    ])
    return "\n".join(lines).rstrip() + "\n"
