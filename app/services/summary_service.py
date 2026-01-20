from app.domain.models import EvaluatedMove
from app.domain.stats import (
    acpl,
    accuracy_percentage,
    count_by_quality,
)
from app.services.elo_service import EloService
from app.domain.enums import MoveQuality


class SummaryService:
    """
    Computes summary statistics from analyzed moves.
    Pure orchestration layer with sanity corrections.
    """

    def __init__(self) -> None:
        self.elo_service = EloService()

    # -------------------------------------------------
    # Helpers
    # -------------------------------------------------

    def _player_move_count(
        self,
        moves: list[EvaluatedMove],
        color: str,
    ) -> int:
        """
        Counts only meaningful moves used for ELO estimation.
        Must match ACPL / accuracy logic exactly.
        """
        return sum(
            1
            for m in moves
            if m.color == color
            and m.quality != MoveQuality.BOOK
        )

    # -------------------------------------------------
    # Public API
    # -------------------------------------------------

    def summarize(self, moves: list[EvaluatedMove]) -> dict:
        # -----------------------------
        # Metrics
        # -----------------------------
        white_acpl = acpl(moves, "white")
        black_acpl = acpl(moves, "black")

        white_acc = accuracy_percentage(moves, "white")
        black_acc = accuracy_percentage(moves, "black")

        white_counts = count_by_quality(moves, "white")
        black_counts = count_by_quality(moves, "black")

        white_move_count = self._player_move_count(moves, "white")
        black_move_count = self._player_move_count(moves, "black")

        # -----------------------------
        # Raw ELO estimation
        # -----------------------------
        white_elo = self.elo_service.estimate(
            acpl=white_acpl,
            accuracy=white_acc,
            blunders=white_counts["blunders"],
            mistakes=white_counts["mistakes"],
            total_moves=white_move_count,
        )

        black_elo = self.elo_service.estimate(
            acpl=black_acpl,
            accuracy=black_acc,
            blunders=black_counts["blunders"],
            mistakes=black_counts["mistakes"],
            total_moves=black_move_count,
        )

        # -----------------------------
        # 🔑 Sanity correction
        # Prevent accuracy inversion
        # -----------------------------
        ACC_DOMINANCE_THRESHOLD = 4.0  # percent
        ELO_SOFTEN_FACTOR = 0.5        # pull, not clamp

        acc_diff = white_acc - black_acc

        if acc_diff >= ACC_DOMINANCE_THRESHOLD:
            # White clearly more accurate → should not be rated lower
            if white_elo["elo"] < black_elo["elo"]:
                avg = int((white_elo["elo"] + black_elo["elo"]) / 2)
                white_elo["elo"] = int(avg + (white_elo["elo"] - avg) * ELO_SOFTEN_FACTOR)
                black_elo["elo"] = int(avg - (avg - black_elo["elo"]) * ELO_SOFTEN_FACTOR)

        elif acc_diff <= -ACC_DOMINANCE_THRESHOLD:
            # Black clearly more accurate → should not be rated lower
            if black_elo["elo"] < white_elo["elo"]:
                avg = int((white_elo["elo"] + black_elo["elo"]) / 2)
                black_elo["elo"] = int(avg + (black_elo["elo"] - avg) * ELO_SOFTEN_FACTOR)
                white_elo["elo"] = int(avg - (avg - white_elo["elo"]) * ELO_SOFTEN_FACTOR)

        # -----------------------------
        # Verdict
        # -----------------------------
        if white_acc > black_acc:
            verdict = "White played better"
        elif black_acc > white_acc:
            verdict = "Black played better"
        else:
            verdict = "Game was evenly played"

        # -----------------------------
        # Response
        # -----------------------------
        return {
            "white": {
                "acpl": white_acpl,
                "accuracy": white_acc,
                **white_counts,
                "estimated_elo": white_elo,
            },
            "black": {
                "acpl": black_acpl,
                "accuracy": black_acc,
                **black_counts,
                "estimated_elo": black_elo,
            },
            "verdict": verdict,
        }
