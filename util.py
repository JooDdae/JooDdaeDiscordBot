def seconds_to_krtime(seconds: int) -> str:
    hours = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if seconds < 60:
        return f"{secs}초"
    if seconds < 3600:
        return f"{mins}분 {secs}초"
    return f"{hours}시간 {mins}분 {secs}초"
