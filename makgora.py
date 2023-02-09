import asyncio    
MAX_TIMEOUT = 30

async def request_makgora(commands, message, client):
    import members, validation

    if len(commands) == 1:
            await message.channel.send("'!막고라신청 [난이도] [상대방 아이디] (추가쿼리)' 로 상대방에게 막고라를 신청할 수 있습니다.")
            return

    discord_id1 = str(message.author.id)
    if await validation.valid_registered_discord_id(discord_id1) == False:
        await message.channel.send(f"{message.author.mention}님은 아직 등록하지 않았습니다. '!등록 [백준 아이디]' 형식으로 등록해주세요.")
        return
    baekjoon_id1 = await members.get_baekjoon_id(discord_id1)

    if await members.is_active(baekjoon_id1):
        await message.channel.send("다른 활동을 하고 있어 막고라를 신청할 수 없습니다.")
        return
    invalid = ""
    if await validation.valid_tier(commands[1]) == False:
        invalid += "티어의 범위가 잘못되었습니다.\n"
    elif await validation.valid_registered_baekjoon_id(commands[2]) == False:
        invalid += "등록되지 않은 백준 아이디입니다.\n"
    elif baekjoon_id1 == commands[2]:
        invalid += "자기 자신에게 막고라를 신청할 수 없습니다.\n"
    
    if invalid != "":
        invalid += "'!막고라신청 [난이도] [상대방 아이디] (추가쿼리)' 형식으로 입력해주세요."
        await message.channel.send(invalid)
        return

    tier = commands[1]
    baekjoon_id2 = commands[2]
    left_second = 5

    query = ""
    for i in range(3, len(commands)):
        query += "%20" + commands[i]
    
    if await members.is_active(baekjoon_id2):
        await message.channel.send("상대방이 다른 활동을 하고 있어 막고라를 신청할 수 없습니다.")
        return
    await members.active_list_add([baekjoon_id1, baekjoon_id2])
    
    request_message = f"<@{discord_id1}>({baekjoon_id1})님, {tier} 난이도의 문제로 {baekjoon_id2}에게 막고라를 신청하는게 맞습니까?"
    if query != "":
        nq = query.replace("%20", " ")
        request_message += f" (추가 쿼리 <{nq}>)"
    
    msg = await message.channel.send(request_message)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    def check_reaction_request(reaction, user):
        return user == message.author and str(reaction.emoji) in ["✅", "❌"]
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=MAX_TIMEOUT, check=check_reaction_request)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
        await msg.edit(content = "시간이 초과되었습니다.")
        await members.active_list_del([baekjoon_id1, baekjoon_id2])
        return
    await msg.clear_reactions()
    if str(reaction.emoji) == "❌":
        await msg.edit(content = "취소되었습니다.")
        await members.active_list_del([baekjoon_id1, baekjoon_id2])
        return


    discord_id2 = await members.get_discord_id(baekjoon_id2)
    msg = await message.channel.send(f"<@{discord_id2}>({baekjoon_id2})님, <@{discord_id1}>({baekjoon_id1})님의 막고라 신청을 수락하겠습니까?", reference = msg)
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    def check_reaction_request2(reaction, user):
        return str(user.id) == discord_id2 and str(reaction.emoji) in ["✅", "❌"]
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=MAX_TIMEOUT, check=check_reaction_request2)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
        await msg.edit(content = "시간이 초과되었습니다.")
        await members.active_list_del([baekjoon_id1, baekjoon_id2])
        return
    await msg.clear_reactions()
    if str(reaction.emoji) == "❌":
        await msg.edit(content = "거절했습니다.")
        await members.active_list_del([baekjoon_id1, baekjoon_id2])
        return

    await start_makgora(commands, message, client, tier, baekjoon_id1, baekjoon_id2, left_second, discord_id1, discord_id2, query)
    await members.active_list_del([baekjoon_id1, baekjoon_id2])


async def result_makgora(challenger, challenged, result, add_log = True):
    import fileio, members, ex_functions
    if add_log == True:
        await fileio.add_makgora_log(challenger, challenged, result)

    winner = challenger
    loser = challenged
    wr = await members.get_rating(winner)
    lr = await members.get_rating(loser)

    if result == "tie" :
        if wr < lr:
            winner, loser = loser, winner
            wr, lr = lr, wr
        delta1 = await ex_functions.calculate_delta(wr, lr, result)
        delta2 = await ex_functions.calculate_delta(lr, wr, result)
        await members.change_rating(winner, delta1)
        await members.change_rating(loser, delta2)
        await members.change_tie(winner, 1)
        await members.change_tie(loser, 1)
        return [delta1, delta2]

    if result == "lost":
        winner, loser = loser, winner
        wr, lr = lr, wr

    delta1 = await ex_functions.calculate_delta(wr, lr, "win")
    delta2 = await ex_functions.calculate_delta(wr, lr, "lose")
    await members.change_rating(winner, delta1)
    await members.change_win(winner, 1)
    await members.change_rating(loser, delta2)
    await members.change_lose(loser, 1)
    return [delta1, delta2]


async def start_makgora(commands, message, client, tier, baekjoon_id1, baekjoon_id2, left_second, discord_id1, discord_id2, query):
    import solvedac_api, output, boj_crawling, ex_functions
    problem_list = await solvedac_api.get_problems("*" + tier + "%20-solved_by%3A" + baekjoon_id1 + "%20-solved_by%3A" + baekjoon_id2 + query, 1)

    if problem_list == [-1]:
        msg = await message.channel.send("API가 정상적으로 동작하지 않아 취소되었습니다.")
        return
    
    if problem_list == [-2]:
        msg = await message.channel.send("해당 난이도의 문제가 없어 취소되었습니다.")
        return

    problem = problem_list[0]
    await message.channel.send(baekjoon_id1 + "과 " + baekjoon_id2 + "의 막고라가 시작됩니다.")
    await message.channel.send(problem['titleKo'] + " https://www.acmicpc.net/problem/" + str(problem['problemId']))
    await message.channel.send("문제를 풀고 나서 '!컷'을 입력해주세요. 이 명령어는 막고라를 진행중인 두 사람만 사용할 수 있습니다.")

    def check_message(message):
        return message.content == "!컷" and (str(message.author.id) == discord_id1 or str(message.author.id) == discord_id2)

    msg_time = await message.channel.send("남은 시간 " + await ex_functions.second_to_krtime(left_second))

    async def check_result():
        result1 = await boj_crawling.first_ac_submission(baekjoon_id1, problem['problemId'])
        result2 = await boj_crawling.first_ac_submission(baekjoon_id2, problem['problemId'])
        if result1 == -1 and result2 == -1:
            return False
        winner = [baekjoon_id2, baekjoon_id1][result2 == -1 or (result1 != -1 and result1 < result2)]
        loser = [baekjoon_id2, baekjoon_id1][baekjoon_id2 == winner]
        await message.channel.send(winner + "가 먼저 문제를 해결했습니다.")
        delta = await result_makgora(winner, loser, "win")
        await output.print_change(message.channel, winner, loser, delta)
        return True

    while True:
        try:
            msg = await client.wait_for('message', timeout=1, check=check_message)
        except asyncio.TimeoutError:
            if left_second == 0 :
                await msg_time.edit(content = "종료")
                if not await check_result():
                    await message.channel.send("제한시간이 초과되었습니다.")
                    delta = await result_makgora(baekjoon_id1, baekjoon_id2, "tie")
                    await output.print_tie(message.channel, baekjoon_id1, baekjoon_id2, delta)
                    return
                return
            await msg_time.edit(content = "남은 시간 " + await ex_functions.second_to_krtime(left_second))
            left_second -= 1
        else:
            if await check_result() :
                return
            await message.channel.send("둘 다 아직 풀지 않았습니다.")