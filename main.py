import discord
import discord_token

token = discord_token.discord_token
headers = {"User-Agent":"JooDdae Bot"}
MAX_TIMEOUT = 30

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# boot event
@client.event
async def on_ready():
    import fileio
    await fileio.simulate_log()

@client.event
async def on_message(message):
    print(client.application_id)
    if message.author.id == client.application_id:
        return

    commands = message.content.split(" ")
    
    if commands[0] == "!아이디확인":
        print(message.author.id)
    
    import makgora, members, output

    if commands[0] == "!막고라신청":
        await makgora.request_makgora(commands, message, client)
    elif commands[0] == "!등록":
        await members.register_member(commands, message, client)
    elif commands[0] == "!멤버":
        await output.print_member(message.channel)
    elif commands[0] == "!도움말":
        await output.print_help(message.channel)
    elif commands[0] == "!랭킹":
        await output.print_ranking(message.channel)
    
client.run(token)