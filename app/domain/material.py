import chess

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
}


def material_count(board: chess.Board) -> int:
    """
    Positive = White ahead
    Negative = Black ahead
    """
    total = 0
    for piece_type, value in PIECE_VALUES.items():
        total += len(board.pieces(piece_type, chess.WHITE)) * value
        total -= len(board.pieces(piece_type, chess.BLACK)) * value
    return total


def is_piece_hanging(board: chess.Board, square: chess.Square) -> bool:
    """
    A piece is hanging if it is attacked and not sufficiently defended.
    """
    attackers = board.attackers(not board.turn, square)
    if not attackers:
        return False

    defenders = board.attackers(board.turn, square)
    if not defenders:
        return True

    return len(attackers) > len(defenders)
