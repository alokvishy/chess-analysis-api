from typing import Optional
from pydantic import BaseModel, Field


class PlayRequestSchema(BaseModel):
    fen: str = Field(
        ...,
        description="Current board position in FEN",
        example="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
    )

    # Optional engine control (future-proof)
    depth: Optional[int] = Field(
        default=None,
        description="Stockfish search depth override",
        example=15,
    )
    elo: Optional[int] = Field(
    default=None,
    ge=400,
    le=3000,
    description="Limit engine strength to target ELO",
    example=1200,
    )


class PlayResponseSchema(BaseModel):
    engine_move_uci: str = Field(..., example="e7e5")
    engine_move_san: str = Field(..., example="e5")

    fen_after: str = Field(
        ...,
        description="FEN after engine move",
    )

    eval: float = Field(
        ...,
        description="Evaluation in pawns from White's perspective",
        example=0.32,
    )

    is_check: bool
    is_checkmate: bool

    engine_effective_elo: int
