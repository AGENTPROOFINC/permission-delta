import json
import tempfile
import unittest
from pathlib import Path

from permission_delta.core import compare_configs, compare_trees, load_config, render_markdown


class CompareConfigTests(unittest.TestCase):
    def test_added_server_and_shell_are_flagged(self):
        findings = compare_configs(
            {"mcpServers": {}},
            {"mcpServers": {"runner": {"command": "bash", "args": ["-c", "echo hi"]}}},
        )
        ids = {item.rule_id for item in findings}
        self.assertIn("MCP_SERVER_ADDED", ids)
        self.assertIn("MCP_SHELL_EXECUTABLE", ids)

    def test_command_change_is_flagged_without_echoing_command(self):
        findings = compare_configs(
            {"mcpServers": {"x": {"command": "node", "args": ["old.js"]}}},
            {"mcpServers": {"x": {"command": "bash", "args": ["-c", "echo PRIVATE_ARGUMENT"]}}},
        )
        report = render_markdown(findings)
        self.assertIn("MCP_COMMAND_CHANGED", report)
        self.assertNotIn("PRIVATE_ARGUMENT", report)

    def test_secret_values_never_appear_in_report(self):
        secret_old = "OLD_SUPER_SECRET_VALUE"
        secret_new = "NEW_SUPER_SECRET_VALUE"
        findings = compare_configs(
            {"mcpServers": {"x": {"command": "node", "env": {"API_TOKEN": secret_old}}}},
            {"mcpServers": {"x": {"command": "node", "env": {"API_TOKEN": secret_new}}}},
        )
        report = render_markdown(findings)
        self.assertIn("API\\_TOKEN", report)
        self.assertNotIn(secret_old, report)
        self.assertNotIn(secret_new, report)

    def test_url_credentials_path_query_are_not_reported(self):
        private_url = "https://user:pass@example.com/private/path?token=ABC123"
        findings = compare_configs(
            {"mcpServers": {}},
            {"mcpServers": {"remote": {"url": private_url}}},
        )
        report = render_markdown(findings)
        self.assertIn("example.com", report)
        for forbidden in ("user", "pass", "private/path", "ABC123", "token="):
            self.assertNotIn(forbidden, report)

    def test_url_path_or_query_change_is_detected_without_exposing_them(self):
        before = {"mcpServers": {"remote": {"url": "https://example.com/v1?token=oldsecret"}}}
        after = {"mcpServers": {"remote": {"url": "https://example.com/v2?token=newsecret"}}}
        report = render_markdown(compare_configs(before, after))
        self.assertIn("MCP_ENDPOINT_CHANGED", report)
        self.assertNotIn("oldsecret", report)
        self.assertNotIn("newsecret", report)
        self.assertNotIn("/v2", report)

    def test_markdown_injection_in_config_names_is_escaped(self):
        name = "safe`\n### injected"
        findings = compare_configs({"mcpServers": {}}, {"mcpServers": {name: {"command": "bash"}}})
        report = render_markdown(findings)
        self.assertNotIn("\n### injected", report)
        self.assertIn("\\`", report)

    def test_wildcard_permission_is_detected(self):
        findings = compare_configs(
            {"mcpServers": {"x": {"command": "node", "permissions": {"tools": ["read"]}}}},
            {"mcpServers": {"x": {"command": "node", "permissions": {"tools": ["*"]}}}},
        )
        self.assertIn("MCP_WILDCARD_PERMISSION", {item.rule_id for item in findings})

    def test_server_removal_is_info(self):
        findings = compare_configs(
            {"mcpServers": {"x": {"command": "node"}}},
            {"mcpServers": {}},
        )
        self.assertEqual(findings[0].severity, "info")
        self.assertEqual(findings[0].rule_id, "MCP_SERVER_REMOVED")

    def test_non_mcp_json_is_empty(self):
        self.assertEqual(compare_configs({"other": True}, {"other": False}), [])


class FileAndTreeTests(unittest.TestCase):
    def test_invalid_json_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text("{bad", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Invalid or unreadable JSON"):
                load_config(path)

    def test_tree_diff_compares_added_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before"
            after = root / "after"
            before.mkdir()
            after.mkdir()
            (after / "mcp.json").write_text(json.dumps({"mcpServers": {"x": {"command": "bash"}}}), encoding="utf-8")
            findings = compare_trees(before, after)
            ids = {item.rule_id for item in findings}
            self.assertIn("MCP_SERVER_ADDED", ids)
            self.assertIn("MCP_SHELL_EXECUTABLE", ids)
            self.assertEqual(findings[0].file, "mcp.json")

    def test_tree_diff_reports_removed_config_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before = root / "before"
            after = root / "after"
            before.mkdir()
            after.mkdir()
            (before / "mcp.json").write_text(json.dumps({"mcpServers": {"x": {"command": "node"}}}), encoding="utf-8")
            findings = compare_trees(before, after)
            self.assertIn("MCP_SERVER_REMOVED", {item.rule_id for item in findings})


if __name__ == "__main__":
    unittest.main()
