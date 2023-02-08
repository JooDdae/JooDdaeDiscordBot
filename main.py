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


client.run(token)