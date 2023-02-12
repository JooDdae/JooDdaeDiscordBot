import { Message } from "discord.js";

export default {
	command: "도움말",
	execute: async(message: Message) => {
		let output = "`!막고라신청` - 상대에게 막고라를 신청할 수 있습니다.\n";
		output += "`!등록` - 계정을 등록할 수 있습니다.\n";
		output += "`!멤버` - 등록된 멤버의 목록을 확인할 수 있습니다.\n";
		output += "`!상대전적` - 두 사람의 상대전적을 확인할 수 있습니다.\n";

		await message.reply(output);
	},
};
