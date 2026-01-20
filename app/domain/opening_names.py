import chess
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class OpeningInfo:
    eco: str
    name: str


# NORMALIZED FEN (first 4 fields only)
OPENING_BY_FEN: dict[str, OpeningInfo] = {
    # --- KING'S PAWN ---
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq": OpeningInfo(
        eco="B00",
        name="King's Pawn Opening",
    ),

    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq": OpeningInfo(
        eco="C20",
        name="King's Pawn Game",
    ),

    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq": OpeningInfo(
        eco="B20",
        name="Sicilian Defense",
    ),

    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq": OpeningInfo(
        eco="C40",
        name="King's Knight Opening",
    ),

    # --- QUEEN'S PAWN ---
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq": OpeningInfo(
        eco="D00",
        name="Queen's Pawn Opening",
    ),

    "rnbqkbnr/pppppppp/8/8/3P4/5N2/PPP1PPPP/RNBQKB1R b KQkq": OpeningInfo(
        eco="D02",
        name="Queen's Pawn Game",
    ),
        # --- RUY LOPEZ ---
    # Position after: 1.e4 e5 2.Nf3 Nc6 3.Bb5
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq": OpeningInfo(
        eco="C60",
        name="Ruy Lopez",
    ),

    # (optional) Morphy Defense after 3...a6
    "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq": OpeningInfo(
        eco="C60",
        name="Ruy Lopez, Morphy Defense",
    ),

    # Add more over time
}


def normalize_fen(board: chess.Board) -> str:
    """
    Normalize FEN by stripping move counters.
    """
    return " ".join(board.fen().split()[:3])


def detect_opening(board: chess.Board) -> Optional[OpeningInfo]:
    """
    Returns opening info if the position matches a known opening.
    """
    return OPENING_BY_FEN.get(normalize_fen(board))
