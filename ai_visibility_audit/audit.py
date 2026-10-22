"""Ask each question once and detect brand/competitor mentions.

Mention detection is deliberately simple: a case-insensitive substring
match. It reports a fact ("mentioned / not mentioned"), never a ranking
or a quality score.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass, field

from .config import Config


@dataclass
class QuestionResult:
    question: str
    answer: str
    brand_mentioned: bool
    competitors_mentioned: list[str] = field(default_factory=list)

    @property
    def excerpt(self) -> str:
        text = self.answer.strip().replace("\n", " ")
        return text[:300]


def find_mentions(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def _call_model(config: Config, question: str, api_key: str) -> str:
    url = config.base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": config.model,
        "messages": [{"role": "user", "content": question}],
        "temperature": 0,
        "max_tokens": config.max_tokens,
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"接口返回 {exc.code}：{detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"接口请求失败：{exc.reason}") from exc

    choices = body.get("choices", [])
    if not choices:
        raise RuntimeError(f"接口返回里没有 choices：{str(body)[:500]}")
    return str(choices[0].get("message", {}).get("content", ""))


# Dry-run answers are labelled as sample data in the report header.
_DRY_RUN_ANSWERS = [
    "可以看看示例品牌，它在本地供应商里口碑不错，竞品A 也常被提到。",
    "这类需求一般会推荐竞品B，先对比几家的报价再定。",
]


def run_audit(config: Config, dry_run: bool = False) -> list[QuestionResult]:
    api_key = ""
    if not dry_run:
        api_key = os.environ.get("AI_VISIBILITY_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "没有找到 API key：请先 export AI_VISIBILITY_API_KEY=你的 key，"
                "不要把 key 写进配置文件"
            )

    results: list[QuestionResult] = []
    for index, question in enumerate(config.questions):
        if dry_run:
            answer = _DRY_RUN_ANSWERS[index % len(_DRY_RUN_ANSWERS)]
        else:
            answer = _call_model(config, question, api_key)
        mentioned = find_mentions(answer, config.brand_terms)
        competitors = find_mentions(answer, config.competitors)
        results.append(
            QuestionResult(
                question=question,
                answer=answer,
                brand_mentioned=bool(mentioned),
                competitors_mentioned=competitors,
            )
        )
    return results
