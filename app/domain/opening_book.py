import chess

# VERY SMALL, FAST, EXTENDABLE
# These are POSITION FENs, not moves
OPENING_FENS = {
   
    # Ruy Lopez after 3.Bb5
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq",

    # After 3...a6
    "r1bqkbnr/1ppp1ppp/p1n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R w KQkq",

    # Initial
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq",

    # After 1.e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq",

    # After 1.d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq",

    # After 1.e4 e5
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq",

    # After 1.e4 c5
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq",

    # Add more over time
}


def normalize_fen(board: chess.Board) -> str:
    """
    Remove move counters from FEN.
    """
    fen = board.fen()
    return " ".join(fen.split()[:3])


def is_book_position(board: chess.Board) -> bool:
    return normalize_fen(board) in OPENING_FENS
