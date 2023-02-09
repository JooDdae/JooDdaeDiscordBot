import asyncio

# discord_id, baekjoon_id, rating, win, lose
member_list = []
with open("member_list.txt", "r") as f:
  for line in f:
    member_list.append(line.strip().split())

baekjoon_id_list = []
for member in member_list:
  baekjoon_id_list.append(member[1])


active_list = set()
async def is_active(id):
  return id in active_list

async def active_list_add(id1, id2):
  active_list.add(id1)
  active_list.add(id2)

async def active_list_del(id1, id2):
  active_list.remove(id1)
  active_list.remove(id2)

async def update_baekjoon_id_list():
  for member in member_list:
    if member[1] not in baekjoon_id_list:
      baekjoon_id_list.append(member[1])

async def get_baekjoon_id(discord_id):
  for member in member_list:
    if member[0] == str(discord_id):
      return member[1]
  return ""

async def get_discord_id(baekjoon_id):
  for member in member_list:
    if member[1] == baekjoon_id:
      return member[0]
  return ""

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
  await message.channel.send(f"승자 : <@{await get_discord_id(winner)}>({winner}) ({r1} :arrow_right: {r1+d} (+{d}))")
  await message.channel.send(f"패자 : <@{await get_discord_id(loser)}>({loser}) ({r2} :arrow_right: {r2-d} (-{d}))")

async def register_member(commands, message, client):
  if len(commands) != 2:
    await message.channel.send("명령어가 잘못되었습니다.")
    return

  if commands[1] in baekjoon_id_list:
    await message.channel.send("이미 존재하는 아이디입니다.")
    return
  
  for member in member_list:
    if member[0] == str(message.author.id):
      await message.channel.send(f"이미 {member[1]}로 등록된 멤버입니다.")
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
      await msg2.edit(content = f"위 문구를 아무 문제에 제출한 후, 제출한 코드를 공유한 주소를 입력해주세요. ({left_time}초 남음)")
      continue

    if msg.content == "!취소":
      await msg1.delete()
      await msg2.edit(content = "취소되었습니다.")
      return

    import validation
    alert = await validation.valid_register_url(msg.content, commands[1], print_string)

    if alert != "pass" :
      await message.channel.send(alert)
      continue
    
    member_list.append([str(message.author.id), commands[1], "1000", "0", "0"])
    await update_member_list()
    await message.channel.send(f"{message.author.mention}님이 {commands[1]}로 등록되었습니다.")
    return