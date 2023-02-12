import { Message } from "discord.js";

import { getHeadToHeadRecord } from "./record";
import { assert, colorDelta } from "../common";
import { getBojId, getBojUser } from "./user";

const usage = "`!상대전적 <상대의 BOJ ID>` 혹은 `!상대전적 <BOJ ID1> <BOJ ID2>` 로 상대전적을 확인할 수 있습니다.\n";

const notRegisteredUser = (userId: string) => (
	`<@${userId}>님은 아직 봇에 등록하지 않았습니다. \`!등록 <백준 아이디>\` 명령어로 등록해주세요.`
);

const notRegisteredBoj = (bojId: string) => (
	`${bojId}님은 아직 봇에 등록하지 않았습니다. 봇에 등록된 사람의 상대전적만 조회할 수 있습니다.`
);

const noRatedRecord = (bojId1: string, bojId2: string) => (
	`${bojId1}와 ${bojId2}의 전적을 찾을 수 없어 취소되었습니다.`
);

export default {
	command: "상대전적",
	execute: async(message: Message) => {
		const { author, content } = message;
		const userId = author.id;
		const userBojId = getBojId(userId);
		assert(userBojId !== undefined, notRegisteredUser, userId);

		const args = content.split(" ").slice(1);
		assert(args.length === 1 || args.length === 2, usage);

		const [bojId1, bojId2] = args.length === 1 ? [userBojId, args[0]] : args;
		const [user1, user2] = [getBojUser(bojId1), getBojUser(bojId2)];
		assert(user1 !== undefined, notRegisteredBoj, bojId1);
		assert(user2 !== undefined, notRegisteredBoj, bojId2);

		const recordList = getHeadToHeadRecord(user1.bojId, user2.bojId);
		assert(recordList !== undefined, noRatedRecord, user1.bojId, user2.bojId);

		const lineLength = 50;
		let output = "```ansi\n\x1B[0;41m";
		output += `${bojId1} ${bojId2}\n`;
		output += `${user1.rating} ${user2.rating}\n`;

		let output2 = `\x1B[32m${"-".repeat(lineLength)}\x1B[1m\n`;
		let winCount = 0;
		let loseCount = 0;
		let tieCount = 0;

		for (const record of recordList) {
			const isChallenger = record.challenger.bojId === bojId1;
			const isWinner = (isChallenger && record.result === "win") || (!isChallenger && record.result === "lose");
			winCount += isWinner ? 1 : 0;
			loseCount += !isWinner ? 1 : 0;
			tieCount += record.result === "tie" ? 1 : 0;

			const user1Delta = isChallenger ? record.delta : -record.delta;
			const user2Delta = isChallenger ? -record.delta : record.delta;
			const user1Rating = isChallenger ? record.challenger.rating : record.challenged.rating;
			const user2Rating = isChallenger ? record.challenged.rating : record.challenger.rating;

			const emoji = "💀";
			// let emoji = getEmoji(record.matchType);
			// if (emoji === null) {
			//     emoji = "?";
			// }

			output2 += `  ${record.result === "tie" ? "\x1B[33mT" : isWinner ? "\x1B[34mW" : "\x1B[31mL"}\x1B[0m ${user1Rating} ⇒ ${user1Rating + user1Delta} (${colorDelta(user1Delta)})\n`;
			output2 += isChallenger ? "==" : "<=";
			output2 += emoji;
			output2 += isChallenger ? "=>" : "==";
			output2 += `  ${record.result === "tie" ? "\x1B[33mT" : isWinner ? "\x1B[31mL" : "\x1B[34mW"}\x1B[0m ${user2Rating} ⇒ ${user2Rating + user2Delta} (${colorDelta(user2Delta)})\n`;
		}

		output += `${winCount}승 ${tieCount}무 ${loseCount}패\x1B[0m\n`;
		output += output2;
		output += "```";

		await message.reply(output);
	},
};
