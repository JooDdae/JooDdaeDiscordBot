import asyncio

# discord_id, baekjoon_id, rating, win, lose
member_list = []
with open("member_list.txt", "r") as f:
  for line in f:
    member_list.append(line.strip().split())

baekjoon_id_list = []
for member in member_list:
  baekjoon_id_list.append(member[1])



makgoraing_list = set()
async def is_makgoraing(id):
  if id in makgoraing_list:
    return True
  return False

async def makgoraing_list_add(id1, id2):
  makgoraing_list.add(id1)
  makgoraing_list.add(id2)

async def makgoraing_list_del(id1, id2):
  makgoraing_list.remove(id1)
  makgoraing_list.remove(id2)

async def update_baekjoon_id_list():
  for member in member_list:
    if member[1] not in baekjoon_id_list:
      baekjoon_id_list.append(member[1])

async def print_member(commands, message):
  if len(commands) == 1:
    msg = "멤버 목록입니다. 멤버의 정보를 보려면 '!멤버 [멤버 이름]'을 입력해주세요.\n"
    for member in member_list:
      msg += member[1] + " "
    await message.channel.send(msg)
  elif len(commands) == 2:
    for member in member_list:
      if member[1] == commands[1]:
        msg = "백준 아이디: " + member[1] + "\n"
        msg += "레이팅: " + member[2] + "\n"
        msg += "승: " + member[3] + "\n"
        msg += "패: " + member[4] + "\n"
        await message.channel.send(msg)
        return
    await message.channel.send("해당 멤버가 존재하지 않습니다.")

async def update_member_list():
  with open("member_list.txt", "w") as f:
    for member in member_list:
      f.write(" ".join(member) + "\n")
  await update_baekjoon_id_list()

async def change_winlose(message, winner, loser) :
  win = baekjoon_id_list.index(winner)
  lose = baekjoon_id_list.index(loser)

  if win == -1 or lose == -1:
    await message.channel.send("해당 멤버가 존재하지 않습니다.")
    return

  r1 = int(member_list[win][2])
  r2 = int(member_list[lose][2])
  d = int(32 * (1 - 1 / (1 + 10 ** ((r2 - r1) / 400))))

  member_list[win][2] = str(r1 + d)
  member_list[lose][2] = str(r2 - d)

  member_list[win][3] = str(int(member_list[win][3]) + 1)
  member_list[lose][4] = str(int(member_list[lose][4]) + 1)

  await update_member_list()

  await message.channel.send("결과가 반영되었습니다.")
  await message.channel.send("승자 : {winner} ({r1} :arrow_right: {r1_new} (+{delta}))".format(winner = winner, r1 = r1, r1_new = r1 + d, delta = d))
  await message.channel.send("패자 : {loser} ({r2} :arrow_right: {r2_new} ({delta}))".format(loser = loser, r2 = r2, r2_new = r2 - d, delta = -d))

async def register_member(commands, message, client):
  if len(commands) != 2:
    await message.channel.send("명령어가 잘못되었습니다.")
    return

  if commands[1] in baekjoon_id_list:
    await message.channel.send("이미 존재하는 아이디입니다.")
    return
  
  for member in member_list:
    if member[0] == str(message.author.id):
      await message.channel.send("이미 {id}로 등록된 멤버입니다.".format(id = member[1]))
      return
  def valid_id(id):
    import requests
    URL = "https://www.acmicpc.net/user/" + id
    page = requests.get(URL, headers={"User-Agent":"JooDdae Bot"})
    return page.status_code == 200
  
  if not valid_id(commands[1]):
    await message.channel.send("해당 백준 아이디가 존재하지 않습니다.")
    return

  import random
  print_string = "사랑해요 주때봇 "
  for i in range(50):
    print_string += str(random.randint(0, 9))
  
  # problem_number = 1008
  msg1 = await message.channel.send(print_string)
  msg2 = await message.channel.send("위 문구를 아무 문제에 제출한 후, 제출한 코드를 공유한 주소를 입력해주세요.")

  left_time = 300

  while left_time > 0:
    def check_same_author(msg):
      return message.author == msg.author
    try:
      msg = await client.wait_for('message', timeout=1, check=check_same_author)
    except asyncio.TimeoutError:
      left_time -= 1
      if left_time == 0 :
        await msg1.delete()
        await msg2.edit(content = "시간이 초과되었습니다.")
        return
      await msg2.edit(content = "위 문구를 아무 문제에 제출한 후, 제출한 코드를 공유한 주소를 입력해주세요. ({left_time}초 남음)".format(left_time = left_time))
      continue

    if msg.content == "!취소":
      await msg1.delete()
      await msg2.edit(content = "취소되었습니다.")
      return

    URL = "https://www.acmicpc.net/source/share/" + msg.content
    if msg.content[:37] == "https://www.acmicpc.net/source/share/" or msg.content[:14] == "http://boj.kr/":
      URL = msg.content

    import requests
    page = requests.get(URL, headers={"User-Agent":"JooDdae Bot"})

    if page.status_code != 200:
      await message.channel.send("링크가 잘못되었습니다. 다시 입력해주세요.")
      continue

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.content, 'html.parser')

    input_string = soup.select("div.sample-source > div.form-group > div.col-md-12 > textarea")[0].text
    problem_info = soup.select("div.breadcrumbs > div.container")[0].text.split()

    # if problem_info[0] != str(problem_number) + "번":
    #   await message.channel.send("제출한 문제가 잘못되었습니다.")
    #   return

    if problem_info[-1] != commands[1]:
      await message.channel.send("아이디가 일치하지 않습니다. 다시 입력해주세요.")
      continue

    if input_string.strip() != print_string:
      await message.channel.send("제출한 코드가 잘못되었습니다. 다시 입력해주세요.")
      continue

    member_list.append([str(message.author.id), commands[1], "1000", "0", "0"])
    await update_member_list()
    await message.channel.send("{mention}님이 {id}로 등록되었습니다.".format(mention=message.author.mention, id=commands[1]))
    await print_member(["!멤버", commands[1]], message)
    return

async def valid_baekjoon_id(id):
  return id in baekjoon_id_list

async def get_baekjoon_id(id):
  for member in member_list:
    if member[0] == str(id):
      return member[1]
  return ""

async def get_discord_id(id):
  for member in member_list:
    if member[1] == id:
      return member[0]
  return ""