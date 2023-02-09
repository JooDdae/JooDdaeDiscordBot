async def valid_tier(tier):
  tier = tier.lower()
  if len(tier) == 1:
    return tier[0] in "bsgpdr"
  elif len(tier) == 2:
    return (tier[0] in "bsgpdr" and tier[1] in "12345") or (tier[0] in "1234567890" and tier[1] in "1234567890" and int(tier) <= 30)
  elif len(tier) <= 6:
    if ".." not in tier :
      return False
    tier = tier.split("..")
    if len(tier) == 2 :
      if len(tier[0]) == 0 :
        return valid_tier(tier[1])
      elif len(tier[1]) == 0 :
        return valid_tier(tier[0])
      else :
        return valid_tier(tier[0]) and valid_tier(tier[1])
  return False

async def valid_baekjoon_id(id):
  import members
  return id in members.baekjoon_id_list

async def valid_register_url(url, id, print_string):
  if url[:37] != "https://www.acmicpc.net/source/share/" and url[:14] != "http://boj.kr/":
    url = "https://www.acmicpc.net/source/share/" + url
  
  import boj_crawling
  submit_id, input_string = await boj_crawling.submit_id_code(url)
  if submit_id == "-1" :
    return "링크가 잘못되었습니다. 다시 입력해주세요."

  if submit_id != id:
    return "아이디가 일치하지 않습니다. 다시 입력해주세요."
  if input_string.strip() != print_string:
    return "제출한 코드가 잘못되었습니다. 다시 입력해주세요."
  return "pass"