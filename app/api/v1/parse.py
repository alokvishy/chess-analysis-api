import io
import chess
import chess.pgn
from fastapi import APIRouter, HTTPException

from app.schemas.parse import ParseResponseSchema, ParsedMoveSchema
from app.schemas.analysis_request import AnalysisRequestSchema

router = APIRouter(prefix="/parse", tags=["parse"])


@router.post("", response_model=ParseResponseSchema)
def parse_pgn(payload: AnalysisRequestSchema):
    game = chess.pgn.read_game(io.StringIO(payload.pgn))
    if game is None:
        raise HTTPException(status_code=400, detail="Invalid PGN")

    board = game.board()
    moves = []
    move_number = 1

    for move in game.mainline_moves():
        color = "white" if board.turn == chess.WHITE else "black"
        san = board.san(move)
        board.push(move)

        moves.append(
            ParsedMoveSchema(
                move_number=move_number,
                color=color,
                uci=move.uci(),
                san=san,
                fen_after=board.fen(),
            )
        )

        if color == "black":
            move_number += 1

    # Normalize PGN back to string (optional but useful)
    exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
    normalized_pgn = game.accept(exporter)

    return {
        "pgn": normalized_pgn,
        "fen": board.fen(),
        "moves": moves,
    }
