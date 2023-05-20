import { Message } from "discord.js";

import { assert } from "../common";
import { getRanking } from "../io/db";

const usage = "`!랭킹 [p=1] 로 랭킹을 볼 수 있습니다.\n"
		+ "`p`은 비필수 옵션으로 `페이지`를 의미합니다. \n"
		+ "예시: `!랭킹`, `!랭킹 2`\n";

const noRatedRecord = () => (
	`기록된 전적이 없어 랭킹을 출력할 수 없습니다.`
);

const pad = (x: number, n = 4) => x.toFixed(0).padStart(n);

export default {
	command: "랭킹",
	execute: async(message: Message) => {
		const { content } = message;
		const args = content.split(" ").slice(1);
		assert(args.length <= 1, usage);

		const page = args.length === 1 ? Math.max(Number(args[0]) | 0, 1) : 1;

		const ranking = await getRanking(page * 10);
		assert(ranking.length > 0, noRatedRecord);

		let rank = page * 10 + 1;
		let index = page * 10 + 1;
		let prevRating = ranking[0].rating;
		const topRating = prevRating;

		let output = "```ansi\n\x1B[0;41m";
		for (const { rating, bojId, winCount, tieCount, loseCount } of ranking) {
			if (rating !== prevRating) rank = index;
			if (rating !== topRating) output += `\x1B[0m`;
			// TODO: rank >= 100
			output += `${pad(rank, 2)} ${bojId.padEnd(15)} ${pad(rating)} ${pad(winCount)}승 ${pad(tieCount)}무 ${pad(loseCount)}패\n`;
			prevRating = rating;
			index += 1;
		}
		output += "```";

		await message.reply(output);
	},
};
