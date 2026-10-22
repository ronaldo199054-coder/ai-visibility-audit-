"""Load and validate the TOML config. No API key lives here."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    brand: str
    aliases: list[str] = field(default_factory=list)
    competitors: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    base_url: str = ""
    model: str = ""
    max_tokens: int = 800

    @property
    def brand_terms(self) -> list[str]:
        terms = [self.brand, *self.aliases]
        # Keep order, drop empties and duplicates.
        seen: set[str] = set()
        out: list[str] = []
        for term in terms:
            term = term.strip()
            if term and term not in seen:
                seen.add(term)
                out.append(term)
        return out


def load_config(path: str | Path) -> Config:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在：{config_path}，先从 config.example.toml 复制一份")
    with config_path.open("rb") as f:
        data = tomllib.load(f)

    brand = str(data.get("brand", "")).strip()
    if not brand:
        raise ValueError("配置里 brand 不能为空")
    questions = [str(q).strip() for q in data.get("questions", []) if str(q).strip()]
    if not questions:
        raise ValueError("配置里 questions 不能为空，至少写 1 个问题")

    model_data = data.get("model", {})
    if not isinstance(model_data, dict):
        raise ValueError("配置里 [model] 必须是表格式")
    base_url = str(model_data.get("base_url", "")).strip()
    model = str(model_data.get("model", "")).strip()
    if not base_url or not model:
        raise ValueError("配置里 [model] 的 base_url 和 model 都不能为空")

    return Config(
        brand=brand,
        aliases=[str(a).strip() for a in data.get("aliases", []) if str(a).strip()],
        competitors=[str(c).strip() for c in data.get("competitors", []) if str(c).strip()],
        questions=questions,
        base_url=base_url,
        model=model,
        max_tokens=int(model_data.get("max_tokens", 800)),
    )
