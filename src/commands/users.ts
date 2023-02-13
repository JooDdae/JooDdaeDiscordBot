import { Message } from "discord.js";
import { getUserBojIds } from "../io/db";

export default {
	command: "유저",
	execute: async(message: Message) => {
		const bojIdList = await getUserBojIds();

		await message.reply(
			"등록된 유저 목록입니다.\n"
			+ "```ansi\n"
			+ `${bojIdList.join(" ")}\n`
			+ "```",
		);
	},
};
