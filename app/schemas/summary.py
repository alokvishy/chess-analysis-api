from typing import Iterable
from pydantic import BaseModel

from app.domain.models import EvaluatedMove
from app.domain.enums import MoveQuality


# ---------- EXISTING METRICS (UNCHANGED) ----------

def acpl(moves: Iterable[EvaluatedMove], color: str) -> float:
    """
    Average Centipawn Loss for a given color.
    """
    losses = [
        m.eval_loss * 100
        for m in moves
        if m.color == color
    ]

    if not losses:
        return 0.0

    return round(sum(losses) / len(losses), 2)


def accuracy_percentage(moves: Iterable[EvaluatedMove], color: str) -> float:
    """
    Rough accuracy metric based on move quality.
    """
    weights = {
        MoveQuality.BEST: 1.0,
        MoveQuality.GOOD: 0.9,
        MoveQuality.INACCURACY: 0.6,
        MoveQuality.MISTAKE: 0.3,
        MoveQuality.BLUNDER: 0.0,
    }

    player_moves = [m for m in moves if m.color == color]
    if not player_moves:
        return 0.0

    score = sum(weights[m.quality] for m in player_moves)
    return round((score / len(player_moves)) * 100, 2)


def count_by_quality(moves: Iterable[EvaluatedMove], color: str) -> dict:
    counts = {
        "blunders": 0,
        "mistakes": 0,
        "inaccuracies": 0,
    }

    for m in moves:
        if m.color != color:
            continue

        if m.quality == MoveQuality.BLUNDER:
            counts["blunders"] += 1
        elif m.quality == MoveQuality.MISTAKE:
            counts["mistakes"] += 1
        elif m.quality == MoveQuality.INACCURACY:
            counts["inaccuracies"] += 1

    return counts


# ---------- NEW: ELO ESTIMATION SCHEMA ----------

class EloEstimateSchema(BaseModel):
    elo: int
    confidence: float


# ---------- UPDATED SUMMARY SCHEMAS ----------

class PlayerSummarySchema(BaseModel):
    acpl: float
    accuracy: float
    blunders: int
    mistakes: int
    inaccuracies: int

    estimated_elo: EloEstimateSchema


class GameSummarySchema(BaseModel):
    white: PlayerSummarySchema
    black: PlayerSummarySchema
    verdict: str
