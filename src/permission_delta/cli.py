"""Command-line interface for Permission Delta."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import compare_configs, compare_trees, load_config, render_markdown

SEVERITY = {"info": 0, "low": 1, "medium": 2, "high": 3}


def _write_report(findings, output_format: str, output: str | None, title: str) -> None:
    if output_format == "json":
        text = json.dumps({"findings": [item.to_dict() for item in findings]}, indent=2, ensure_ascii=False) + "\n"
    else:
        text = render_markdown(findings, title=title)
    if output:
        Path(output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="permission-delta",
        description="Compare MCP server configuration changes without executing servers or exposing secret values.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser("compare", help="Compare two MCP JSON configuration files")
    compare.add_argument("before", help="Baseline JSON file")
    compare.add_argument("after", help="Proposed JSON file")
    compare.add_argument("--format", choices=("markdown", "json"), default="markdown")
    compare.add_argument("--output", help="Write report to a file instead of stdout")
    compare.add_argument("--fail-on", choices=("never", "low", "medium", "high"), default="never",
                         help="Return exit code 1 when a finding at or above this severity exists")

    tree = sub.add_parser("tree-diff", help="Compare MCP config files across two repository snapshots")
    tree.add_argument("--before-dir", required=True, help="Baseline repository directory")
    tree.add_argument("--after-dir", required=True, help="Proposed repository directory")
    tree.add_argument("--format", choices=("markdown", "json"), default="markdown")
    tree.add_argument("--output", help="Write report to a file instead of stdout")
    tree.add_argument("--fail-on", choices=("never", "low", "medium", "high"), default="never")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "compare":
            before = load_config(args.before)
            after = load_config(args.after)
            findings = compare_configs(before, after)
            title = "Permission Delta configuration comparison"
        else:
            findings = compare_trees(args.before_dir, args.after_dir)
            title = "Permission Delta pull request review"
        _write_report(findings, args.format, args.output, title)
        if args.fail_on != "never":
            threshold = SEVERITY[args.fail_on]
            if any(SEVERITY[item.severity] >= threshold for item in findings):
                return 1
        return 0
    except (ValueError, OSError) as exc:
        print(f"permission-delta: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
