import asyncio, http.client, json, requests
from bs4 import BeautifulSoup

headers = {"User-Agent":"JooDdae Bot"}
MAX_TIMEOUT = 30

async def start_makgora(commands, message, client):
  if len(commands[0]) == 0:
      await message.channel.send("TODO : 설명 추가")
      return

  def valid_id(id):
    URL = "https://www.acmicpc.net/user/" + id
    page = requests.get(URL, headers=headers)
    return page.status_code == 200
  
  def valid_tier(tier):
    if len(tier) == 1:
      return tier[0] in "bsgpdr"
    elif len(tier) == 2:
      return (tier[0] in "bsgpdr" and tier[1] in "12345") or (tier[0] in "1234567890" and tier[1] in "1234567890" and int(tier) <= 30)
    elif len(tier) <= 6:
      if ".." not in tier :
        return False
      tier = tier.split("..")
      if len(tier) == 1 :
        return valid_tier(tier[0])
      else :
        return len(tier) == 2 and valid_tier(tier[0]) and valid_tier(tier[1])
    return False

  if len(commands) != 4 or valid_tier(commands[1]) == False or valid_id(commands[2]) == False or valid_id(commands[3]) == False or commands[2] == commands[3]:
    await message.channel.send("TODO : 어떻게 잘못되었는지 설명 추가")
    await message.channel.send("형식이 잘못되었습니다. '!막고라 [난이도] [아이디1] [아이디2]' 형식으로 입력해주세요.")
    return
  
  tier = commands[1]
  id1 = commands[2]
  id2 = commands[3]
  left_minute = 10
  notification_minute = 2

  msg = await message.channel.send(tier + " 난이도의 문제로 " + id1 + "와 " + id2 + "의 막고라를 진행하는게 맞습니까?")
  await msg.add_reaction("✅")
  await msg.add_reaction("❌")

  def check_reaction(reaction, user):
    return user == message.author and str(reaction.emoji) in ["✅", "❌"]
  try:
    reaction, user = await client.wait_for('reaction_add', timeout=MAX_TIMEOUT, check=check_reaction)
  except asyncio.TimeoutError:
    await msg.clear_reactions()
    await message.channel.send("시간이 초과되었습니다.")
    return
  
  await msg.clear_reactions()
  if str(reaction.emoji) == "❌":
    await message.channel.send("취소되었습니다.")
    return
  conn = http.client.HTTPSConnection("solved.ac")
  conn.request("GET", "/api/v3/search/problem?query=*" + tier + "%20-solved_by%3A" + id1 + "%20-solved_by%3A" + id1 + "&sort=random", headers={ 'Content-Type': "application/json" })

  res = conn.getresponse()
  data = res.read()

  if res.status != 200:
    msg = await message.channel.send("API가 정상적으로 동작하지 않아 취소되었습니다.")
    return
  
  problems = json.loads(data.decode("utf-8"))
  if problems['count'] == 0:
    msg = await message.channel.send("해당 난이도의 문제가 없어 취소되었습니다.")
    return

  problem = problems['items'][0]
  await message.channel.send(id1 + "과 " + id2 + "의 막고라가 시작됩니다.")
  await message.channel.send(problem['titleKo'] + " https://www.acmicpc.net/problem/" + str(problem['problemId']))
  await message.channel.send("문제를 풀고 나서 '!컷'을 입력해주세요. 이 명령어는 누구든 사용할 수 있습니다.")

  def first_ac_submission(user_id, problem_id):
    URL = "https://www.acmicpc.net/status?problem_id=" + str(problem_id) + "&user_id=" + user_id + "&result_id=4"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    if len(soup.select("tbody > tr")) == 0 :
      return -1
    return int(soup.select("tbody > tr")[-1].select("td")[0].text)
  
  left_second = left_minute * 60

  def check_message(message):
    return message.content == "!컷" or message.content == "!취소"

  while True:
    try:
      msg = await client.wait_for('message', timeout=1, check=check_message)
    except asyncio.TimeoutError:
      if left_second == 0 :
        await message.channel.send("제한시간이 초과되었습니다.")
        return
      if left_second % (60 * notification_minute) == 0 or left_second == 60:
        await message.channel.send("남은 시간 " + str(left_second//60) + "분")
      elif left_second == 10 :
        await message.channel.send("남은 시간 10초")
      elif left_second <= 5 :
        await message.channel.send("남은 시간 " + str(left_second) + "초")
      left_second -= 1
    else:
      if msg.content == "!취소" :
        await message.channel.send("취소되었습니다.")
        return
      result1 = first_ac_submission(id1, problem['problemId'])
      result2 = first_ac_submission(id2, problem['problemId'])
      if result1 != -1 or result2 != -1:
        winner = [id2, id1][result2 == -1 or (result1 != -1 and result1 < result2)]
        loser = [id2, id1][id2 == winner]
        await message.channel.send(winner + "가 먼저 문제를 해결했습니다.")

        import members
        await members.change_winlose(message, winner, loser)

        break
      await message.channel.send("둘 다 아직 풀지 않았습니다.")