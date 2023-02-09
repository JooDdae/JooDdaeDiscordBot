async def second_to_krtime(second):
  if second < 60:
    return f"{second}초"
  elif second < 3600:
    minute = second // 60
    second = second % 60
    return f"{minute}분 {second}초"
  hour = second // 3600
  minute = (second % 3600) // 60
  second = second % 60
  return f"{hour}시간 {minute}분 {second}초"

async def calculate_delta(r1, r2, result):
  if result == "win":
    result = 1
  elif result == "lose":
    result = 0
  elif result == "tie":
    result = 0.5
  delta = 32 * (result - 1 / (1 + 10 ** ((r2 - r1) / 400)))
  return int(delta)