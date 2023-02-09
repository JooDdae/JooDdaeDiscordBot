import asyncio

active_list = set()
async def is_active(id):
  return id in active_list

async def active_list_add(id_list):
  for id in id_list:
    active_list.add(id)

async def active_list_del(id_list):
  for id in id_list:
    active_list.remove(id)



async def get_baekjoon_id(discord_id):
  import fileio
  member_list = await fileio.get_member_list()

  for member in member_list:
    if member[0] == str(discord_id):
      return member[1]
  return ""

async def get_discord_id(baekjoon_id):
  import fileio
  member_list = await fileio.get_member_list()
  
  for member in member_list:
    if member[1] == baekjoon_id:
      return member[0]
  return ""



rating = {}
win = {}
lose = {}
tie = {}

async def init(baekjoon_id):
  rating[baekjoon_id] = 1000
  win[baekjoon_id] = 0
  tie[baekjoon_id] = 0
  lose[baekjoon_id] = 0

async def get_rating(baekjoon_id):
  if baekjoon_id not in rating:
    await init(baekjoon_id)
  return rating[baekjoon_id]

async def change_rating(baekjoon_id, delta):
  if baekjoon_id not in rating:
    await init(baekjoon_id)
  rating[baekjoon_id] += delta


async def get_win(baekjoon_id):
  if baekjoon_id not in win:
    await init(baekjoon_id)
  return win[baekjoon_id]

async def change_win(baekjoon_id, delta):
  if baekjoon_id not in win:
    await init(baekjoon_id)
  win[baekjoon_id] += delta


async def get_tie(baekjoon_id):
  if baekjoon_id not in tie:
    await init(baekjoon_id)
  return tie[baekjoon_id]

async def change_tie(baekjoon_id, delta):
  if baekjoon_id not in tie:
    await init(baekjoon_id)
  tie[baekjoon_id] += delta


async def get_lose(baekjoon_id):
  if baekjoon_id not in lose:
    await init(baekjoon_id)
  return lose[baekjoon_id]

async def change_lose(baekjoon_id, delta):
  if baekjoon_id not in lose:
    await init(baekjoon_id)
  lose[baekjoon_id] += delta





async def register_member(commands, message, client):
  if len(commands) != 2:
    await message.channel.send("명령어가 잘못되었습니다.")
    return

  import fileio, validation
  member_list = await fileio.get_member_list()
  
  if await validation.valid_registered_baekjoon_id(commands[1]):
    await message.channel.send("이미 존재하는 아이디입니다.")
    return
  if await validation.valid_registered_discord_id(str(message.author.id)):
    await message.channel.send(f"이미 {get_discord_id(commands[1])}로 등록된 멤버입니다.")
    return

  if not await validation.valid_baekjoon_id(commands[1]):
    await message.channel.send("해당 백준 아이디가 존재하지 않습니다.")
    return

  import random
  print_string = "`사랑해요 주때봇 "
  for i in range(50):
    print_string += str(random.randint(0, 9))
  print_string += "`"
  
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

    alert = await validation.valid_register_url(msg.content, commands[1], print_string[1:-1])

    if alert != "pass" :
      await message.channel.send(alert)
      continue
    
    await fileio.add_member(str(message.author.id), commands[1])
    await message.channel.send(f"{message.author.mention}님이 {commands[1]}로 등록되었습니다.")
    return