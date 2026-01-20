from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.infrastructure.stockfish.pool import StockfishEnginePool
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    """

    # ---------- STARTUP ----------
    engine_pool = StockfishEnginePool(
        path=settings.STOCKFISH_PATH,
        size=2,
    )

    app.state.engine_pool = engine_pool

    print("🚀 Application startup (engine pool ready)")

    yield

    # ---------- SHUTDOWN ----------
    print("🛑 Application shutdown (closing engine pool)")
    engine_pool.shutdown()
