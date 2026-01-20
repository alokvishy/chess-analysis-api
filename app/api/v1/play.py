from fastapi import APIRouter, HTTPException, Request

from app.schemas.play import PlayRequestSchema, PlayResponseSchema
from app.services.play_service import PlayService

router = APIRouter(prefix="/play", tags=["play"])


@router.post("/move", response_model=PlayResponseSchema)
def play_engine_move(
    request: Request,
    payload: PlayRequestSchema,
):
    engine_pool = request.app.state.engine_pool
    service = PlayService(engine_pool)

    try:
        result = service.play_move(
            fen=payload.fen,
            depth=payload.depth,
            elo=payload.elo,
        )
        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {e}",
        )
