from dataclasses import dataclass
from typing import List

from app.domain.models import EvaluatedMove
from app.domain.enums import MoveQuality


@dataclass(frozen=True)
class KeyMoment:
    """
    A critical moment in the game.
    """
    move_number: int
    color: str
    uci: str
    san: str
    reason: str
    eval_before: float
    eval_after: float


def detect_key_moments(moves: List[EvaluatedMove]) -> List[KeyMoment]:
    """
    Detect key moments in a game.
    BOOK moves and moves without engine evaluations are ignored.
    """

    key_moments: List[KeyMoment] = []

    for move in moves:
        # 🚫 Ignore opening book moves
        if move.quality == MoveQuality.BOOK:
            continue

        # 🚫 Ignore moves without valid evaluations
        if move.eval_before is None or move.eval_after is None:
            continue

        # -----------------------------
        # 1️⃣ Blunders (always key moments)
        # -----------------------------
        if move.quality == MoveQuality.BLUNDER:
            key_moments.append(
                KeyMoment(
                    move_number=move.move_number,
                    color=move.color,
                    uci=move.uci,
                    san=move.san,
                    reason="Blunder",
                    eval_before=move.eval_before,
                    eval_after=move.eval_after,
                )
            )
            continue

        # -----------------------------
        # 2️⃣ Turning points (big eval swing)
        # -----------------------------
        swing = abs(move.eval_after - move.eval_before)
        if swing >= 2.0:
            key_moments.append(
                KeyMoment(
                    move_number=move.move_number,
                    color=move.color,
                    uci=move.uci,
                    san=move.san,
                    reason="Turning point",
                    eval_before=move.eval_before,
                    eval_after=move.eval_after,
                )
            )
            continue

        # -----------------------------
        # 3️⃣ Missed wins
        # -----------------------------
        if move.color == "white":
            had_win = move.eval_before >= 3.0
            lost_win = move.eval_after < 2.0
        else:
            had_win = move.eval_before <= -3.0
            lost_win = move.eval_after > -2.0

        if had_win and lost_win:
            key_moments.append(
                KeyMoment(
                    move_number=move.move_number,
                    color=move.color,
                    uci=move.uci,
                    san=move.san,
                    reason="Missed win",
                    eval_before=move.eval_before,
                    eval_after=move.eval_after,
                )
            )

    return key_moments
