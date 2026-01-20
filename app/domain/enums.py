from enum import Enum


class MoveQuality(str, Enum):
    BOOK = "BOOK"          # 👈 ADD
    BRILLIANT = "BRILLIANT"
    BEST = "BEST"
    GOOD = "GOOD"
    INACCURACY = "INACCURACY"
    MISTAKE = "MISTAKE"
    BLUNDER = "BLUNDER"
