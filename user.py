from typing import Any, NamedTuple, Optional
import asyncio
import secrets

import discord
from constants import REGISTER_TIMEOUT

from boj import get_user as get_user_boj, get_shared_source
from fileio import add_user as add_user_file


class UserInfo(NamedTuple):
    discord_id: str
    boj_id: str
    rating: float
    win_count: int
    lose_count: int
    tie_count: int
    active: bool

class UserTable(object):
    user_dict: dict[str, UserInfo]
    boj_user_dict: dict[str, str]
    discord_user_dict: dict[str, str]

    def __init__(self):
        self.user_dict = {}
        self.boj_user_dict = {}
        self.discord_user_dict = {}

    def new_user(self, discord_id: str, boj_id: str) -> UserInfo:
        return UserInfo(
            discord_id=discord_id,
            boj_id=boj_id,
            rating=1500,
            win_count=0,
            lose_count=0,
            tie_count=0,
            active=False
        )

    def discord_to_boj(self, discord_id: str) -> Optional[str]:
        if not discord_id in self.discord_user_dict:
            return None
        return self.discord_user_dict[discord_id]

    def boj_to_discord(self, boj_id: str) -> Optional[str]:
        if not boj_id in self.boj_user_dict:
            return None
        return self.boj_user_dict[boj_id]

    def get_user(self, boj_id: str) -> Optional[UserInfo]:
        if not boj_id in self.user_dict:
            return None
        return self.user_dict[boj_id]

    def get_discord_user(self, discord_id: str) -> Optional[UserInfo]:
        boj_id = self.discord_to_boj(discord_id)
        if boj_id is None:
            return None
        return self.get_user(boj_id)

    def get_users(self) -> list[UserInfo]:
        return list(self.user_dict.values())

    def get_user_ids(self) -> list[str]:
        return list(self.boj_user_dict.keys())

    def add_user(self, discord_id: str, boj_id: str, logging: bool = True) -> None:
        if logging:
            add_user_file(discord_id, boj_id)
        self.user_dict[boj_id] = self.new_user(discord_id, boj_id)
        self.discord_user_dict[discord_id] = boj_id
        self.boj_user_dict[boj_id] = discord_id

    def update_user(self, user: UserInfo, **kwargs: Any) -> None:
        self.user_dict[user.boj_id] = self.user_dict[user.boj_id]._replace(**kwargs)

User = UserTable()


async def register_discord_user(commands: list[str], message: discord.Message, client: discord.Client) -> None:
    if len(commands) != 2:
        await message.channel.send("명령어가 잘못되었습니다.")
        return

    boj_id = commands[1]
    discord_id = str(message.author.id)

    if discord_id in User.discord_user_dict:
        await message.channel.send("이미 아이디를 등록한 상태입니다.")
        return
    if boj_id in User.boj_user_dict:
        await message.channel.send(f"이미 {User.boj_to_discord(boj_id)}로 등록된 멤버입니다.")
        return

    if await get_user_boj(boj_id) is None:
        await message.channel.send("해당 백준 아이디가 존재하지 않습니다.")
        return

    left_time = REGISTER_TIMEOUT
    register_token = f"사랑해요 주때봇 {secrets.token_hex(16)}"

    token_msg = await message.channel.send(f"`{register_token}`")
    alert_msg = await message.channel.send("위 문구를 임의의 문제에 제출하고, 해당 코드를 공유한 주소를 입력해주세요.")

    while left_time > 0:
        try:
            msg = await client.wait_for(
                "message",
                timeout=1,
                check=lambda m: str(m.author.id) == discord_id
            )
            if msg.content == "!취소":
                await token_msg.delete()
                await alert_msg.edit(content = "취소되었습니다.")
                return

            res = await get_shared_source(msg.content)
            if res is None:
                await message.channel.send("링크가 잘못되었습니다. 다시 입력해주세요.")
                continue

            submit_id, input_string = res
            if submit_id != boj_id:
                await message.channel.send("아이디가 일치하지 않습니다. 다시 입력해주세요.")
                continue
            if input_string.strip() != register_token:
                await message.channel.send("제출한 코드가 잘못되었습니다. 다시 입력해주세요.")
                continue

            break
        except asyncio.TimeoutError:
            left_time -= 1
            await alert_msg.edit(content=f"위 문구를 임의의 문제에 제출하고, 해당 코드를 공유한 주소를 입력해주세요. ({left_time}초 남음)")
            continue

    await token_msg.delete()
    if left_time > 0:
        User.add_user(discord_id, boj_id)
        await alert_msg.edit(content=f"{message.author.mention}님이 {boj_id}로 등록되었습니다.")
    else:
        await alert_msg.edit(content="시간이 초과되었습니다.")
    return
