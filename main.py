import discord

from discord_token import DISCORD_TOKEN
from fileio import get_member_list, open_makgora_log
from makgora import change_makgora_rating, request_makgora
from user import User, register_discord_user
from output import print_help, print_users, print_ranking, print_head_to_head_record
from multi import make_multi_party

headers = {"User-Agent":"JooDdae Bot"}
REQUESTS_TIMEOUT = 30

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


# boot event
@client.event
async def on_ready():
    member_list = await get_member_list()
    for discord_id, boj_id in member_list:
        User.add_user(discord_id, boj_id, False)

    log_file = await open_makgora_log()
    with log_file as file:
        for line in file:
            log = line.strip().split()
            if len(log) == 0:
                continue
            if log[0] == "makgora":
                _, challenger, challenged, result, problem, time, start_datetime, query, timeout, rated = log
                change_makgora_rating(challenger, challenged, result, int(problem), int(time), start_datetime, query, int(timeout), rated == "True", False)

@client.event
async def on_message(message: discord.Message):
    if message.author.id == client.application_id:
        return

    commands = message.content.split(" ")

    if commands[0] == "!아이디확인":
        print(message.author.id)

    if commands[0] == "!막고라신청":
        await request_makgora(commands, message, client)
    elif commands[0] == "!등록":
        await register_discord_user(commands, message, client)
    elif commands[0] == "!멤버":
        await print_users(message.channel)
    elif commands[0] == "!도움말":
        await print_help(message.channel)
    elif commands[0] == "!랭킹":
        await print_ranking(message.channel)
    elif commands[0] == "!상대전적":
        await print_head_to_head_record(commands, message)
    elif commands[0] == "!파티생성":
        await make_multi_party(commands, message, client)

client.run(DISCORD_TOKEN)
