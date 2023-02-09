from typing import Any

from user import User, UserInfo


# channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread, discord.DMChannel, discord.GroupChannel, discord.PartialMessageable]

async def print_help(channel: Any) -> None:
    output = "`!막고라신청 [난이도] [상대의 BOJ ID] (추가쿼리)` - 막고라를 신청할 수 있습니다.\n"
    output += "`!멤버` - 등록된 멤버의 목록을 확인할 수 있습니다.\n"
    output += "`!등록 [BOJ ID]` - 계정을 등록할 수 있습니다.\n"
    output += "`!취소` - 진행중인 막고라나 신청을 취소할 수 있습니다.\n"
    output += "`!도움말` - 도움말을 확인할 수 있습니다."
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

        output += f"{rank:<3} {user.boj_id:<15} {user.rating:4.0f} {user.win_count:4}승 {user.tie_count:4}무 {user.lose_count}패\n"
        prev_user = user

    output += "\n```"
    await channel.send(output)

async def print_result(channel: Any, winner: UserInfo, loser: UserInfo, delta: tuple[float, float], tied: bool = False) -> None:
    wr = winner.rating
    lr = loser.rating

    output = "결과가 반영되었습니다.\n"
    if not tied:
        output += "승자: "
    output += f"<@{winner.discord_id}> ({winner.boj_id}): {wr:.0f} :arrow_right: {wr + delta[0]:.0f} ({delta[0]:+.0f})\n"
    if not tied:
        output += "패자: "
    output += f"<@{loser.discord_id}> ({loser.boj_id}): {lr:.0f} :arrow_right: {lr + delta[1]:.0f} ({delta[1]:+.0f})"
    await channel.send(output)
