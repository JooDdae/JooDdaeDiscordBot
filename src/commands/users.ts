import { Message } from "discord.js";

import { getUserBojIds } from "./user";

export default {
	command: "멤버",
	execute: async(message: Message) => {
		const bojIdList = getUserBojIds().join(" ");
		let output = "등록된 멤버 목록입니다.\n";
		output += `\`\`\`ansi\n${bojIdList}\n\`\`\``;

		await message.reply(output);
	},
};
