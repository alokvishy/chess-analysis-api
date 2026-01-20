from dataclasses import dataclass


@dataclass(frozen=True)
class BrilliantContext:
    eval_before: int
    eval_after: int
    eval_after_reply: int

    material_delta: int           # negative means sacrifice
    piece_sacrificed: bool

    was_piece_hanging_before: bool
    was_forced_move: bool
    alternative_good_moves: int

    move_gives_immediate_mate: bool
    move_is_capture: bool

    player_elo: int


def calculate_brilliant_move(ctx: BrilliantContext) -> bool:
    """
    Strict brilliance classifier.
    Returns True only if the move qualifies as BRILLIANT.
    """

    # --- SACRIFICE REQUIREMENT ---
    if not ctx.piece_sacrificed:
        return False

    # Pawn sacs excluded, exchange or piece sac only
    if ctx.material_delta > -2:
        return False

    # --- VOLUNTARINESS ---
    if ctx.move_is_capture:
        return False

    if ctx.was_piece_hanging_before:
        return False

    if ctx.was_forced_move:
        return False

    # --- GAME CONTEXT ---
    if ctx.eval_before < -200:
        return False

    if ctx.move_gives_immediate_mate:
        return False

    # --- ENGINE VALIDATION ---
    eval_drop = ctx.eval_after_reply - ctx.eval_before

    # Allow temporary initiative loss
    if eval_drop < -50:
        return False

    # --- NON-OBVIOUSNESS ---
    if ctx.alternative_good_moves >= 3:
        return False

    # --- ELO-RELATIVE STRICTNESS ---
    if ctx.player_elo < 1000:
        allowed_drop = -30
    elif ctx.player_elo < 1400:
        allowed_drop = -20
    elif ctx.player_elo < 1800:
        allowed_drop = -10
    else:
        allowed_drop = 0

    if eval_drop < allowed_drop:
        return False

    return True
