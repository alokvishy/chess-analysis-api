import io
from typing import List, Tuple, Optional

import chess
import chess.pgn
import chess.engine

from app.domain.enums import MoveQuality
from app.domain.models import EvaluatedMove
from app.domain.analysis import classify_move
from app.domain.material import material_count, is_piece_hanging
from app.domain.brilliance import BrilliantContext, calculate_brilliant_move
from app.domain.analysis_heuristics import is_interesting_move
from app.domain.opening import is_opening_phase
from app.domain.opening_book import is_book_position, normalize_fen
from app.domain.opening_names import detect_opening, OpeningInfo

from app.infrastructure.stockfish.pool import StockfishEnginePool
from app.core.config import settings


class AnalysisService:
    def __init__(self, engine_pool: StockfishEnginePool):
        self._engine_pool = engine_pool

    def analyze_pgn(
        self,
        pgn_text: str,
        depth: Optional[int] = None,
        player_elo: int = 1200,
    ) -> Tuple[List[EvaluatedMove], Optional[OpeningInfo]]:

        game = chess.pgn.read_game(io.StringIO(pgn_text))
        if game is None:
            raise ValueError("Invalid PGN")

        board = game.board()
        engine = self._engine_pool.acquire()

        try:
            moves: List[EvaluatedMove] = []
            opening_info: Optional[OpeningInfo] = None

            move_number = 1
            prev_eval: Optional[float] = None

            for move in game.mainline_moves():
                color = "white" if board.turn == chess.WHITE else "black"
                board_before = board.copy(stack=False)

                san = board.san(move)
                is_capture = board.is_capture(move)

                # ---------------- OPENING BOOK ----------------
                if (
                    is_opening_phase(
                        move_number,
                        settings.OPENING_BOOK_MAX_FULL_MOVES,
                    )
                    and is_book_position(board_before)
                ):
                    board.push(move)

                    if opening_info is None:
                        detected = detect_opening(board)
                        if detected:
                            opening_info = detected

                    moves.append(
                        EvaluatedMove(
                            move_number=move_number,
                            color=color,
                            uci=move.uci(),
                            san=san,
                            eval_before=prev_eval,
                            eval_after=prev_eval,
                            eval_loss=0.0,
                            quality=MoveQuality.BOOK,
                            is_check=board.is_check(),
                            is_checkmate=board.is_checkmate(),
                            is_capture=is_capture,
                            clock=None,
                        )
                    )

                    if color == "black":
                        move_number += 1
                    continue

                # ---------------- ENGINE EVAL ----------------
                best_move = None

                if prev_eval is None:
                    info = engine.analyze(
                        board,
                        chess.engine.Limit(
                            depth=depth or settings.STOCKFISH_BASE_DEPTH
                        )
                    )

                    score = info["score"].white().score(mate_score=10000)
                    prev_eval = score / 100 if score is not None else 0.0

                    pv = info.get("pv")
                    if pv:
                        best_move = pv[0]


                before_material = material_count(board_before)
                was_hanging = is_piece_hanging(
                    board_before, move.from_square
                )

                board.push(move)

                if opening_info is None:
                    detected = detect_opening(board)
                    if detected:
                        opening_info = detected

                eval_depth = (
                    settings.STOCKFISH_OPENING_DEPTH
                    if is_opening_phase(
                        move_number,
                        settings.OPENING_MAX_FULL_MOVES,
                    )
                    else depth or settings.STOCKFISH_BASE_DEPTH
                )

                eval_after = self._eval_depth(
                    engine,
                    board,
                    eval_depth,
                )

                if is_interesting_move(
                    prev_eval, eval_after, is_capture, board
                ):
                    eval_after = self._eval_time(
                        engine,
                        board,
                        settings.STOCKFISH_DEEP_TIME,
                    )

                eval_loss = (
                    max(0.0, prev_eval - eval_after)
                    if color == "white"
                    else max(0.0, eval_after - prev_eval)
                )

                quality = classify_move(eval_loss)

                after_material = material_count(board)
                material_delta = after_material - before_material
                piece_sacrificed = material_delta < 0 and not is_capture

                reply_eval = self._eval_time(engine, board, 0.05)

                ctx = BrilliantContext(
                    eval_before=int(prev_eval * 100),
                    eval_after=int(eval_after * 100),
                    eval_after_reply=int(reply_eval * 100),
                    material_delta=material_delta,
                    piece_sacrificed=piece_sacrificed,
                    was_piece_hanging_before=was_hanging,
                    was_forced_move=False,
                    alternative_good_moves=2,
                    move_gives_immediate_mate=board.is_checkmate(),
                    move_is_capture=is_capture,
                    player_elo=player_elo,
                )

                if (
                    quality == MoveQuality.BEST
                    and not is_opening_phase(
                        move_number,
                        settings.OPENING_MAX_FULL_MOVES,
                    )
                    and calculate_brilliant_move(ctx)
                ):
                    quality = MoveQuality.BRILLIANT

                moves.append(
                    EvaluatedMove(
                        move_number=move_number,
                        color=color,
                        uci=move.uci(),
                        san=san,
                        eval_before=prev_eval,
                        eval_after=eval_after,
                        eval_loss=eval_loss,
                        quality=quality,
                        is_check=board.is_check(),
                        is_checkmate=board.is_checkmate(),
                        is_capture=is_capture,
                        clock=None,
                                # ✅ NEW
                        best_move_uci=best_move.uci() if best_move else None,
                        best_move_san=(
                            board_before.san(best_move)
                            if best_move else None
                        ),
                    )
                )

                prev_eval = eval_after
                if color == "black":
                    move_number += 1

            return moves, opening_info

        finally:
            self._engine_pool.release(engine)

    # ---------------- ENGINE HELPERS ----------------

    def _eval_depth(self, engine, board, depth: int) -> float:
        info = engine.analyze(board, chess.engine.Limit(depth=depth))
        score = info["score"].white().score(mate_score=10000)
        return score / 100 if score is not None else 0.0

    def _eval_time(self, engine, board, time_s: float) -> float:
        info = engine.analyze(board, chess.engine.Limit(time=time_s))
        score = info["score"].white().score(mate_score=10000)
        return score / 100 if score is not None else 0.0
