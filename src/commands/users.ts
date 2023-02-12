import { Message } from "discord.js";

import { getUserBojIds } from "./user";

export default {
	command: "유저",
	execute: async(message: Message) => {
		const bojIdList = getUserBojIds().join(" ");
		let output = "등록된 유저 목록입니다.\n";
		output += `\`\`\`ansi\n${bojIdList}\n\`\`\``;

		await message.reply(output);
	},
};
