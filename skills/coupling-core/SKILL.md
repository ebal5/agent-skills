---
name: coupling-core
description: |
  3 次元モデル (統合強度 × 距離 × 変動性) と均衡結合方程式の定義・スケール・
  解釈帯をまとめた共有参照スキル。用語・式・判定基準を単一ソースとして
  coupling-design-advisor や将来の coupling-audit / coupling-rebalance が参照する。

  発火条件:
  - 「均衡結合」「結合バランス」「3 次元モデル」の用語定義を確認したいとき
  - balance スコアの解釈帯を参照したいとき
  - coupling-* 系スキルの前提として読み込まれる

  発火しない:
  - 設計相談そのもの → coupling-design-advisor
  - 既存コードの計測 → coupling-audit (未実装)
allowed-tools: Read, Bash(uv run:*)
model: sonnet
effort: low
license: MIT
metadata:
  origin: "https://github.com/ebal5/agent-skills"
---

# coupling-core

## 概要

本スキルは『ソフトウェア設計の結合バランス』が提示する **3 次元モデル（統合強度 × 距離 × 変動性）** と
**均衡結合方程式** を蒸留した共有基盤である。
coupling-design-advisor・coupling-audit・coupling-rebalance の各スキルが参照する
用語定義・スケール変換・バランス計算を一箇所に集約し、プロジェクトをまたいだ一貫した設計議論を可能にする。

## 用語

| 用語 | 定義 |
| --- | --- |
| **統合強度 (Strength)** | 下流が上流の何をどれだけ知っているかの度合い。コントラクト結合（最小）から侵入結合（最大）までを 1-10 で表す。 |
| **距離 (Distance)** | モジュール間の物理的・組織的隔たり。同一オブジェクト内（最近傍）から別ベンダーシステム（最遠）までを 1-10 で表す。 |
| **変動性 (Volatility)** | モジュールが将来どの程度変化するかの期待値。進化しないレガシー（低）からコアサブドメイン（高）までを 1-10 で表す。 |
| **均衡度 (Balance score)** | 均衡結合方程式から得られる 1-10 の整数スコア。高いほど結合がバランスしている。 |
| **コアサブドメイン** | ビジネス上の競争優位を担う中核領域。変動性が高く、設計投資が最も見合うサブドメイン種別。 |

## 1-10 スケール表

| 次元 | 1 | 3 | 5 | 8 | 10 |
| --- | --- | --- | --- | --- | --- |
| **統合強度** | コントラクト結合 | モデル結合 | （中間） | 機能結合 | 侵入結合 |
| **距離** | 同一オブジェクト | 同一パッケージ | 別モジュール | 別ライブラリ | 別ベンダーシステム |
| **変動性** | 進化しないレガシー | 支援/汎用サブドメイン | （中間） | （中間） | コアサブドメイン |

## 均衡結合方程式

```text
均衡度 = max(|強度 - 距離|, 10 - 変動性) + 1
```

### 解釈帯

| スコア | 判定 | 意味 |
| --- | --- | --- |
| 8〜10 | **良好** | バランスが取れており、現状維持または軽微な調整で十分 |
| 5〜7 | **許容** | 許容範囲内だが改善余地あり。優先度低めで監視を続ける |
| 1〜4 | **不均衡** | 見直し必須。設計的なリスクが高い状態 |

## Python library

当 skill repo 内の `src/coupling_core/` が純粋計算ライブラリを提供する。

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path("<skill-root>/src")))

from coupling_core.balance import balance_score, interpret, recommend_rebalance

score = balance_score(8, 6, 9)   # => 3
verdict = interpret(score)        # => "不均衡"
hints = recommend_rebalance(8, 6, 9)
```

`scripts/balance.py` は同ライブラリを薄く包んだ CLI ラッパーであり、
ライブラリ自体は I/O・argparse を持たない純粋関数で構成されている。

## CLI

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

各フィールドの意味:

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `score` | int | 均衡度（1-10） |
| `verdict` | str | "良好" / "許容" / "不均衡" |
| `hints` | list[str] | 優先的に調整すべき次元への具体的なアドバイス |

引数が 1-10 の範囲外の場合は exit 1 でエラーを返す。

## 注意点

- **正確な科学ではない**: 本書自身が「これは正確な科学ではない」と明言している。数値の絶対値に固執せず、相対比較と議論の起点として使用すること。
- **プロジェクトごとのキャリブレーションが必要**: スケール定義はチームや組織の文脈によって異なる。プロジェクト固有の `.coupling.yaml` などで値を上書きし、常に同じ基準で議論できる環境を整えること。
