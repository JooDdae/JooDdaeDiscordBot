/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { Message } from "discord.js";
import { randomBytes } from "crypto";

import { REGISTER_TIMEOUT } from "../constants";
import { OnCleanup, assert } from "../common";
import { addUser, getUser, getUserByBojId } from "../io/db";
import { existBojId, getSharedSource } from "../io/boj";

const usage = "`!등록 <BOJ ID>`으로 봇에 등록할 수 있습니다.";

const userAlreadyRegistered = (id: string, userBojId: string) => (
	`<@${id}>님은 \`${userBojId}\`로 이미 봇에 등록되어 있습니다.`
);

const bojIdAlreadyRegistered = (bojId: string) => (
	`\`${bojId}\`는 이미 봇에 등록된 BOJ ID입니다.`
);

const notFound = (bojId: string) => (
	`\`${bojId}\` 백준 아이디가 존재하지 않습니다.`
);

const remainTime = (remain: number) => `등록 제한시간: ${(remain / 60000).toFixed(0)}분`;

export default {
	command: "등록",
	execute: async(message: Message, onCleanup: OnCleanup) => {
		const { author, content } = message;
		const { id } = author;

		const args = content.split(" ").slice(1);
		assert(args.length === 1, usage);
		const bojId = args[0];

		{
			const user = await getUser(id);
			assert(user === null, userAlreadyRegistered, id, user!.bojId);
		}
		{
			const user = await getUserByBojId(bojId);
			assert(user === null, bojIdAlreadyRegistered, id);
		}
		assert(await existBojId(bojId), notFound, bojId);

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

		// 등록

		await addUser(id, bojId);
		await tokenMessage.reply(`<@${id}>님이 \`${bojId}\`로 봇에 등록되었습니다.`);
	},
};
