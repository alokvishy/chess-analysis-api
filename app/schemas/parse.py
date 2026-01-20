
from pydantic import BaseModel
from typing import List, Literal


class ParsedMoveSchema(BaseModel):
    move_number: int
    color: Literal["white", "black"]
    uci: str
    san: str
    fen_after: str


class ParseResponseSchema(BaseModel):
    pgn: str
    fen: str
    moves: List[ParsedMoveSchema]
