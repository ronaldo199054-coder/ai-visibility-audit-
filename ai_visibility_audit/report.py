"""Render the Markdown report and the JSON payload."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .audit import QuestionResult
from .config import Config


def build_report(config: Config, results: list[QuestionResult], dry_run: bool = False) -> tuple[str, dict]:
    total = len(results)
    brand_hits = sum(1 for r in results if r.brand_mentioned)
    competitor_hits = {
        name: sum(1 for r in results if name in r.competitors_mentioned)
        for name in config.competitors
    }
    generated_at = datetime.now(timezone.utc).isoformat()

    lines: list[str] = []
    if dry_run:
        lines.append("> DRY RUN：以下为示例数据，非真实审计结果，仅用于跑通流程。")
        lines.append("")
    lines.append(f"# AI 可见度自查报告：{config.brand}")
    lines.append("")
    lines.append(f"- 生成时间：{generated_at}")
    lines.append(f"- 模型：{config.model}")
    lines.append(f"- 问题总数：{total}")
    lines.append(f"- 品牌被提到：{brand_hits} / {total} 题")
    for name, hits in competitor_hits.items():
        lines.append(f"- 竞品 {name} 被提到：{hits} / {total} 题")
    lines.append("")
    lines.append("## 逐题明细")
    lines.append("")
    for i, result in enumerate(results, 1):
        mentioned = "提到品牌" if result.brand_mentioned else "未提到品牌"
        competitors = "、".join(result.competitors_mentioned) if result.competitors_mentioned else "无"
        lines.append(f"### {i}. {result.question}")
        lines.append("")
        lines.append(f"- 结果：{mentioned}；提到竞品：{competitors}")
        lines.append(f"- 回答摘要：{result.excerpt}")
        lines.append("")
    gaps = [r.question for r in results if not r.brand_mentioned]
    lines.append("## 缺口清单（品牌未被提到的问题）")
    lines.append("")
    if gaps:
        for question in gaps:
            lines.append(f"- {question}")
    else:
        lines.append("- 无：所有问题都提到了品牌。")
    lines.append("")

    payload = {
        "brand": config.brand,
        "model": config.model,
        "generated_at": generated_at,
        "dry_run": dry_run,
        "total": total,
        "brand_mentioned": brand_hits,
        "competitor_mentioned": competitor_hits,
        "results": [
            {
                "question": r.question,
                "brand_mentioned": r.brand_mentioned,
                "competitors_mentioned": r.competitors_mentioned,
                "excerpt": r.excerpt,
            }
            for r in results
        ],
    }
    return "\n".join(lines), payload


def write_outputs(
    markdown: str,
    payload: dict,
    out_path: str | Path,
    json_path: str | Path | None,
) -> None:
    out = Path(out_path)
    out.write_text(markdown, encoding="utf-8")
    if json_path:
        Path(json_path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
