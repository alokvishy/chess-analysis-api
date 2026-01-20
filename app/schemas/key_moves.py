from pydantic import BaseModel



class KeyMomentSchema(BaseModel):
    move_number: int
    color: str
    uci: str
    san: str
    reason: str
    eval_before: float
    eval_after: float

key_moments: list[KeyMomentSchema]