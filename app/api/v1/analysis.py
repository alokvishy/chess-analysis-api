from fastapi import APIRouter, HTTPException, Request

from app.schemas.analysis import (
    AnalysisResponseSchema,
    MoveAnalysisSchema,
    OpeningSchema,
)
from app.schemas.analysis_request import AnalysisRequestSchema
from app.services.analysis_service import AnalysisService
from app.services.summary_service import SummaryService
from app.services.key_move_service import KeyMoveService
from app.schemas.key_moves import KeyMomentSchema


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("", response_model=AnalysisResponseSchema)
def analyze_game(request: Request, payload: AnalysisRequestSchema):
    engine_pool = request.app.state.engine_pool
    analysis_service = AnalysisService(engine_pool)
    summary_service = SummaryService()
    key_move_service = KeyMoveService()

    try:
        # 🔑 IMPORTANT: unpack opening info
        moves, opening = analysis_service.analyze_pgn(
            payload.pgn,
            depth=payload.depth,
            player_elo=payload.player_elo,
        )

        summary = summary_service.summarize(moves)
        key_moments = key_move_service.find_key_moments(moves)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return AnalysisResponseSchema(
        opening=(
            OpeningSchema(
                eco=opening.eco,
                name=opening.name,
            )
            if opening
            else None
        ),
        moves=[
            MoveAnalysisSchema(
                move_number=m.move_number,
                color=m.color,
                uci=m.uci,
                san=m.san,
                eval_before=m.eval_before,
                eval_after=m.eval_after,
                eval_loss=m.eval_loss,
                quality=m.quality.value,
                is_check=m.is_check,
                is_checkmate=m.is_checkmate,
                is_capture=m.is_capture,
                clock=m.clock,
                best_move_uci=m.best_move_uci,
                best_move_san=m.best_move_san,
                
            )
            for m in moves
        ],
        summary=summary,
        key_moments=[
            KeyMomentSchema(
                move_number=k.move_number,
                color=k.color,
                uci=k.uci,
                san=k.san,
                reason=k.reason,
                eval_before=k.eval_before,
                eval_after=k.eval_after,
            )
            for k in key_moments
        ],

    )
