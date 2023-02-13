import { Message } from "discord.js";
import { getUserBojIds } from "../io/db";

const listUser = (ids: string[]) => (
	"등록된 유저 목록입니다.\n"
	+ "```ansi\n"
	+ `${ids.join(" ")}\n`
	+ "```"
);

export default {
	command: "유저",
	execute: async(message: Message) => {
		const users = await getUserBojIds();
		const ids = users.map(({ bojId }) => bojId);
		await message.reply(listUser(ids));
	},
};
