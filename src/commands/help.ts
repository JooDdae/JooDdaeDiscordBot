import { Message } from "discord.js";

export default {
	command: "도움말",
	execute: async(message: Message) => {
		await message.reply(
			"각 명령어를 입력해 자세한 설명을 볼 수 있습니다.\n"
			+ "`!막고라` - 상대에게 막고라를 신청할 수 있습니다.\n"
			+ "`!등록` - 계정을 등록할 수 있습니다.\n"
			+ "`!유저` - 등록된 유저의 목록을 확인할 수 있습니다.\n"
			+ "`!상대전적` - 두 사람의 상대전적을 확인할 수 있습니다.\n"
			+ "`!프리셋` - 쿼리의 프리셋을 관리합니다.\n",
		);
	},
};
