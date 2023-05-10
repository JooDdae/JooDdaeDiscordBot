import { Message } from "discord.js";

import { assert } from "../common";
import { getRanking } from "../io/db";

const noRatedRecord = () => (
	`기록된 전적이 없어 랭킹을 출력할 수 없습니다.`
);

const pad = (x: number, n = 4) => x.toString().padStart(n);

export default {
	command: "랭킹",
	execute: async(message: Message) => {
		const ranking = await getRanking();
		assert(ranking.length > 0, noRatedRecord);

		let rank = 1;
		let index = 1;
		let prevRating = ranking[0].rating;
		const topRating = prevRating;

		let output = "```ansi\n\x1B[0;41m";
		for (const { rating, bojId, winCount, tieCount, loseCount } of ranking) {
			if (rating !== prevRating) rank = index;
			if (rating !== topRating) output += `\x1B[0m`;
			output += `${pad(rank, 2)} ${bojId.padEnd(15)} ${pad(rating)} ${pad(winCount)}승 ${pad(tieCount)}무 ${pad(loseCount)}패\n`;
			prevRating = rating;
			index += 1;
		}
		output += "```";

		await message.reply(output);
	},
};
