from typing import Iterable
from app.domain.models import EvaluatedMove
from app.domain.enums import MoveQuality


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _player_moves(
    moves: Iterable[EvaluatedMove],
    color: str,
) -> list[EvaluatedMove]:
    """
    Returns only meaningful moves played by the given color.
    BOOK moves are excluded.
    """
    return [
        m for m in moves
        if m.color == color and m.quality != MoveQuality.BOOK
    ]


# -------------------------------------------------
# ACPL (Primary strength signal)
# -------------------------------------------------

def acpl(moves: Iterable[EvaluatedMove], color: str) -> float:
    """
    Average Centipawn Loss (ACPL) for a given player.

    - Only counts that player's moves
    - Excludes BOOK moves
    - Excludes zero-loss moves (engine-equal positions)
    """

    player_moves = _player_moves(moves, color)

    losses_cp = [
        m.eval_loss * 100
        for m in player_moves
        if m.eval_loss is not None and m.eval_loss > 0
    ]

    if not losses_cp:
        return 0.0

    return round(sum(losses_cp) / len(losses_cp), 2)


# -------------------------------------------------
# Accuracy (Secondary signal)
# -------------------------------------------------

def accuracy_percentage(moves: Iterable[EvaluatedMove], color: str) -> float:
    """
    Accuracy percentage based on move quality.

    This is a SUPPORTING metric, not dominant.
    Brilliancies do NOT push accuracy beyond 100.
    """

    weights = {
        MoveQuality.BRILLIANT: 1.0,
        MoveQuality.BEST: 1.0,
        MoveQuality.GOOD: 0.9,
        MoveQuality.INACCURACY: 0.7,
        MoveQuality.MISTAKE: 0.4,
        MoveQuality.BLUNDER: 0.0,
    }

    player_moves = _player_moves(moves, color)

    if not player_moves:
        return 0.0

    score = sum(weights[m.quality] for m in player_moves)
    accuracy = (score / len(player_moves)) * 100

    return round(min(100.0, accuracy), 2)


# -------------------------------------------------
# Error counts (used for ELO penalties)
# -------------------------------------------------

def count_by_quality(moves: Iterable[EvaluatedMove], color: str) -> dict:
    """
    Counts only meaningful mistakes by the player.
    BOOK moves are excluded.
    """

    counts = {
        "blunders": 0,
        "mistakes": 0,
        "inaccuracies": 0,
    }

    for m in _player_moves(moves, color):
        if m.quality == MoveQuality.BLUNDER:
            counts["blunders"] += 1
        elif m.quality == MoveQuality.MISTAKE:
            counts["mistakes"] += 1
        elif m.quality == MoveQuality.INACCURACY:
            counts["inaccuracies"] += 1

    return counts
