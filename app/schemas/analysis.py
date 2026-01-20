from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.summary import GameSummarySchema
from app.schemas.key_moves import KeyMomentSchema


class MoveAnalysisSchema(BaseModel):
    move_number: int = Field(..., example=1)
    color: str = Field(..., example="white")

    uci: str = Field(..., example="e2e4")
    san: str = Field(..., example="e4")

    # ✅ BOOK moves have no engine eval → must be Optional
    eval_before: Optional[float] = Field(None, example=0.0)
    eval_after: Optional[float] = Field(None, example=0.2)

    # eval_loss is always defined (0 for BOOK moves)
    eval_loss: float = Field(..., example=0.0)

    quality: str = Field(..., example="BEST")

    is_check: bool
    is_checkmate: bool
    is_capture: bool

    clock: Optional[float] = None
        # ✅ NEW
    best_move_uci: Optional[str] = Field(
        None, example="d2d4"
    )
    best_move_san: Optional[str] = Field(
        None, example="d4"
    )


class OpeningSchema(BaseModel):
    eco: str = Field(..., example="B20")
    name: str = Field(..., example="Sicilian Defense")


class AnalysisResponseSchema(BaseModel):
    opening: Optional[OpeningSchema]
    moves: List[MoveAnalysisSchema]
    summary: GameSummarySchema
    key_moments: List[KeyMomentSchema]
