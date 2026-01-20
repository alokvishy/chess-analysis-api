from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # -------------------------------------------------
    # Stockfish binary & pool
    # -------------------------------------------------
    STOCKFISH_PATH: str = Field(
        default=r"C:\stockfish\stockfish\stockfish-windows-x86-64-avx2.exe",
        description="Absolute path to Stockfish binary",
    )

    STOCKFISH_POOL_SIZE: int = Field(
        default=2,
        description="Number of Stockfish engines in the pool",
    )

    # -------------------------------------------------
    # Engine resources
    # -------------------------------------------------
    STOCKFISH_THREADS: int = Field(default=1)
    STOCKFISH_HASH_MB: int = Field(default=256)

    # -------------------------------------------------
    # FAST + DEEP ANALYSIS STRATEGY
    # -------------------------------------------------
    STOCKFISH_BASE_DEPTH: int = Field(
        default=14,
        description="Fast baseline depth (all moves)",
    )

    STOCKFISH_DEEP_TIME: float = Field(
        default=0.15,
        description="Time (seconds) for selective deep analysis",
    )

    STOCKFISH_REPLY_TIME: float = Field(
        default=0.10,
        description="Time (seconds) for opponent best reply eval",
    )

    # -------------------------------------------------
    # Play / Elo limits
    # -------------------------------------------------
    STOCKFISH_MIN_ELO: int = 400
    STOCKFISH_MAX_ELO: int = 3000
    STOCKFISH_MIN_ELO_NATIVE: int = 1320


    OPENING_MAX_FULL_MOVES: int = Field(
        default=10,
        description="Number of full moves considered opening phase",
    )

    STOCKFISH_OPENING_DEPTH: int = Field(
        default=8,
        description="Very fast depth for opening moves",
    )

        # -------------------------------------------------
    # Opening book
    # -------------------------------------------------
    OPENING_BOOK_MAX_FULL_MOVES: int = Field(
        default=10,
        description="Max full moves to consider opening book",
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
