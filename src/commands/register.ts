import { Message } from "discord.js";

import { REGISTER_TIMEOUT } from "../constants";
import { assert } from "../common";
import { saveUser } from "../io/fileio";
import { undefinedBoj } from "../io";
import { addUser, getBojId, getDiscordId } from "./user";

const usage = "`!등록 <BOJ ID>` 봇에 등록할 수 있습니다.";

const registeredDiscordUser = (id: string, userBojId: string) => (
	`<@${id}>님은 \`${userBojId}\`로 이미 봇에 등록되어 있습니다.`
);

const registeredBojId = (bojId: string) => (
	`\`${bojId}\`는 이미 봇에 등록된 BOJ ID입니다.`
);

const undefinedBojId = (bojId: string) => (
	`\`${bojId}\` 백준 아이디가 존재하지 않습니다.`
);

const remainTime = (remain: number) => `등록 마감까지 남은 시간: ${(remain / 1000 / 60).toFixed(0)}분`;

export default {
	command: "등록",
	execute: async(message: Message) => {
		const { author, content } = message;
		const id = author.id;

		const args = content.split(" ").slice(1);
		assert(args.length === 1, usage);

		const userBojId = getBojId(id);
		assert(userBojId === undefined, registeredDiscordUser, id, userBojId as string);

		const bojId = args[0];
		const registeredId = getDiscordId(bojId);
		assert(registeredId === undefined, registeredBojId, bojId);
		assert(undefinedBoj(bojId), undefinedBojId, bojId);

		const registerToken = `사랑해요 주때봇`;
		const startTime = Date.now();
		const endTime = startTime + REGISTER_TIMEOUT;

		const tokenMessage = await message.reply(`\`${bojId}\`로 봇에 등록하시려면 \`${registerToken}\`를 임의의 문제에 제출하고, 해당 코드를 공유한 주소를 입력해주세요.`);
		const remainMessage = await message.channel.send(remainTime(endTime - Date.now()));

		// 병렬 실행

		addUser(id, bojId);
		saveUser(id, bojId);
		await tokenMessage.reply(`<@${id}>님이 \`${bojId}\`로 봇에 등록되었습니다.`);
	},
};
