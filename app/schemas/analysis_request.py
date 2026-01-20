from pydantic import BaseModel, Field
from typing import Optional


class AnalysisRequestSchema(BaseModel):
    pgn: str = Field(
        ...,
        description="Full PGN text including headers and moves",
        example='''[Event "Test"]
[Site "?"]
[Date "2025.01.01"]
[Round "-"]
[White "White"]
[Black "Black"]
[Result "*"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *
''',
    )

    depth: Optional[int] = Field(
        default=None,
        description="Stockfish search depth override",
        example=20,
    )

    player_elo: Optional[int] = Field(
        default=1200,
        description="Approximate player ELO used for brilliance scaling",
        example=1200,
        ge=100,
        le=3000,
    )
