import chess
import chess.engine
from typing import Optional, List, Tuple

from app.infrastructure.stockfish.pool import StockfishEnginePool
from app.core.config import settings
from app.domain.humanization import select_human_like_move


class PlayService:
    """
    Handles play-vs-engine logic.
    Stateless, request-scoped configuration.
    """

    def __init__(self, engine_pool: StockfishEnginePool):
        self._engine_pool = engine_pool

    # -------------------------------------------------
    # Depth scaling by ELO
    # -------------------------------------------------

    def _depth_for_elo(self, elo: Optional[int]) -> int:
        if elo is None:
            return settings.STOCKFISH_DEPTH

        if elo < 800:
            return 4
        if elo < 1100:
            return 6
        if elo < 1500:
            return 8
        if elo < 1800:
            return 10
        return settings.STOCKFISH_DEPTH

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _normalize_multipv(self, result) -> List[dict]:
        """
        Normalize python-chess multipv output to a list.
        """
        if isinstance(result, list):
            return result
        if isinstance(result, dict):
            return [result]
        return []

    def _eval_cp_from_side_to_move(
        self,
        score: chess.engine.PovScore,
        board: chess.Board,
    ) -> Optional[int]:
        """
        Always evaluate from side to move.
        """
        return score.pov(board.turn).score(mate_score=10000)

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def play_move(
        self,
        fen: str,
        depth: Optional[int] = None,
        elo: Optional[int] = None,
    ) -> dict:
        board = chess.Board(fen)

        if board.is_game_over():
            raise ValueError("Game is already over")

        engine = self._engine_pool.acquire()

        try:
            effective_depth = depth or self._depth_for_elo(elo)
            limit = chess.engine.Limit(depth=effective_depth)

            # -----------------------------------------
            # Engine strength config
            # -----------------------------------------
            if elo is not None and elo >= settings.STOCKFISH_MIN_ELO_NATIVE:
                engine.set_elo(elo)
                effective_elo = elo
                use_humanization = False
            else:
                engine.set_elo(None)
                effective_elo = elo
                use_humanization = elo is not None

            # -----------------------------------------
            # Decide move
            # -----------------------------------------
            if use_humanization:
                raw = engine.analyze(board, limit, multipv=5)
                infos = self._normalize_multipv(raw)

                candidates: List[Tuple[chess.Move, int]] = []

                for info in infos:
                    pv = info.get("pv")
                    score = info.get("score")
                    if not pv or score is None:
                        continue

                    cp = self._eval_cp_from_side_to_move(score, board)
                    if cp is None:
                        continue

                    candidates.append((pv[0], cp))

                if candidates:
                    move = select_human_like_move(board, candidates, elo)
                else:
                    move = engine.play(board, limit).move
            else:
                move = engine.play(board, limit).move

            if move is None:
                raise RuntimeError("Engine did not return a move")

            # -----------------------------------------
            # Apply move
            # -----------------------------------------
            san = board.san(move)
            board.push(move)

            # -----------------------------------------
            # Evaluate resulting position
            # -----------------------------------------
            info = engine.analyze(
                board,
                chess.engine.Limit(depth=effective_depth),
            )

            cp = self._eval_cp_from_side_to_move(info["score"], board)
            eval_pawns = cp / 100 if cp is not None else 0.0

            return {
                "engine_move_uci": move.uci(),
                "engine_move_san": san,
                "fen_after": board.fen(),
                "eval": eval_pawns,
                "is_check": board.is_check(),
                "is_checkmate": board.is_checkmate(),
                "engine_effective_elo": effective_elo,
            }

        finally:
            self._engine_pool.release(engine)
