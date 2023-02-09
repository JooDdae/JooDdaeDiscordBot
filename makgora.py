from typing import Literal
import asyncio

import discord
from boj import get_accepted_submission
from constants import MAKGORA_DEFAULT_TIMEOUT, REACTION_TIMEOUT
from fileio import add_makgora_log
from output import print_result
from solvedac import get_problems

from user import User
from util import seconds_to_krtime



def valid_tier(tier: str) -> bool:
    tier = tier.lower()
    if len(tier) == 1:
        return tier[0] in "bsgpdr"
    elif len(tier) == 2:
        return (tier[0] in "bsgpdr" and tier[1] in "12345") or (tier[0] in "1234567890" and tier[1] in "1234567890" and int(tier) <= 30)
    elif len(tier) <= 6:
        if ".." not in tier:
            return False
        tiers = tier.split("..")
        if len(tiers) == 2:
            if len(tiers[0]) == 0:
                return valid_tier(tiers[1])
            elif len(tiers[1]) == 0:
                return valid_tier(tiers[0])
            else:
                return valid_tier(tiers[0]) and valid_tier(tiers[1])
    return False

def elo_delta(rating_a: float, rating_b: float, result: Literal["win", "lose", "tie"]) -> float:
    weight = 0.5
    if result == "win":
        weight = 1
    elif result == "lose":
        weight = 0
    delta = 32 * (weight - 1 / (1 + 10 ** ((rating_b - rating_a) / 400)))
    return delta

def change_rating(challenger: str, challenged: str, result: str, logging: bool = True) -> tuple[float, float]:
    if logging:
        add_makgora_log(challenger, challenged, result)

    winner = User.get_user(challenger)
    loser = User.get_user(challenged)
    if winner is None or loser is None:
        return (0.0, 0.0)
    if result == "lose":
        winner, loser = loser, winner

    wr = winner.rating
    lr = loser.rating

    if result == "tie":
        if wr < lr:
            winner, loser = loser, winner
            wr, lr = lr, wr
        winner_delta = elo_delta(wr, lr, "tie")
        loser_delta = elo_delta(lr, wr, "tie")
        User.update_user(winner, rating=wr + winner_delta, tie_count=winner.tie_count + 1)
        User.update_user(loser, rating=lr + loser_delta, tie_count=loser.tie_count + 1)
        return (winner_delta, loser_delta)

    winner_delta = elo_delta(wr, lr, "win")
    loser_delta = elo_delta(wr, lr, "lose")
    User.update_user(winner, rating=wr + winner_delta, win_count=winner.win_count + 1)
    User.update_user(loser, rating=lr + loser_delta, lose_count=loser.lose_count + 1)
    return (winner_delta, loser_delta)

async def request_makgora(commands: list[str], message: discord.Message, client: discord.Client) -> None:
    if len(commands) < 3:
        await message.channel.send("`!막고라신청 <난이도> <상대방 아이디> [추가쿼리]` 로 상대방에게 막고라를 신청할 수 있습니다.")
        return

    tier = commands[1]
    target_boj_id = commands[2]
    query = " ".join(commands[3:])

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
    if not valid_tier(tier):
        await message.channel.send("티어의 범위가 잘못되었습니다.")
        return

    if user.active:
        await message.channel.send("다른 활동을 하고 있어 막고라를 신청할 수 없습니다.")
        return
    if target.active:
        await message.channel.send("상대방이 다른 활동을 하고 있어 막고라를 신청할 수 없습니다.")
        return

    request_message = f"<@{discord_id}>({boj_id})님, {tier} 난이도의 문제로 {target_boj_id}에게 막고라를 신청하는게 맞습니까?"
    if query != "":
        request_message += f" (추가 쿼리 `{query}`)"

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
    problem_list = await get_problems(f"*{tier} -solved_by:{boj_id} -solved_by:{target_boj_id} {query}")

    if problem_list == -1:
        msg = await message.channel.send("API가 정상적으로 동작하지 않아 취소되었습니다.")
        return

    if problem_list == -2:
        msg = await message.channel.send("해당 난이도의 문제가 없어 취소되었습니다.")
        return

    problem = problem_list[0]
    await message.channel.send(f"{boj_id}와 {target_boj_id}의 막고라가 시작됩니다.")
    await message.channel.send(f"{problem['titleKo']}: https://www.acmicpc.net/problem/{problem['problemId']}")
    await message.channel.send("문제를 풀고 나서 `!컷`을 입력해주세요. 이 명령어는 막고라를 진행중인 두 사람만 사용할 수 있습니다.")

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

    if left_second > 0:
        result = "win" if result2 == -1 or (result1 != -1 and result1 < result2) else "lose"
        delta = change_rating(boj_id, target_boj_id, result)
        winner = user if result == "win" else target
        loser = user if result == "lose" else target
        await message.channel.send(f"{winner.boj_id}가 먼저 문제를 해결했습니다.")
        await print_result(message.channel, winner, loser, delta)
    else:
        delta = change_rating(boj_id, target_boj_id, "tie")
        winner = user if user.rating > target.rating else target
        loser = user if user.rating <= target.rating else target
        await time_msg.edit(content = "종료")
        await message.channel.send("제한시간이 초과되었습니다.")
        await print_result(message.channel, winner, loser, delta, True)

    User.update_user(user, active=False)
    User.update_user(target, active=False)
