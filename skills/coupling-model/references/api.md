# coupling-model API reference

`coupling-model` は均衡結合方程式を計算する **self-contained CLI** を
`scripts/balance.py` として提供する。SKILL.md は定義のみに絞る方針のため、
CLI の使い方・JSON 契約・エラー envelope など operational な情報はこちら
に分離している。

## 設計方針

v0.2.2 時点で、pure Python library (`src/coupling_core/`) は**廃止**した。

- `gh skill install` はファイルをコピーするだけで `pip install` 相当のフックが
  ないため、Python package として別 skill (e.g. 将来の `coupling-audit`) から
  import する経路が存在しなかった。
- 結果、library 層は CLI 内でしか使われず、責務の重複だけが残っていた。
- v0.2.2 で `balance_score` / `interpret` / `recommend_rebalance` を
  `scripts/balance.py` に inline し、library layer を削除。
- 別 skill から再利用する場合は `subprocess` で CLI を呼ぶか、同じ Python
  プロセスから import したい場合はファイル path を `sys.path` に追加して
  `import balance` する（ただし公式 API は CLI と明言）。

## CLI

```bash
uv run skills/coupling-model/scripts/balance.py <strength> <distance> <volatility>
```

各引数は 1-10 の整数。

### 出力 envelope（成功時、exit 0）

```json
{
  "ok": true,
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

### 出力 envelope（範囲外エラー、exit 1）

```json
{"ok": false, "error": "strength must be between 1 and 10, got 11", "field": "strength", "got": 11}
```

### 出力 envelope（型エラー、exit 1 or 2）

```json
{"ok": false, "error": "argument strength: strength must be an integer, got 'abc'"}
```

argparse の内部慣習により型エラーは **exit 2**、ValueError 経由の範囲エラーは
**exit 1**。どちらも **stdout に JSON** を出力するので、エージェントは
stdout のみをパースすれば成否判定できる。

### フィールド定義

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `ok` | bool | 成功時 `true`, エラー時 `false` |
| `score` | int | 均衡度（1-10） — 成功時のみ |
| `verdict` | str | "良好" / "許容" / "不均衡" — 成功時のみ |
| `hints` | list[str] | 推奨アクション — 成功時のみ |
| `error` | str | 原因メッセージ — エラー時のみ |
| `field` | str | 範囲エラー時のフィールド名 — 範囲エラー時のみ |
| `got` | int | 与えられた値 — 範囲エラー時のみ |

### Exit code マトリクス

| 状況 | exit | stdout 形状 |
| --- | --- | --- |
| 正常 | 0 | `{"ok": true, "score": ..., ...}` |
| 値が 1-10 の範囲外 | 1 | `{"ok": false, "error": ..., "field": ..., "got": ...}` |
| 非整数 / 引数不足 | 2 | `{"ok": false, "error": ...}` |

## エージェント呼び出し例

Python subprocess から:

```python
import json
import subprocess

result = subprocess.run(
    ["uv", "run", "skills/coupling-model/scripts/balance.py", "8", "6", "9"],
    capture_output=True,
    text=True,
    check=False,
)
envelope = json.loads(result.stdout)
if envelope["ok"]:
    print(envelope["score"], envelope["verdict"])
else:
    print("error:", envelope["error"])
```

exit code とは独立に、stdout の `ok` フラグで成否判定できる。
