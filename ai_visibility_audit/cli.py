"""CLI entry point."""

from __future__ import annotations

import argparse
import sys

from .audit import run_audit
from .config import load_config
from .report import build_report, write_outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-visibility-audit",
        description="用你自己的 API key 跑一遍品牌可见度自查，输出 Markdown 报告。",
    )
    parser.add_argument("--config", required=True, help="TOML 配置文件路径")
    parser.add_argument("--out", default="report.md", help="Markdown 报告输出路径")
    parser.add_argument("--json", default=None, help="可选：JSON 结果输出路径")
    parser.add_argument("--check-config", action="store_true", help="只校验配置，不调用接口")
    parser.add_argument("--dry-run", action="store_true", help="用示例数据跑通流程，不调用接口、不花钱")
    args = parser.parse_args(argv)

    try:
        config = load_config(args.config)
    except (FileNotFoundError, ValueError, OSError) as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    if args.check_config:
        print(f"配置 OK：品牌={config.brand}，问题={len(config.questions)} 个，模型={config.model}")
        return 0

    try:
        results = run_audit(config, dry_run=args.dry_run)
    except RuntimeError as exc:
        print(f"运行失败：{exc}", file=sys.stderr)
        return 1

    markdown, payload = build_report(config, results, dry_run=args.dry_run)
    write_outputs(markdown, payload, args.out, args.json)
    hits = sum(1 for r in results if r.brand_mentioned)
    print(f"完成：品牌被提到 {hits} / {len(results)} 题，报告已写到 {args.out}")
    return 0
