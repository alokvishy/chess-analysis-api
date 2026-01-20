# app/services/elo_service.py

import math


class EloService:
    """
    Pure analysis-based strength estimator.
    NOT real Elo. NOT contextual. NOT result-based.
    """

    def estimate(
        self,
        acpl: float,
        accuracy: float,
        blunders: int,
        mistakes: int,
        total_moves: int,
    ) -> dict:
        if total_moves <= 0:
            return {"elo": 400, "confidence": 0.0}

        # -----------------------------
        # Normalize metrics
        # -----------------------------

        # ACPL dominates (log decay)
        acpl_score = math.exp(-acpl / 45.0)

        # Accuracy (linear)
        accuracy_score = accuracy / 100.0

        # Error penalty (non-linear)
        error_penalty = math.exp(
            -(2.0 * blunders + 0.8 * mistakes) / total_moves
        )

        # -----------------------------
        # Performance index (0–1)
        # -----------------------------
        performance_index = (
            0.55 * acpl_score +
            0.30 * accuracy_score +
            0.15 * error_penalty
        )

        # -----------------------------
        # Logistic rating mapping
        # -----------------------------
        sigmoid = 1 / (1 + math.exp(-6 * (performance_index - 0.5)))
        estimated_elo = int(round(400 + 2600 * sigmoid))

        # -----------------------------
        # Confidence
        # -----------------------------
        confidence = round(min(1.0, total_moves / 40), 2)

        return {
            "elo": estimated_elo,
            "confidence": confidence,
        }
