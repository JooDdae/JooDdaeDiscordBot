import { Message } from "discord.js";

import { getAcceptedSubmission } from "../io/boj";
import { getRandomProblems } from "../io/solvedac";
import { DEFAULT_MAKGORA_TIMEOUT, REACTION_TIMEOUT } from "../constants";
import { OnCleanup, assert, colorDelta, eloDelta, getReactions, getTwoStepCommands, sendTimer, transformPresetQuery } from "../common";
import { User, addMakgora, getActive, getUser, getUserByBojId, setActive } from "../io/db";

const usage = "`!막고라 <상대의 BOJ ID | @멘션> <솔브드 쿼리> [t=60] [r=1]` 으로 상대방에게 막고라를 신청할 수 있습니다.\n"
		+ "`t`와 `r`은 비필수 옵션이며, 각각 `제한 시간(분 단위)`, `레이팅 적용 여부(0이면 미적용)`를 의미합니다. \n"
		+ "예시: `!막고라 kyo20111 *p5..1`, `!막고라 cgiosy *s lang:en t=30 r=false`, `!막고라 @주때`\n";

const sameUser = `자기 자신에게 막고라를 신청할 수 없습니다.`;

const userAlreadyActive = `이미 다른 곳에 참가한 상태이므로, 끝나기 전까지 다른 대상에게 막고라를 신청할 수 없습니다.`;

const targetAlreadyActive = `상대방이 이미 다른 곳에 참가한 상태이므로, 끝나기 전까지 대상에게 막고라를 신청할 수 없습니다.`;

const reactionTimedOut = `시간이 초과되었습니다.`;

const cancelled = `취소되었습니다.`;

const notFound = `조건에 맞는 문제가 없어 취소되었습니다.`;

const noSolver = `둘 모두 풀지 못한 상태입니다.`;

const notRegisteredUser = (userId: string) => (
	`<@${userId}>님은 아직 봇에 등록하지 않았습니다. \`!등록 <백준 아이디>\` 명령어로 등록해주세요.`
);

const notRegisteredTarget = (targetId: string) => (
	`\`${targetId}\`님은 아직 봇에 등록하지 않았습니다. 봇에 등록된 사람에게만 막고라를 신청할 수 있습니다.`
);

const checkMakgora = (query: string, timeout: number, rated: boolean, targetId: string, targetBojId: string) => (
	`쿼리 \`${query}\`, 제한 시간 \`${(timeout / 60000).toFixed(0)}\`분, 레이팅 ${rated ? "" : "미"}반영으로 `
	+ `<@${targetId}>(${targetBojId})님에게 막고라를 신청합니다. 수락하시겠습니까?`
);

const startMakgora = (userId: string, targetId: string, titleKo: string, problemId: string | number) => (
	`# ${titleKo}: https://www.acmicpc.net/problem/${problemId}\n`
	+ `<@${userId}>가 <@${targetId}>에게 신청한 막고라가 성사되었습니다. 막고라 중인 두 사람은 다음 명령어를 사용 가능합니다.\n`
	+ "`!컷`: 문제를 둘 중 한 명 이상이 풀었는지 확인하고, 먼저 푼 쪽의 승리로 끝냅니다.\n"
	+ "🛑: 둘 모두 무승부를 요청할 경우, 무승부로 끝냅니다.\n"
	+ "🏳️: 항복을 요청할 경우, 상대방의 승리로 끝냅니다."
);

const remainTime = (remain: number) => `무승부로 강제 종료까지 남은 시간: ${(remain / 1000 / 60).toFixed(0)}분`;

const ratingChange = (bojId: string, rating: number, delta: number) => (
	`${bojId}: ${(rating).toFixed(0)} ⇒ ${(rating + delta).toFixed(0)} (${colorDelta(delta)})\n`
);

const resultMakgora = (
	userId: string,
	targetId: string,
	result: -1 | 0 | 1,
	delta: number,
	user: User,
	target: User,
) => {
	let output = "";
	if (result === 0) output += "막고라가 무승부로 끝났습니다.";
	else output += `<@${result === 1 ? userId : targetId}>의 승리! 축하합니다!`;
	output += ` <@${userId}>와 <@${targetId}>의 레이팅 변화는 다음과 같습니다.\n`;
	output += "```ansi\n";
	output += ratingChange(user.bojId, user.rating, delta);
	output += ratingChange(target.bojId, target.rating, -delta);
	output += "```";
	return output;
};

export default {
	command: "막고라",
	execute: async(message: Message, onCleanup: OnCleanup) => {
		// 메세지 파싱 후 사용자 데이터 가져오고 체크

		const { author, content } = message;
		const userId = author.id;
		const user = await getUser(userId);
		assert(user !== null, notRegisteredUser, userId);
		const userBojId = user.bojId;

		const args = content.split(" ").slice(1);

		let targetBojId = "";
		let query = `-@${userBojId}`;
		let timeout: number = DEFAULT_MAKGORA_TIMEOUT;
		let rated = true;
		for (const arg of args) {
			const optionPos = arg.indexOf("=");
			if (optionPos === -1) {
				if (targetBojId === "") {
					targetBojId = arg;
					if (arg[0] === "<" && arg[1] === "@" && arg[arg.length - 1] === ">") {
						// eslint-disable-next-line no-await-in-loop
						const targetUser = await getUser(arg.slice(2, -1));
						if (targetUser !== null) targetBojId = targetUser.bojId;
					}
					query = `-@${targetBojId} ${query}`;
				} else {
					// eslint-disable-next-line no-await-in-loop
					query += ` ${await transformPresetQuery(userId, arg)}`;
				}
			} else {
				const type = arg.slice(0, optionPos);
				const value = arg.slice(optionPos + 1);
				if (type === "t") {
					timeout = Number(value) * 60 * 1000;
				} else if (type === "r" && value !== "1") {
					rated = false;
				}
			}
		}

		assert(targetBojId !== "", usage);
		assert(targetBojId !== userBojId, sameUser);

		const target = await getUserByBojId(targetBojId);
		assert(target !== null, notRegisteredTarget, targetBojId);
		const targetId = target.id;

		assert(!getActive(userId), userAlreadyActive);
		assert(!getActive(targetId), targetAlreadyActive);


		// 사용자 반응 확인 및 문제 가져오기

		await setActive([userId, targetId]);
		onCleanup(() => setActive([userId, targetId], false));

		const checkingMessage = await message.reply(checkMakgora(query, timeout, rated, targetId, targetBojId));
		await checkingMessage.react("✅");
		await checkingMessage.react("❌");

		const reactions = await getReactions(checkingMessage, REACTION_TIMEOUT, {
			"✅": [targetId],
			"❌": [userId, targetId],
		});
		const reaction = reactions.first();
		checkingMessage.reactions.removeAll();
		assert(reaction !== undefined, reactionTimedOut);
		assert(reaction.emoji.name !== "❌", cancelled);

		const problems = await getRandomProblems(query);
		assert(problems.length > 0, notFound);
		const { titleKo, problemId } = problems[0];

		const startingMessage = await message.channel.send(startMakgora(userId, targetId, titleKo, problemId));


		// 막고라 시작
		// 남은 시간 업데이트, 무승부 확인, 컷 확인을 병렬로 실행

		const startTime = Date.now();
		const endTime = startTime + timeout;

		const timerMessage = await sendTimer(message, remainTime, endTime - Date.now(), onCleanup);

		const tiePromise = getReactions(
			timerMessage,
			endTime - Date.now(),
			{ "🛑": [userId, targetId] },
			2,
		).then(() => 0 as const);

		const userSurrenderPromise = getReactions(
			timerMessage,
			endTime - Date.now(),
			{ "🏳️": [userId] },
		).then(() => -1 as const);

		const targetSurrenderPromise = getReactions(
			timerMessage,
			endTime - Date.now(),
			{ "🏳️": [targetId] },
		).then(() => 1 as const);

		const winPromise = getTwoStepCommands(
			message,
			endTime - Date.now(),
			{ "!컷": [userId, targetId] },
			onCleanup,
			async() => {
				const [userResult, targetResult] = await Promise.all([
					getAcceptedSubmission(userBojId, problemId),
					getAcceptedSubmission(targetBojId, problemId),
				]);
				if (userResult < targetResult) return 1;
				if (userResult > targetResult) return -1;
				message.channel.send(noSolver);
			},
			0 as const,
		);

		// 결과 반영
		const result = await Promise.race([tiePromise, winPromise, userSurrenderPromise, targetSurrenderPromise]);
		const eloResult = result === 1 ? 1 : result === -1 ? 0 : 0.5;
		const delta = eloDelta(user.rating, target.rating, eloResult);

		startingMessage.reply(resultMakgora(userId, targetId, result, delta, user, target));
		await addMakgora(user, target, result, startTime, rated, delta, timeout, problemId, query);
	},
};
