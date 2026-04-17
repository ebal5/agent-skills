# coupling-core API reference

`coupling-core` が公開する Python library と CLI の使い方。
SKILL.md は**定義のみ**に絞る方針のため、library import や CLI 仕様など
operational な情報はこちらに分離する。

## Python library

`src/coupling_core/` が純粋計算ライブラリを提供する。
I/O・argparse を持たない pure function のみで構成。

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("<skill-root>/src")))

from coupling_core.balance import balance_score, interpret, recommend_rebalance

score = balance_score(8, 6, 9)   # => 3
verdict = interpret(score)        # => "不均衡"
hints = recommend_rebalance(8, 6, 9)
```

`<skill-root>` は `coupling-core` skill のインストール先 (user scope:
`~/.claude/skills/coupling-core`, project scope: `.claude/skills/coupling-core` など)。

**注意**: 当 skill には `pyproject.toml` が同梱されていないため、
外部パッケージとしての import は `sys.path` 経由に限られる。
別 skill から再利用する場合のインストール経路は open issue
(packaging 整備) で追跡中。

## CLI

`scripts/balance.py` は library を薄く包んだ uv シェバン CLI。

```bash
uv run skills/coupling-core/scripts/balance.py <strength> <distance> <volatility>
```

### 出力例

```json
{
  "strength": 8,
  "distance": 6,
  "volatility": 9,
  "score": 3,
  "verdict": "不均衡",
  "hints": [
    "強度を下げる (契約化 / 抽象境界)",
    "変更後は再度スコアを計算して均衡を確認する"
  ]
}
```

### フィールド

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `score` | int | 均衡度（1-10） |
| `verdict` | str | "良好" / "許容" / "不均衡" |
| `hints` | list[str] | 優先的に調整すべき次元への具体的なアドバイス |

### Exit code

引数が 1-10 の範囲外の場合は exit 1。
エラー出力契約の詳細は別途 open issue で仕様化中。
