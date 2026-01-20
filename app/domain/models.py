from dataclasses import dataclass
from typing import Optional

from app.domain.enums import MoveQuality



@dataclass(frozen=True)
class Opening:
    eco: str
    name: str


@dataclass(frozen=True)
class EvaluatedMove:
    """
    Result of analyzing a single move.
    """

    move_number: int
    color: str  # "white" or "black"
    uci: str
    san: str

    eval_before: float
    eval_after: float
    eval_loss: float

    quality: MoveQuality

    is_check: bool
    is_checkmate: bool
    is_capture: bool

    clock: Optional[float] = None

        # ✅ NEW (additive)
    best_move_uci: Optional[str] = None
    best_move_san: Optional[str] = None
