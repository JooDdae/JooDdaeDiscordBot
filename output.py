async def print_help(channel):
  output = "!막고라신청 [난이도] [상대의 BOJ ID] (추가쿼리) : 막고라를 신청할 수 있습니다.\n"
  output += "!멤버 : 등록된 멤버의 목록을 확인할 수 있습니다.\n"
  output += "!등록 [BOJ ID] : 계정을 등록할 수 있습니다.\n"
  output += "!취소 : 진행중인 막고라나 신청을 취소할 수 있습니다.\n"
  output += "!도움말 : 도움말을 확인할 수 있습니다."
  await channel.send(output)

async def print_ranking(commands, message, client):
  import members, fileio, validation

  baekjoon_id_list = await fileio.get_baekjoon_id_list()
  top_list = []

  for baekjoon_id in baekjoon_id_list:
    if await validation.valid_logged_id(baekjoon_id):
      top_list.append([baekjoon_id, await members.get_rating(baekjoon_id), await members.get_win(baekjoon_id), await members.get_lose(baekjoon_id)])
  
  top_list.sort(key=lambda x: x[1], reverse=True)

  rank = 1
  output = "```ansi\n[0;41m"
  for i in range(len(top_list)):
    if i > 0 and top_list[i-1][1] != top_list[i][1]:
      rank = i+1
    
    baekjoon_id, rating, win, lose = top_list[i]
    if top_list[i][2] != top_list[0][2] : output += "[0m឵"

    p = str(rank) + " " + baekjoon_id
    p += " "*(15-len(baekjoon_id)) + str(rating)
    p += " "*(6-len(str(rating))) + str(win) + "승 " + str(lose) + "패"
    output += p + "\n"
  output += "\n```"
  await message.channel.send(output)

async def print_member(commands, message):
  import fileio
  baekjoon_id_list = await fileio.get_baekjoon_id_list()
  output = "등록된 멤버 목록입니다.\n"
  output += "```ansi\n"
  for baekjoon_id in baekjoon_id_list:
    output += baekjoon_id + " "
  output += "\n```"
  await message.channel.send(output)
#   if len(commands) == 1:
#     msg = "멤버 목록입니다. 멤버의 정보를 보려면 '!멤버 [멤버 이름]'을 입력해주세요.\n"
#     for member in members.member_list:
#       msg += member[1] + " "
#     await message.channel.send(msg)
#   elif len(commands) == 2:
#     for member in members.member_list:
#       if member[1] == commands[1]:
#         msg = "백준 아이디: " + member[1] + "\n"
#         msg += "레이팅: " + member[2] + "\n"
#         msg += "승: " + member[3] + "\n"
#         msg += "패: " + member[4] + "\n"
#         await message.channel.send(msg)
#         return
#     await message.channel.send("해당 멤버가 존재하지 않습니다.")
  
async def print_change(channel, winner, loser, delta):
  import members
  wr = await members.get_rating(winner)
  lr = await members.get_rating(loser)

  output = "결과가 반영되었습니다.\n"
  output += f"승자 : <@{await members.get_discord_id(winner)}>({winner}) ({wr-delta} :arrow_right: {wr} (+{delta}))\n"
  output += f"패자 : <@{await members.get_discord_id(loser)}>({loser}) ({lr+delta} :arrow_right: {lr} (-{delta}))"
  await channel.send(output)