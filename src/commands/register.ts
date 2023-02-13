import { Message } from "discord.js";
import { randomBytes } from "crypto";

import { REGISTER_TIMEOUT } from "../constants";
import { saveUser } from "../io/fileio";
import { OnCleanup, assert } from "../common";
import { addUser, getBojId, getDiscordId } from "./user";
import { existBojId, getSharedSource } from "../io/boj";

const usage = "`!등록 <BOJ ID>`으로 봇에 등록할 수 있습니다.";

const registeredDiscordUser = (id: string, userBojId: string) => (
	`<@${id}>님은 \`${userBojId}\`로 이미 봇에 등록되어 있습니다.`
);

const registeredBojId = (bojId: string) => (
	`\`${bojId}\`는 이미 봇에 등록된 BOJ ID입니다.`
);

const undefinedBojId = (bojId: string) => (
	`\`${bojId}\` 백준 아이디가 존재하지 않습니다.`
);

const remainTime = (remain: number) => `등록 취소까지 남은 시간: ${(remain / 1000 / 60).toFixed(0)}분`;

export default {
	command: "등록",
	execute: async(message: Message, onCleanup: OnCleanup) => {
		const { author, content } = message;
		const id = author.id;

		const args = content.split(" ").slice(1);
		assert(args.length === 1, usage);

		const userBojId = getBojId(id);
		assert(userBojId === undefined, registeredDiscordUser, id, userBojId as string);

		const bojId = args[0];
		const registeredId = getDiscordId(bojId);
		assert(registeredId === undefined, registeredBojId, bojId);
		assert(existBojId(bojId), undefinedBojId, bojId);

		const registerToken = `사랑해요 주때봇 ${randomBytes(16).toString("hex")}`;
		const token = await message.channel.send(`\`${registerToken}\``);
		const tokenMessage = await token.reply(`<@${id}>님, \`${bojId}\`로 봇에 등록하시려면 위 문구를 임의의 문제에 제출하고, 해당 코드를 공유한 주소를 입력해주세요.\n등록을 취소하려면 ❌ 이모지를 달아주세요.`);


		// 병렬 실행
		const startTime = Date.now();
		const endTime = startTime + REGISTER_TIMEOUT;

		const remainMessage = await message.channel.send(remainTime(endTime - Date.now()));
		const updateRemain = () => {
			const { content } = remainMessage;
			const newContent = remainTime(endTime - Date.now());
			if (content !== newContent) remainMessage.edit(newContent);
		};

		const timer = setInterval(updateRemain, 1000);
		onCleanup(() => clearInterval(timer));

		let end = false;
		onCleanup(() => (end = true));

		await remainMessage.react("❌");
		const cancelPromise = remainMessage.awaitReactions({
			filter: ({ emoji: { name } }, { id }) => name === "❌" && id === author.id,
			max: 1,
			time: endTime - Date.now(),
		}).then(() => false);

		const registerPromise = (async() => {
			while (Date.now() < endTime) {
				// eslint-disable-next-line no-await-in-loop
				const replyMessage = await message.channel.awaitMessages({
					filter: ({ content, author: { id } }) => content.startsWith("http") && id === author.id,
					max: 1,
					time: endTime - Date.now(),
				});
				if (end) break;
				const sourceMessage = replyMessage.first();
				// eslint-disable-next-line no-await-in-loop
				const input = await getSharedSource(sourceMessage?.content);
				if (input !== undefined && input[0] === bojId && input[1] === registerToken) return true;
				if (sourceMessage !== undefined)
					sourceMessage.reply("잘못된 링크입니다. 다시 입력해주세요.");
			}
			return false;
		})();

		const result = await Promise.race([cancelPromise, registerPromise]);
		if (!result) {
			await tokenMessage.reply("등록이 취소되었습니다.");
			return;
		}

		addUser(id, bojId);
		saveUser(id, bojId);
		await tokenMessage.reply(`<@${id}>님이 \`${bojId}\`로 봇에 등록되었습니다.`);
	},
};
