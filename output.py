async def print_help(commands, message, client):
  output = "!막고라신청 [난이도] [상대의 BOJ ID] : 막고라를 신청할 수 있습니다.\n"
  output += "!멤버 : 멤버 목록을 확인할 수 있습니다.\n"
  output += "!등록 [BOJ ID] : 계정을 등록할 수 있습니다.\n"
  output += "!취소 : 진행중인 막고라나 신청을 취소할 수 있습니다.\n"
  output += "!도움말 : 도움말을 확인할 수 있습니다."
  await message.channel.send(output)

async def print_ranking(commands, message, client):
  import members
  top_list = sorted(members.member_list, key = lambda x: [int(x[2]), -1][int(x[3])+int(x[4]) == 0], reverse=True)[:10]

  rank = 1
  output = "```ansi\n[0;41m"
  for i in range(len(top_list)):
    if i > 0 and top_list[i-1][2] != top_list[i][2]:
      rank = i+1
    is_unrank = int(top_list[i][3])+int(top_list[i][4]) == 0
    if top_list[i][2] != top_list[0][2] : output += "[0m឵"
    p = [str(rank), "-"][is_unrank] + " " + top_list[i][1]

    rating = [top_list[i][2], "---"][is_unrank]
    p += " "*(15-len(top_list[i][1])) + rating
    p += " "*(6-len(rating)) + [top_list[i][3], '-'][is_unrank] + "승 " + [top_list[i][4], '-'][is_unrank] + "패"
    output +=  p + "\n"
  output += "\n```"
  await message.channel.send(output)

async def print_member(commands, message):
  import members
  if len(commands) == 1:
    msg = "멤버 목록입니다. 멤버의 정보를 보려면 '!멤버 [멤버 이름]'을 입력해주세요.\n"
    for member in members.member_list:
      msg += member[1] + " "
    await message.channel.send(msg)
  elif len(commands) == 2:
    for member in members.member_list:
      if member[1] == commands[1]:
        msg = "백준 아이디: " + member[1] + "\n"
        msg += "레이팅: " + member[2] + "\n"
        msg += "승: " + member[3] + "\n"
        msg += "패: " + member[4] + "\n"
        await message.channel.send(msg)
        return
    await message.channel.send("해당 멤버가 존재하지 않습니다.")