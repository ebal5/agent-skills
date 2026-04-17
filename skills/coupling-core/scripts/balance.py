#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""CLI wrapper around coupling_core.balance."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from coupling_core.balance import balance_score, interpret, recommend_rebalance


def main() -> int:
    parser = argparse.ArgumentParser(
        description="均衡結合方程式を計算し JSON で出力する"
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
