import { Message } from "discord.js";

import { assert } from "../common";
import { UserInfo, getUsers } from "./user";

const noRatedRecord = () => (
	`기록된 전적이 없어 랭킹을 출력할 수 없습니다.`
);

export default {
	command: "랭킹",
	execute: async(message: Message) => {
		const ranking: UserInfo[] = [];

		const userList = getUsers();
		for (const user of userList)
			if (user.count[-1] + user.count[0] + user.count[1] > 0)
				ranking.push(user);
		assert(ranking.length > 0, noRatedRecord);

		ranking.sort((a: UserInfo, b: UserInfo) => a.rating - b.rating);

		let rank = 1;
		let prevUser = ranking[0];
		const topRating = prevUser.rating;
		let output = "```ansi\n\x1B[0;41m";

		for (const { index, user } of ranking.map((user, index) => ({
			index,
			user,
		}))) {
			if (user.rating !== prevUser.rating)
				rank = index + 1;

			if (user.rating !== topRating)
				output += `\x1B[0m`;

			output += `${rank} ${user.bojId.padEnd(15)} ${user.rating.toFixed(0).toString()
				.padStart(4)} ${user.count[1].toString().padStart(4)}승 ${user.count[0].toString().padStart(4)}무 ${user.count[-1].toString().padStart(4)}패\n`;
			prevUser = user;
		}
		output += "```";

		await message.reply(output);
	},
};
