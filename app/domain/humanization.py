# app/domain/humanization.py

import chess
import random

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100,
}

# ============================================================
# PUBLIC ENTRY
# ============================================================
def select_human_like_move(
    board: chess.Board,
    candidates: list[tuple[chess.Move, float]],
    elo: int,
) -> chess.Move:

    # Tunnel vision selection
    spatial = random.random() < 0.7
    conceptual = random.choice(["attack", "defend"])

    visible = apply_spatial_tunnel(board, candidates, elo) if spatial else candidates
    visible = apply_conceptual_tunnel(board, visible, conceptual, elo)

    visible = maybe_ignore_mate_threat(board, visible, elo)

    scored = []
    for move, _ in visible:
        score = priority_score(board, move, elo)
        scored.append((score, move))

    scored.sort(key=lambda x: x[0], reverse=True)

    # Human randomness
    if elo < 1400 and len(scored) > 1:
        return random.choice(scored[:2])[1]

    return scored[0][1]


# ============================================================
# SPATIAL TUNNEL VISION
# ============================================================
def apply_spatial_tunnel(board, candidates, elo):
    focus = pick_focus_region(board)

    filtered = [
        (m, e)
        for m, e in candidates
        if m.to_square in focus
    ]

    if filtered and elo < 1200:
        return filtered

    return candidates


def pick_focus_region(board):
    own_squares = [
        sq for sq, p in board.piece_map().items()
        if p.color == board.turn
    ]

    avg_file = sum(chess.square_file(sq) for sq in own_squares) / len(own_squares)

    if avg_file <= 2:
        return queenside()
    if avg_file >= 5:
        return kingside()
    return center()


def kingside():
    return {sq for sq in chess.SQUARES if chess.square_file(sq) >= 5}


def queenside():
    return {sq for sq in chess.SQUARES if chess.square_file(sq) <= 2}


def center():
    return {chess.D4, chess.E4, chess.D5, chess.E5}


# ============================================================
# CONCEPTUAL TUNNEL VISION
# ============================================================
def apply_conceptual_tunnel(board, candidates, mode, elo):
    if elo > 1600:
        return candidates

    filtered = []
    for move, eval_score in candidates:
        if mode == "attack" and is_attacking_move(board, move):
            filtered.append((move, eval_score))
        elif mode == "defend" and is_defensive_move(board, move):
            filtered.append((move, eval_score))

    return filtered or candidates


# ============================================================
# MATE AWARENESS DECAY
# ============================================================
def maybe_ignore_mate_threat(board, candidates, elo):
    if not opponent_has_mate_in_1(board):
        return candidates

    defend_prob = (
        0.95 if elo >= 2000 else
        0.75 if elo >= 1500 else
        0.4 if elo >= 1000 else
        0.15 if elo >= 600 else
        0.05
    )

    if random.random() > defend_prob:
        return candidates

    safe = [(m, e) for m, e in candidates if prevents_mate(board, m)]
    return safe or candidates


# ============================================================
# PRIORITY SCORING (UPDATED)
# ============================================================
def priority_score(board, move, elo):
    score = 0.0

    # 1️⃣ Threats (highest)
    if creates_threat(board, move):
        score += 4

    # 2️⃣ Defense
    if is_defensive_move(board, move):
        score += defense_weight(elo)

    # 3️⃣ Captures (LOW priority, reversed by ELO)
    if board.is_capture(move):
        score += capture_bias(board, move, elo)

    return score


def capture_bias(board, move, elo):
    captured = board.piece_at(move.to_square)
    attacker = board.piece_at(move.from_square)

    if not captured or not attacker:
        return 0

    diff = PIECE_VALUES[captured.piece_type] - PIECE_VALUES[attacker.piece_type]

    # Lower overall magnitude
    if elo >= 1800:
        return 1 if diff > 0 else -0.5
    if elo >= 1400:
        return 0.3 if diff > 0 else -0.3
    if elo >= 1000:
        return -0.5 * diff
    if elo >= 600:
        return -1.2 * diff

    # 400–600: fully reversed
    return -2.0 * diff


def defense_weight(elo):
    if elo >= 1800:
        return 3
    if elo >= 1400:
        return 2
    if elo >= 1000:
        return 1
    if elo >= 600:
        return 0.3
    return 0


# ============================================================
# HELPERS
# ============================================================
def creates_threat(board, move):
    after = board.copy()
    after.push(move)

    attacker = after.piece_at(move.to_square)
    if not attacker:
        return False

    for sq in after.attacks(move.to_square):
        target = after.piece_at(sq)
        if target and target.color != attacker.color:
            return PIECE_VALUES[target.piece_type] > PIECE_VALUES[attacker.piece_type]

    return False


def is_defensive_move(board, move):
    after = board.copy()
    after.push(move)

    for sq, piece in board.piece_map().items():
        if piece.color != board.turn:
            continue
        if board.is_attacked_by(not board.turn, sq) and not after.is_attacked_by(not board.turn, sq):
            return True

    return False


def is_attacking_move(board, move):
    return board.is_capture(move) or creates_threat(board, move)


def opponent_has_mate_in_1(board):
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return True
        board.pop()
    return False


def prevents_mate(board, move):
    after = board.copy()
    after.push(move)
    return not opponent_has_mate_in_1(after)
