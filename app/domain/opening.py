def is_opening_phase(move_number: int, max_opening_moves: int) -> bool:
    """
    Returns True if the game is still in the opening phase.
    move_number is FULL move number (1, 2, 3...)
    """
    return move_number <= max_opening_moves
