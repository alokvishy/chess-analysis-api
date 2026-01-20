from typing import List

from app.domain.models import EvaluatedMove
from app.domain.key_moves import detect_key_moments, KeyMoment


class KeyMoveService:
    """
    Computes key moments from evaluated moves.
    """

    def find_key_moments(
        self,
        moves: List[EvaluatedMove],
        max_items: int = 5,
    ) -> List[KeyMoment]:
        moments = detect_key_moments(moves)

        # Keep most important ones first
        return moments[:max_items]
