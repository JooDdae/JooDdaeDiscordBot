/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { Message } from "discord.js";

import { assert, colorDelta, maxPadding } from "../common";
import { getMatches, getUser, getUserByBojId } from "../io/db";

const usage = "`!전적` 혹은 `!전적 <BOJ ID>` 로 전적을 확인할 수 있습니다.\n";

const notRegistered = (id: string) => (
	`${id}님은 아직 봇에 등록하지 않았습니다. 봇에 등록된 사람 간의 상대전적만 조회할 수 있습니다.`
);

const notFound = (bojId: string) => (
	`${bojId} 님의 전적이 존재하지 않습니다. 다른 사람과 막고라를 뜬 후 다시 조회해 주세요.`
);

const colorType = (result: number) => (result === 1 ? "\x1B[34mW" : result === -1 ? "\x1B[31mL" : "\x1B[33mT");

export default {
	command: "전적",
	execute: async(message: Message) => {
		const { author, content } = message;
		const args = content.split(" ").slice(1);
		assert(args.length === 0 || args.length === 1, usage);


		let id = author.id;
		let user = null;
		if (args.length === 0) {
			user = await getUser(id);
		} else if (args.length === 1) {
			user = await getUserByBojId(args[0]);
			assert(user !== null, notRegistered, args[0]);
			id = user.id;
		}
		assert(user !== null, notRegistered, id);


		// 둘이 모두 포함된 대결들을 가져와 레이팅 변화를 추적

		const { bojId, rating, winCount, tieCount, loseCount } = user;
		const matches = await getMatches(id);
		assert(matches.length > 0, notFound, bojId);

		const lineLength = 50;
		const [paddingL, paddingR] = maxPadding(matches.map(({ participants }) => participants), id);
		let output = "";

		for (const {
			// type,
			authorId,
			// rated,
			// timeout,
			ext,
			participants,
		} of matches) {
			const leftIsAuthor = id === authorId;
			const {
				result: leftResult,
				prevRating: leftRating,
				newRating: leftNewRating,
			} = participants.find(({ userId }) => userId === id)!;
			const {
				user: { bojId: targetId },
				result: rightResult,
				prevRating: rightRating,
				newRating: rightNewRating,
			} = participants.find(({ userId }) => userId !== id)!;

			output += `${colorType(leftResult)}\x1B[0m ${leftRating.toFixed(0)} ⇒ ${leftNewRating.toFixed(0)} (${colorDelta(leftNewRating - leftRating, paddingL)}) `;
			output += ` ${leftIsAuthor ? "=" : "<"}=💀=${leftIsAuthor ? ">" : "="} `;
			output += ` ${colorType(rightResult)}\x1B[0m ${rightRating.toFixed(0)} ⇒ ${rightNewRating.toFixed(0)} (${colorDelta(rightNewRating - rightRating, paddingR)})   ${targetId.padEnd(14)}`;

			try {
				const { problemId } = JSON.parse(ext);
				output += `  [${problemId}]\n`;
			} catch {
				output += "\n";
			}
		}

		await message.reply(
			"```ansi\n\x1B[1m"
			+ `${bojId}: ${rating.toFixed(0)} / ${winCount}승 ${tieCount}무 ${loseCount}패\x1B[0m\n`
			+ `\x1B[32m${"-".repeat(lineLength)}\x1B[1m\n${output}`
			+ "```",
		);
	},
};
