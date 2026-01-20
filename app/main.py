from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analysis import router as analysis_router
from app.api.v1.play import router as play_router
from app.api.v1.parse import router as parse_router

from app.infrastructure.stockfish.pool import StockfishEnginePool


# -------------------------------------------------
# App
# -------------------------------------------------

app = FastAPI(
    title="Chess Backend",
    version="1.0.0",
)


# -------------------------------------------------
# CORS (frontend-safe)
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Lifespan: Engine Pool
# -------------------------------------------------

@app.on_event("startup")
def startup() -> None:
    """
    Application startup:
    - create Stockfish engine pool
    - store in app.state
    """
    pool = StockfishEnginePool()
    pool.create()                      # 🔑 CRITICAL
    app.state.engine_pool = pool

    print("🚀 Application startup (engine pool ready)")


@app.on_event("shutdown")
def shutdown() -> None:
    """
    Application shutdown:
    - gracefully stop all engines
    """
    pool: StockfishEnginePool = app.state.engine_pool
    pool.shutdown()

    print("🛑 Application shutdown (engine pool closed)")


# -------------------------------------------------
# Routers
# -------------------------------------------------

app.include_router(analysis_router, prefix="/api/v1")
app.include_router(play_router, prefix="/api/v1")
app.include_router(parse_router, prefix="/api/v1")
