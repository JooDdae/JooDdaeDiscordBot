

async def get_member_list():
    member_list = []
    with open("member_list.txt", "r") as f:
        for line in f:
            member_list.append(line.strip().split())
    return member_list

async def get_baekjoon_id_list():
    member_list = await get_member_list()
    baekjoon_id_list = []
    for member in member_list:
        baekjoon_id_list.append(member[1])
    return baekjoon_id_list

async def get_discord_id_list():
    member_list = await get_member_list()
    discord_id_list = []
    for member in member_list:
        discord_id_list.append(member[0])
    return discord_id_list


async def simulate_log():
    with open("match_log.txt", "r") as f:
        for line in f:
            log = line.strip().split()

            if len(log) == 0:
                continue

            if log[0] == "makgora":
                challenger = log[1]
                challenged = log[2]
                result = log[3]

                import makgora
                await makgora.result_makgora(challenger, challenged, result, False)


async def add_member(discord_id, baekjoon_id):
    with open("member_list.txt", "a") as f:
        f.write(f"{discord_id} {baekjoon_id}\n")

async def add_makgora_log(challenger, challenged, result):
    with open("match_log.txt", "a") as f:
        f.write(f"makgora {challenger} {challenged} {result}\n")