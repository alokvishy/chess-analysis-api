import chess
import random


def is_hanging_piece(board: chess.Board, move: chess.Move) -> bool:
    board.push(move)
    try:
        piece = board.piece_at(move.to_square)
        if piece is None:
            return False
        attackers = board.attackers(not piece.color, move.to_square)
        defenders = board.attackers(piece.color, move.to_square)
        return len(attackers) > len(defenders)
    finally:
        board.pop()


def is_greedy_capture(board: chess.Board, move: chess.Move) -> bool:
    return board.is_capture(move) and board.piece_at(move.from_square).piece_type != chess.PAWN


def misses_simple_fork(board: chess.Board, move: chess.Move) -> bool:
    # crude but effective: knight forks missed
    board.push(move)
    try:
        for sq in board.pieces(chess.KNIGHT, not board.turn):
            attacks = board.attacks(sq)
            high_value = 0
            for a in attacks:
                p = board.piece_at(a)
                if p and p.color == board.turn and p.piece_type in (chess.QUEEN, chess.ROOK):
                    high_value += 1
            if high_value >= 2:
                return True
        return False
    finally:
        board.pop()


def thematic_blunder_filter(
    board: chess.Board,
    moves: list[chess.Move],
    elo: int,
) -> chess.Move | None:
    """
    Try to select a move that matches common low-ELO blunder themes.
    Returns None if no thematic blunder fits.
    """

    themes = []

    if elo <= 800:
        themes.append(is_hanging_piece)

    if elo <= 1000:
        themes.append(is_greedy_capture)

    if elo <= 1200:
        themes.append(misses_simple_fork)

    random.shuffle(themes)

    for theme in themes:
        themed_moves = [m for m in moves if theme(board, m)]
        if themed_moves:
            return random.choice(themed_moves)

    return None
