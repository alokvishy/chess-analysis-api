import chess


def is_interesting_move(
    eval_before: float,
    eval_after: float,
    is_capture: bool,
    board_after: chess.Board,
) -> bool:
    """
    Cheap heuristic to decide whether a move deserves deep analysis.
    """

    # Big eval swing
    if abs(eval_after - eval_before) >= 1.0:
        return True

    # Tactical nature
    if is_capture:
        return True

    # Check / threats
    if board_after.is_check():
        return True

    return False
