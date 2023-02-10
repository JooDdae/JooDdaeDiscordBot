from typing import Any

import discord

from record import Record
from user import User, UserInfo
from util import add_delta_color


# channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread, discord.DMChannel, discord.GroupChannel, discord.PartialMessageable]

async def print_help(channel: Any) -> None:
    output = "`!막고라신청 <상대의 BOJ ID>` - 막고라를 신청할 수 있습니다.\n"
    output += "`!멤버` - 등록된 멤버의 목록을 확인할 수 있습니다.\n"
    output += "`!등록 [BOJ ID]` - 계정을 등록할 수 있습니다.\n"
    output += "`!취소` - 신청을 취소할 수 있습니다."
    await channel.send(output)

async def print_users(channel: Any) -> None:
    user_ids = " ".join(User.get_user_ids())
    output = "등록된 멤버 목록입니다.\n"
    output += f"```ansi\n{user_ids}\n```"
    await channel.send(output)
#     if len(commands) == 1:
#         msg = "멤버 목록입니다. 멤버의 정보를 보려면 "!멤버 [멤버 이름]"을 입력해주세요.\n"
#         for member in members.member_list:
#             msg += member[1] + " "
#         await message.channel.send(msg)
#     elif len(commands) == 2:
#         for member in members.member_list:
#             if member[1] == commands[1]:
#                 msg = "백준 아이디: " + member[1] + "\n"
#                 msg += "레이팅: " + member[2] + "\n"
#                 msg += "승: " + member[3] + "\n"
#                 msg += "패: " + member[4] + "\n"
#                 await message.channel.send(msg)
#                 return
#         await message.channel.send("해당 멤버가 존재하지 않습니다.")

async def print_ranking(channel: Any) -> None:
    ranking: list[UserInfo] = []

    for user in User.get_users():
        if user.win_count + user.tie_count + user.lose_count > 0:
            ranking.append(user)
    ranking.sort(key=lambda x: x.rating, reverse=True)

    if len(ranking) == 0:
        return

    rank = 1
    prev_user = ranking[0]
    top_rating = prev_user.rating
    output = "```ansi\n\x1B[0;41m"
    for i, user in enumerate(ranking):
        if i > 0 and prev_user.rating != user.rating:
            rank = i + 1

        if user.rating != top_rating:
            output += "\x1B[0m឵"

        output += f"{rank:<3} {user.boj_id:<15} {user.rating:4.0f} {user.win_count:4}승 {user.tie_count:4}무 {user.lose_count:4}패\n"
        prev_user = user

    output += "\n```"
    await channel.send(output)

async def print_result(channel: Any, winner: UserInfo, loser: UserInfo, delta: float, result: str) -> None:
    if result == "lose":
        winner, loser, delta = loser, winner, -delta
    wr = winner.rating
    lr = loser.rating

    output = "결과가 반영되었습니다.\n"
    if result != "tie":
        output += "승자: "
    output += f"<@{winner.discord_id}> ({winner.boj_id}): {wr:.0f} :arrow_right: {wr + delta:.0f} ({delta:+.0f})\n"
    if result != "tie":
        output += "패자: "
    output += f"<@{loser.discord_id}> ({loser.boj_id}): {lr:.0f} :arrow_right: {lr - delta:.0f} ({-delta:+.0f})"
    await channel.send(output)

async def print_head_to_head_record(commands: list[str], message: discord.Message):
    if not 2 <= len(commands) <= 3:
        await message.channel.send("`!상대전적 <상대의 BOJ ID>` 혹은 `!상대전적 <BOJ ID1> <BOJ ID2>` 로 상대전적을 확인할 수 있습니다.")
        return

    if len(commands) == 2:
        discord_id = str(message.author.id)
        user = User.get_discord_user(discord_id)
        if user is None:
            await message.channel.send(f"{message.author.mention}님은 아직 봇에 등록하지 않았습니다. `!등록 <백준 아이디>` 명령어로 등록해주세요.")
            return
        await print_head_to_head_record([commands[0], user.boj_id, commands[1]], message)
        return

    user1, user2 = User.get_user(commands[1]), User.get_user(commands[2])

    if user1 is None:
        await message.channel.send(f"{commands[1]}님은 아직 봇에 등록하지 않았습니다.")
        return
    if user2 is None:
        await message.channel.send(f"{commands[2]}님은 아직 봇에 등록하지 않았습니다.")
        return

    record_list = Record.get_head_to_head_record(user1.boj_id, user2.boj_id)
    if record_list is None:
        await message.channel.send(f"{user1.boj_id}와 {user2.boj_id}의 전적을 찾을 수 없습니다.")
        return
    
    line_length = 50
    output = "```ansi\n\x1B[0m"
    output += f"{user1.boj_id:^25}{user2.boj_id:^25}\n"
    rating1, rating2 = f"{user1.rating:4.0f}", f"{user2.rating:4.0f}"
    output += f"{rating1:^25}{rating2:^25}\n"
    output2 = "\x1B[32m" + "-"*line_length + "\x1B[1m\n"
    win_count, tie_count, lose_count = 0, 0, 0
    for match_type, challenger, challenged, result, delta, _, _, _ in record_list:
        is_challenger = challenger.boj_id == user1.boj_id
        is_winner = (is_challenger and result == "win") or (not is_challenger and result == "lose")
        win_count += 1 if is_winner else 0
        lose_count += 1 if not is_winner else 0
        tie_count += 1 if result == "tie" else 0
        user1_delta = delta if is_challenger else -delta
        user2_delta = -delta if is_challenger else delta
        user1_rating = challenger.rating if is_challenger else challenged.rating
        user2_rating = challenged.rating if is_challenger else challenger.rating
        output2 += ("\x1B[33mT" if result == 'tie' else "\x1B[34mW" if is_winner else '\x1B[31mL') + f"\x1B[0m {user1_rating:4.0f} ⇒ {user1_rating+user1_delta:4.0f} ({add_delta_color(user1_delta)})  "
        output2 += "==" if is_challenger else "<="
        output2 += "💀" if match_type == "makgora" else "?"
        output2 += "=>" if is_challenger else "=="
        output2 += f"  {user2_rating:4.0f} ⇒ {user2_rating+user2_delta:4.0f} ({add_delta_color(user2_delta)}) " + ("\x1B[33mT" if result == 'tie' else '\x1B[31mL' if is_winner else "\x1B[34mW") + "\x1B[0m\n"
    output2 += "```"
    win, tie, lose = f"{win_count}승", f"{tie_count}무", f"{lose_count}패"
    await message.channel.send(output + f"       {win:^11}{tie:^13}{lose:^11}        \x1B[0m\n" + output2)
