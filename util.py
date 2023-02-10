def seconds_to_krtime(seconds: int) -> str:
    hours = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if seconds < 60:
        return f"{secs}초"
    if seconds < 3600:
        return f"{mins}분 {secs}초"
    return f"{hours}시간 {mins}분 {secs}초"

def valid_tier(tier: str) -> bool:
    tier = tier.lower()
    if len(tier) == 1:
        return tier[0] in "bsgpdr"
    elif len(tier) == 2:
        return (tier[0] in "bsgpdr" and tier[1] in "12345") or (tier[0] in "1234567890" and tier[1] in "1234567890" and int(tier) <= 30)
    elif len(tier) <= 6:
        if ".." not in tier:
            return False
        tiers = tier.split("..")
        if len(tiers) == 2:
            if len(tiers[0]) == 0:
                return valid_tier(tiers[1])
            elif len(tiers[1]) == 0:
                return valid_tier(tiers[0])
            else:
                return valid_tier(tiers[0]) and valid_tier(tiers[1])
    return False

def add_delta_color(delta: float) -> str:
    color_delta = f"{delta:+.0f}\x1B[0m"
    if abs(delta) < 0.5:
        return "+ 0"
    if len(color_delta) == 6:
        color_delta = color_delta[0] + " " + color_delta[1:]
    if color_delta[0] == "+" :
        color_delta = "\x1B[34m" + color_delta
    else :
        color_delta = "\x1B[31m" + color_delta
    return color_delta
