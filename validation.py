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