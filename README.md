# ai-visibility-audit

> A tiny CLI to check whether AI answers mention your brand, and how you compare to competitors. No ranking promises, no scraping.

一个很小的命令行工具：输入品牌名、竞品和一组用户可能会问的问题，
用你自己的 API key 调一个 OpenAI 兼容接口，输出一份 Markdown 审计报告：
AI 在回答这些问题时有没有提到你、怎么提到你、和竞品比缺了哪些问题。

它**不承诺排名、不做评分、不爬任何 AI 网页**，只做一件事：
把“被提到 / 没被提到”这个事实摆出来。

## 快速开始

```bash
# 1. 复制示例配置，改成你自己的品牌和问题
cp config.example.toml config.toml

# 2. 设置 API key（只走环境变量，不要写进配置文件）
export AI_VISIBILITY_API_KEY="你的 key"

# 3. 先校验配置，不花钱
python3 -m ai_visibility_audit --config config.toml --check-config

# 4. 跑一次审计
python3 -m ai_visibility_audit --config config.toml --out report.md --json report.json
```

不想花钱先试骨架，可以用 dry-run（输出会明确标注是示例数据）：

```bash
python3 -m ai_visibility_audit --config config.example.toml --out report.md --dry-run
```

## 配置说明（config.toml）

| 字段 | 说明 |
| --- | --- |
| `brand` | 你的品牌名 |
| `aliases` | 品牌的别名/英文名，提及检测会一起算 |
| `competitors` | 竞品名列表 |
| `questions` | 用户可能会问的问题，建议 10 个左右 |
| `[model] base_url` | OpenAI 兼容接口地址，例如 `https://api.example.com/v1` |
| `[model] model` | 模型名 |
| `[model] max_tokens` | 可选，默认 800 |

## 报告里有什么

- 总览：共问了几题、品牌被提到几题、每个竞品被提到几题
- 逐题明细：每题的回答摘要、提到了谁
- 缺口清单：品牌**没被提到**的那些问题（只列事实，不给排名承诺）

示例见 `examples/sample-report.md`。

## 开发

```bash
python3 -m unittest discover -s tests -v
```

## 注意

- `config.toml` 不要提交，`.gitignore` 已经排除了它和生成的报告

## Changelog

见 `CHANGELOG.md`。
