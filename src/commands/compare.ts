/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { Message } from "discord.js";

import { assert, colorDelta, padCenter } from "../common";
import { getMatches, getUser, getUserByBojId } from "../io/db";

const usage = "`!상대전적 <상대의 BOJ ID>` 혹은 `!상대전적 <BOJ ID1> <BOJ ID2>` 로 상대전적을 확인할 수 있습니다.\n";

const sameUser = `같은 사람의 상대전적은 볼 수 없습니다.`;

const notRegistered = (id: string) => (
	`${id}님은 아직 봇에 등록하지 않았습니다. 봇에 등록된 사람 간의 상대전적만 조회할 수 있습니다.`
);

const notRegisteredBoj = (bojId: string) => (
	`${bojId}님은 아직 봇에 등록하지 않았습니다. 봇에 등록된 사람 간의 상대전적만 조회할 수 있습니다.`
);

const notFound = (bojId1: string, bojId2: string) => (
	`${bojId1} 님과 ${bojId2} 님 간의 전적이 존재하지 않습니다.`
);

const colorType = (result: number) => (result === 1 ? "\x1B[34mW" : result === -1 ? "\x1B[31mL" : "\x1B[33mT");

export default {
	command: "상대전적",
	execute: async(message: Message) => {
		const { author, content } = message;
		const args = content.split(" ").slice(1);
		assert(args.length === 1 || args.length === 2, usage);


		// 인자가 하나면 본인을 왼쪽 유저로 자동 선택

		let leftUser = null;
		let rightUser = null;
		if (args.length === 1) {
			const { id } = author;
			const rightBojId = args[0];

			leftUser = await getUser(id);
			assert(leftUser !== null, notRegistered, id);
			assert(leftUser.bojId !== rightBojId, sameUser);

			rightUser = await getUserByBojId(rightBojId);
			assert(rightUser !== null, notRegisteredBoj, rightBojId);
		} else {
			const [leftBojId, rightBojId] = args;
			assert(leftBojId !== rightBojId, sameUser);

			leftUser = await getUserByBojId(leftBojId);
			assert(leftUser !== null, notRegistered, leftBojId);

			rightUser = await getUserByBojId(rightBojId);
			assert(rightUser !== null, notRegisteredBoj, rightBojId);
		}


		// 둘이 모두 포함된 대결들을 가져와 레이팅 변화를 추적

		const id = leftUser.id;
		const targetId = rightUser.id;
		const matches = await getMatches(id, rightUser.id);
		assert(matches.length > 0, notFound, leftUser.bojId, rightUser.bojId);

		const lineLength = 50;
		let output = "";
		let winCount = 0;
		let loseCount = 0;
		let tieCount = 0;

		for (const {
			// type,
			authorId,
			// rated,
			// timeout,
			// ext,
			participants,
		} of matches) {
			const leftIsAuthor = id === authorId;
			const {
				result: leftResult,
				prevRating: leftRating,
				delta: leftDelta,
			} = participants.find(({ userId }) => userId === id)!;
			const {
				result: rightResult,
				prevRating: rightRating,
				delta: rightDelta,
			} = participants.find(({ userId }) => userId === targetId)!;

			winCount += Number(leftResult === 1);
			loseCount += Number(rightResult === 1);
			tieCount += Number(leftResult === 0);

			output += `${colorType(leftResult)}\x1B[0m ${leftRating} ⇒ ${leftRating + leftDelta} (${colorDelta(leftDelta)}) `;
			output += `${leftIsAuthor ? "=" : "<"}=💀=${leftIsAuthor ? ">" : "="}`;
			output += ` ${colorType(rightResult)}\x1B[0m ${rightRating} ⇒ ${rightRating + rightDelta} (${colorDelta(rightDelta)})\n`;
		}

		await message.reply(
			"```ansi\n\x1B[1m"
			+ `${padCenter(leftUser.bojId, lineLength >> 1)}${padCenter(rightUser.bojId, lineLength >> 1)}\n`
			+ `${padCenter(leftUser.rating, lineLength >> 1)}${padCenter(rightUser.rating, lineLength >> 1)}\n`
			+ `${winCount}승 ${tieCount}무 ${loseCount}패\x1B[0m\n`
			+ `\x1B[32m${"-".repeat(lineLength)}\x1B[1m\n${output}`
			+ "```",
		);
	},
};
