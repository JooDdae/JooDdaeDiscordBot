def elo_delta(rating_a: float, rating_b: float, result: str) -> float:
    weight = 0.5
    if result == "win":
        weight = 1
    elif result == "lose":
        weight = 0
    delta = 32 * (weight - 1 / (1 + 10 ** ((rating_b - rating_a) / 400)))
    return delta
