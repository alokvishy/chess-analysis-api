from app.domain.enums import MoveQuality


def classify_move(eval_loss: float) -> MoveQuality:
    """
    Classify a move based on evaluation loss (from the player's perspective).

    eval_loss:
        0.0   -> perfect
        0.2   -> small loss
        1.0   -> inaccuracy
        3.0   -> mistake
        6.0+  -> blunder
    """

    if eval_loss <= 0.1:
        return MoveQuality.BEST
    if eval_loss <= 0.5:
        return MoveQuality.GOOD
    if eval_loss <= 1.5:
        return MoveQuality.INACCURACY
    if eval_loss <= 3.0:
        return MoveQuality.MISTAKE
    return MoveQuality.BLUNDER
