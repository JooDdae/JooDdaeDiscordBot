import asyncio
from datetime import datetime as dt

import discord
from boj import get_accepted_submission, get_submit_time
from constants import MAKGORA_DEFAULT_TIMEOUT, REACTION_TIMEOUT
from fileio import add_makgora_log
from output import print_result
from solvedac import get_random_problems

from user import User
from record import Record
from util import seconds_to_krtime
from elo import elo_delta


def change_makgora_rating(user: str, target: str, result: str, problem: int, time: int, start_time: str, logging: bool = True) -> float:
    if logging:
        add_makgora_log(user, target, result, problem, time, start_time)

    challenger = User.get_user(user)
    challenged = User.get_user(target)
    if challenger is None or challenged is None:
        return 0.0

    delta = elo_delta(challenger.rating, challenged.rating, result)
    Record.add_record('makgora', challenger, challenged, result, delta, problem, time, start_time)

    if result == "tie":
        User.update_user(challenger, rating=challenger.rating + delta, tie_count=challenger.tie_count + 1)
        User.update_user(challenged, rating=challenged.rating - delta, tie_count=challenger.tie_count + 1)
    elif result == "win":
        User.update_user(challenger, rating=challenger.rating + delta, win_count=challenger.win_count + 1)
        User.update_user(challenged, rating=challenged.rating - delta, lose_count=challenged.lose_count + 1)
    else:
        User.update_user(challenger, rating=challenger.rating + delta, lose_count=challenger.lose_count + 1)
        User.update_user(challenged, rating=challenged.rating - delta, win_count=challenged.win_count + 1)

    return delta

async def request_makgora(commands: list[str], message: discord.Message, client: discord.Client) -> None:
    if len(commands) < 2:
        await message.channel.send("`!막고라신청 <상대의 BOJ ID> [추가쿼리]` 로 상대방에게 막고라를 신청할 수 있습니다.")
        return

    target_boj_id = commands[1]
    query = " ".join(commands[2:])

    discord_id = str(message.author.id)
    user = User.get_discord_user(discord_id)
    target = User.get_user(target_boj_id)
    if user is None:
        await message.channel.send(f"{message.author.mention}님은 아직 봇에 등록하지 않았습니다. `!등록 <백준 아이디>` 명령어로 등록해주세요.")
        return
    if target is None:
        await message.channel.send(f"{target_boj_id}님은 아직 봇에 등록하지 않았습니다.")
        return

    boj_id = user.boj_id
    target_discord_id = target.discord_id
    if target_boj_id == boj_id:
        await message.channel.send("자기 자신에게 막고라를 신청할 수 없습니다.")
        return

    if user.active:
        await message.channel.send("다른 활동을 하고 있어 막고라를 신청할 수 없습니다.")
        return
    if target.active:
        await message.channel.send("상대방이 다른 활동을 하고 있어 막고라를 신청할 수 없습니다.")
        return

    request_message = f"<@{discord_id}>({boj_id})님, `{query}`의 쿼리로 {target_boj_id}님에게 막고라를 신청하는게 맞습니까?"

    msg = await message.channel.send(request_message)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    User.update_user(user, active=True)
    User.update_user(target, active=True)
    try:
        reaction, _ = await client.wait_for(
            "reaction_add",
            timeout=REACTION_TIMEOUT,
            check=lambda r, u: str(u.id) == discord_id and str(r.emoji) in ("✅", "❌")
        )
        await msg.clear_reactions()

        if str(reaction.emoji) == "❌":
            User.update_user(user, active=False)
            User.update_user(target, active=False)
            await msg.edit(content = "취소되었습니다.")
            return
    except asyncio.TimeoutError:
        User.update_user(user, active=False)
        User.update_user(target, active=False)
        await msg.clear_reactions()
        await msg.edit(content = "시간이 초과되었습니다.")
        return

    msg = await message.channel.send(f"<@{target_discord_id}>({target_boj_id})님, <@{discord_id}>({boj_id})님의 막고라 신청을 수락하겠습니까?", reference=msg)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    try:
        reaction, _ = await client.wait_for(
            "reaction_add",
            timeout=REACTION_TIMEOUT,
            check=lambda r, u: str(u.id) == target_discord_id and str(r.emoji) in ("✅", "❌")
        )

        await msg.clear_reactions()
        if str(reaction.emoji) == "❌":
            User.update_user(user, active=False)
            User.update_user(target, active=False)
            await msg.edit(content = "거절했습니다.")
            return
    except asyncio.TimeoutError:
        User.update_user(user, active=False)
        User.update_user(target, active=False)
        await msg.clear_reactions()
        await msg.edit(content = "시간이 초과되었습니다.")
        return

    left_second = MAKGORA_DEFAULT_TIMEOUT
    problem_list = await get_random_problems(f"-solved_by:{boj_id} -solved_by:{target_boj_id} {query}")

    if problem_list == -1:
        User.update_user(user, active=False)
        User.update_user(target, active=False)
        msg = await message.channel.send("API가 정상적으로 동작하지 않아 취소되었습니다.")
        return

    if problem_list == -2:
        User.update_user(user, active=False)
        User.update_user(target, active=False)
        msg = await message.channel.send("해당 난이도의 문제가 없어 취소되었습니다.")
        return

    problem = problem_list[0]
    await message.channel.send(f"{boj_id}와 {target_boj_id}의 막고라가 시작됩니다.")
    await message.channel.send(f"{problem['titleKo']}: https://www.acmicpc.net/problem/{problem['problemId']}")
    await message.channel.send("문제를 풀고 나서 `!컷`을 입력해주세요. 이 명령어는 막고라를 진행중인 두 사람만 사용할 수 있습니다.")

    start_time = dt.now()
    time_msg = await message.channel.send(f"남은 시간  {seconds_to_krtime(left_second)}")

    result1 = -1
    result2 = -1
    while left_second > 0:
        try:
            msg = await client.wait_for(
                "message",
                timeout=1,
                check=lambda m: m.content == "!컷" and str(m.author.id) in (discord_id, target_discord_id)
            )
            result1 = await get_accepted_submission(boj_id, problem["problemId"])
            result2 = await get_accepted_submission(target_boj_id, problem["problemId"])
            if result1 != -1 or result2 != -1:
                break
            await message.channel.send("둘 다 아직 풀지 않았습니다.")
        except asyncio.TimeoutError:
            left_second -= 1
            await time_msg.edit(content=f"남은 시간: {seconds_to_krtime(left_second)}")

    result = "win" if result2 == -1 or (result1 != -1 and result1 < result2) else "lose" if result1 != -1 or result2 != -1 else "tie"

    end_time = start_time if result == "tie" else await get_submit_time(result1 if result == "win" else result2)
    time_delta = int((end_time - start_time).total_seconds()) if end_time is not None else MAKGORA_DEFAULT_TIMEOUT
    delta = change_makgora_rating(boj_id, target_boj_id, result, problem["problemId"], time_delta, start_time.strftime("%Y-%m-%d/%H:%M:%S"))

    if result != "tie":
        winner = user if result == "win" else target
        await message.channel.send(f"{winner.boj_id}가 먼저 문제를 해결했습니다.")
    await print_result(message.channel, user, target, delta, result)

    User.update_user(user, active=False)
    User.update_user(target, active=False)
