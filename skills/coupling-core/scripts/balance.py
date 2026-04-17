#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""均衡結合方程式の計算・解釈・改善ヒント出力ツール。

使い方:
    uv run scripts/balance.py <strength> <distance> <volatility>

各引数は 1-10 の整数。
"""

import argparse
import json
import sys


def balance_score(strength: int, distance: int, volatility: int) -> int:
    """均衡度を計算する。

    均衡度 = max(|強度 - 距離|, 10 - 変動性) + 1

    Args:
        strength: 統合強度 (1-10)
        distance: 距離 (1-10)
        volatility: 変動性 (1-10)

    Returns:
        均衡度スコア (1-11)

    Raises:
        ValueError: 引数が 1-10 の範囲外の場合
    """
    for name, val in [
        ("strength", strength),
        ("distance", distance),
        ("volatility", volatility),
    ]:
        if not (1 <= val <= 10):
            raise ValueError(f"{name} must be between 1 and 10, got {val}")
    return max(abs(strength - distance), 10 - volatility) + 1


def interpret(score: int) -> str:
    """均衡度スコアを解釈する。

    Args:
        score: 均衡度スコア (1-11)

    Returns:
        "良好" | "許容" | "不均衡"

    Raises:
        ValueError: スコアが 1-11 の範囲外の場合
    """
    if not (1 <= score <= 11):
        raise ValueError(f"score must be between 1 and 11, got {score}")
    if score >= 8:
        return "良好"
    if score >= 5:
        return "許容"
    return "不均衡"


def recommend_rebalance(strength: int, distance: int, volatility: int) -> list[str]:
    """改善ヒントを返す。

    どの次元を優先的に調整すべきかをヒューリスティックに判定する。

    Args:
        strength: 統合強度 (1-10)
        distance: 距離 (1-10)
        volatility: 変動性 (1-10)

    Returns:
        改善ヒントの文字列リスト
    """
    hints: list[str] = []
    sd_term = abs(strength - distance)
    v_term = 10 - volatility

    if sd_term >= v_term:
        # |強度 - 距離| が支配的
        if strength > distance:
            hints.append("強度を下げる (契約化 / 抽象境界)")
        else:
            hints.append("距離を縮める or 強度を上げる")
    else:
        # 10 - 変動性 が支配的
        hints.append("変動性低下を待つ or コアサブドメインなら分離強化")

    hints.append("変更後は再度スコアを計算して均衡を確認する")
    return hints


def main() -> int:
    """CLI エントリーポイント。"""
    parser = argparse.ArgumentParser(
        description="均衡結合方程式を計算し JSON で出力する",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
例:
    uv run scripts/balance.py 8 6 9
    uv run scripts/balance.py 3 3 3
""",
    )
    parser.add_argument("strength", type=int, help="統合強度 (1-10)")
    parser.add_argument("distance", type=int, help="距離 (1-10)")
    parser.add_argument("volatility", type=int, help="変動性 (1-10)")
    args = parser.parse_args()

    try:
        score = balance_score(args.strength, args.distance, args.volatility)
        verdict = interpret(score)
        hints = recommend_rebalance(args.strength, args.distance, args.volatility)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    result = {
        "strength": args.strength,
        "distance": args.distance,
        "volatility": args.volatility,
        "score": score,
        "verdict": verdict,
        "hints": hints,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
