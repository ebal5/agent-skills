#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""均衡結合方程式を計算し JSON で出力する self-contained CLI。

書籍『ソフトウェア設計の結合バランス』の 3 次元モデル
(統合強度 × 距離 × 変動性) と均衡結合方程式
`均衡度 = max(|強度 - 距離|, 10 - 変動性) + 1` を実装する。

出力は常に JSON 形式で stdout に出力される:

- 成功時 (exit 0): `{"ok": true, "strength": ..., "score": ..., ...}`
- 範囲外 (exit 1): `{"ok": false, "error": "...", "field": "...", "got": ...}`
- 型エラー (exit 2): `{"ok": false, "error": "..."}`

エージェントからの呼び出しでも stdout の JSON のみをパースすれば
成否判定できる。
"""

import argparse
import json
import sys


def balance_score(strength: int, distance: int, volatility: int) -> int:
    """均衡度を計算する。

    均衡度 = max(|強度 - 距離|, 10 - 変動性) + 1

    Raises:
        ValueError: 引数が 1-10 の範囲外の場合。メッセージは
            "<field> must be between 1 and 10, got <value>" 形式で、
            CLI wrapper がこれをパースしてフィールド名と値を抽出する。
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
    """均衡度スコアを解釈する。8-10=良好, 5-7=許容, 1-4=不均衡。"""
    if not (1 <= score <= 10):
        raise ValueError(f"score must be between 1 and 10, got {score}")
    if score >= 8:
        return "良好"
    if score >= 5:
        return "許容"
    return "不均衡"


def recommend_rebalance(strength: int, distance: int, volatility: int) -> list[str]:
    """改善ヒントを返す。どの次元を優先的に調整すべきかのヒューリスティック。"""
    hints: list[str] = []
    sd_term = abs(strength - distance)
    v_term = 10 - volatility

    if sd_term == 0 and v_term == 0:
        # 対称機能結合 + 高変動性 = 最悪例 (score=1)
        # case-studies 例 4 と同型。SD も V も最大限不均衡で、
        # 疎結合化 (強度↓) 以外に出口がない。
        hints.append("強度を下げる (所有権統合 / 単一サービス化)")
        hints.append("対称機能結合アンチパターンを疑う (case-studies 例 4 参照)")
    elif sd_term >= v_term:
        # SD 項が優勢 (タイケース含む)
        if strength > distance:
            hints.append("強度を下げる (契約化 / 抽象境界)")
        else:
            hints.append("距離を縮める or 強度を上げる")
    else:
        # 変動性項が優勢
        hints.append("変動性低下を待つ or コアサブドメインなら分離強化")

    hints.append("変更後は再度スコアを計算して均衡を確認する")
    return hints


class _JsonErrorParser(argparse.ArgumentParser):
    """argparse のエラーを JSON envelope に変換する ArgumentParser。

    型エラー (非整数入力など) や引数不足のとき、親クラスは stderr に
    prose を出して sys.exit(2) するため、stdout を parse する agent には
    空文字列が渡ってしまう。本サブクラスは stdout に JSON を出してから
    exit する。
    """

    def error(self, message: str) -> None:
        print(
            json.dumps({"ok": False, "error": message}, ensure_ascii=False),
            flush=True,
        )
        sys.exit(2)


def _int_arg(field_name: str):
    """argparse の type= に渡す整数パーサー。エラー時に field 情報を保持。"""

    def parse(value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{field_name} must be an integer, got {value!r}"
            )

    return parse


def _range_error_envelope(message: str) -> dict:
    """ValueError メッセージからフィールド情報を抽出して envelope を作る。

    balance_score が出す "strength must be between 1 and 10, got 11" 形式を
    パースして field / got を分離する。ベストエフォート: パースに失敗した
    場合は error 文字列のみを返す。
    """
    envelope: dict = {"ok": False, "error": message}
    parts = message.split()
    if parts:
        envelope["field"] = parts[0]
    if "got" in parts:
        idx = parts.index("got")
        if idx + 1 < len(parts):
            try:
                envelope["got"] = int(parts[idx + 1])
            except ValueError:
                envelope["got"] = parts[idx + 1]
    return envelope


def main() -> int:
    parser = _JsonErrorParser(description="均衡結合方程式を計算し JSON で出力する")
    parser.add_argument("strength", type=_int_arg("strength"), help="統合強度 (1-10)")
    parser.add_argument("distance", type=_int_arg("distance"), help="距離 (1-10)")
    parser.add_argument("volatility", type=_int_arg("volatility"), help="変動性 (1-10)")
    args = parser.parse_args()

    try:
        score = balance_score(args.strength, args.distance, args.volatility)
        verdict = interpret(score)
        hints = recommend_rebalance(args.strength, args.distance, args.volatility)
    except ValueError as e:
        print(
            json.dumps(_range_error_envelope(str(e)), ensure_ascii=False),
            flush=True,
        )
        return 1

    result = {
        "ok": True,
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
