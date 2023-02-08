import discord
import discord_token

token = discord_token.discord_token
headers = {"User-Agent":"JooDdae Bot"}
MAX_TIMEOUT = 30

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
  
  if message.author.id == client.user.id:
    return

  commands = message.content.split(" ")
  
  if commands[0] == "!막고라신청":
    import makgora
    await makgora.request_makgora(commands, message, client)
  elif commands[0] == "!멤버":
    import members
    await members.print_member(commands, message)
  elif commands[0] == "!등록":
    import members
    await members.register_member(commands, message, client)
  elif commands[0] == "!도움말":
    await message.channel.send("!막고라신청 [난이도] [상대의 BOJ ID] : 막고라를 신청할 수 있습니다.\n!멤버 : 멤버 목록을 확인할 수 있습니다.\n!등록 [BOJ ID] : 계정을 등록할 수 있습니다.\n!취소 : 진행중인 막고라나 신청을 취소할 수 있습니다.\n!도움말 : 도움말을 확인할 수 있습니다.")

client.run(token)