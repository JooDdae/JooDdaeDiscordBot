import asyncio, http.client, json, requests
from bs4 import BeautifulSoup

headers = {"User-Agent":"JooDdae Bot"}
MAX_TIMEOUT = 30

async def request_makgora(commands, message, client):
  if len(commands[0]) == 0:
      await message.channel.send("TODO : 설명 추가")
      return

  import members, validation

  id1 = await members.get_baekjoon_id(message.author.id)
  if len(id1) == 0 :
    await message.channel.send("등록되지 않은 멤버입니다. '!등록 [백준 아이디]' 형식으로 등록해주세요.")
    return

  if len(commands) != 3 or await validation.valid_tier(commands[1]) == False or await validation.valid_baekjoon_id(commands[2]) == False or id1 == commands[2]:
    await message.channel.send("TODO : 어떻게 잘못되었는지 설명 추가")
    await message.channel.send("형식이 잘못되었습니다. '!막고라신청 [난이도] [상대방 아이디]' 형식으로 입력해주세요.")
    return

  tier = commands[1]
  id2 = commands[2]
  left_minute = 10
  notification_minute = 1
  
  if await members.is_active(id1) == True or await members.is_active(id2) == True:
    await message.channel.send("이미 막고라 중인 멤버가 있습니다.")
    return
  
  msg = await message.channel.send("<@{id1}>님, {tier} 난이도의 문제로 {id2}에게 막고라를 신청하는게 맞습니까?".format(id1 = message.author.id, tier = tier, id2 = id2))
  await msg.add_reaction("✅")
  await msg.add_reaction("❌")
  def check_reaction(reaction, user):
    return user == message.author and str(reaction.emoji) in ["✅", "❌"]
  try:
    reaction, user = await client.wait_for('reaction_add', timeout=MAX_TIMEOUT, check=check_reaction)
  except asyncio.TimeoutError:
    await msg.clear_reactions()
    await msg.edit(content = "시간이 초과되었습니다.")
    return
  await msg.clear_reactions()
  if str(reaction.emoji) == "❌":
    await msg.edit(content = "취소되었습니다.")
    return

  discord_id2 = await members.get_discord_id(id2)
  msg = await message.channel.send("<@{id2}>({baekjoonid2})님, <@{id1}>({baekjoonid1})님의 막고라 신청을 수락하겠습니까?".format(id1 = message.author.id, id2 = discord_id2, baekjoonid1 = id1, baekjoonid2 = id2))
  await msg.add_reaction("✅")
  await msg.add_reaction("❌")
  def check_reaction(reaction, user):
    return str(user.id) == discord_id2 and str(reaction.emoji) in ["✅", "❌"]
  try:
    reaction, user = await client.wait_for('reaction_add', timeout=MAX_TIMEOUT, check=check_reaction)
  except asyncio.TimeoutError:
    await msg.clear_reactions()
    await msg.edit(content = "시간이 초과되었습니다.")
    return
  await msg.clear_reactions()
  if str(reaction.emoji) == "❌":
    await msg.edit(content = "거절했습니다.")
    return

  import members
  await members.active_list_add(id1, id2)
  await start_makgora(commands, message, client, tier, id1, id2, left_minute, notification_minute, str(message.author.id), discord_id2)
  await members.active_list_del(id1, id2)


async def start_makgora(commands, message, client, tier, id1, id2, left_minute, notification_minute, discord_id1, discord_id2):
  conn = http.client.HTTPSConnection("solved.ac")
  conn.request("GET", "/api/v3/search/problem?query=*" + tier + "%20-solved_by%3A" + id1 + "%20-solved_by%3A" + id2 + "&sort=random", headers={ 'Content-Type': "application/json" })

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
  await message.channel.send("문제를 풀고 나서 '!컷'을 입력해주세요. 이 명령어는 막고라를 진행중인 두 사람만 사용할 수 있습니다.")


  def first_ac_submission(user_id, problem_id):
    URL = "https://www.acmicpc.net/status?problem_id=" + str(problem_id) + "&user_id=" + user_id + "&result_id=4"
    page = requests.get(URL, headers=headers)
    soup = BeautifulSoup(page.content, "lxml")
    if len(soup.select("tbody > tr")) == 0 :
      return -1
    return int(soup.select("tbody > tr")[-1].select("td")[0].text)
  
  left_second = left_minute * 60

  def check_message(message):
    return (message.content == "!컷" or message.content == "!취소") and (str(message.author.id) == discord_id1 or str(message.author.id) == discord_id2)

  msg_time = await message.channel.send("남은 시간 " + str(left_minute) + "분")

  async def check_result():
    result1 = first_ac_submission(id1, problem['problemId'])
    result2 = first_ac_submission(id2, problem['problemId'])
    if result1 == -1 and result2 == -1:
      return False
    winner = [id2, id1][result2 == -1 or (result1 != -1 and result1 < result2)]
    loser = [id2, id1][id2 == winner]
    await message.channel.send(winner + "가 먼저 문제를 해결했습니다.")
    import members
    await members.change_winlose(message, winner, loser)
    return True

  while True:
    try:
      msg = await client.wait_for('message', timeout=1, check=check_message)
    except asyncio.TimeoutError:
      if left_second == 0 :
        await msg_time.edit(content = "종료")
        if not await check_result():
          await message.channel.send("제한시간이 초과되었습니다.")
        return
      if left_second % (60 * notification_minute) == 0 or left_second == 60:
        await msg_time.edit(content = "남은 시간 " + str(left_second//60) + "분")
      elif left_second == 10 :
        await msg_time.edit(content = "남은 시간 10초")
      elif left_second <= 5 :
        await msg_time.edit(content = "남은 시간 " + str(left_second) + "초")
      left_second -= 1
    else:
      if msg.content == "!취소" :
        await msg_time.edit(content = "취소되었습니다.")
        return
      if await check_result() :
        return
      await message.channel.send("둘 다 아직 풀지 않았습니다.")