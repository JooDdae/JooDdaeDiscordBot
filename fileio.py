from io import TextIOWrapper


async def get_member_list() -> list[list[str]]:
    member_list: list[list[str]] = []
    with open("member_list.txt", "r", encoding="utf-8") as file:
        for line in file:
            member_list.append(line.strip().split())
    return member_list

async def get_discord_id_list() -> list[str]:
    member_list = await get_member_list()
    return list(map(lambda line: line[0], member_list))

async def get_boj_id_list() -> list[str]:
    member_list = await get_member_list()
    return list(map(lambda line: line[1], member_list))

def add_user(discord_id: str, boj_id: str) -> None:
    with open("member_list.txt", "a", encoding="utf-8") as file:
        file.write(f"{discord_id} {boj_id}\n")

async def open_makgora_log() -> TextIOWrapper:
    return open("match_log.txt", "r", encoding="utf-8")

def add_makgora_log(challenger: str, challenged: str, result: str, problem: int, time: int, start_datetime: str, query: str, timeout: int, rated: bool) -> None:
    with open("match_log.txt", "a", encoding="utf-8") as file:
        file.write(f"makgora {challenger} {challenged} {result} {problem} {time} {start_datetime} {query} {timeout} {rated}\n")
