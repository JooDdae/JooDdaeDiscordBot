import { Client, Events, GatewayIntentBits } from "discord.js";

import { DISCORD_TOKEN } from "./discord-token";
import { addUser } from "./commands/user";
import { changeMakgoraRating } from "./commands/makgora";
import commands from "./commands";
import { AlertMessage, Cleanup, OnCleanup } from "./common";
import { getMatchLog, getUserList } from "./io/fileio";

const client = new Client({
	intents: [
		GatewayIntentBits.DirectMessages,
		GatewayIntentBits.Guilds,
		GatewayIntentBits.GuildMessages,
		GatewayIntentBits.GuildMessageReactions,
		GatewayIntentBits.MessageContent,
	],
});

client.once(Events.ClientReady, (c) => {
	const userList = getUserList();
	const matchLog = getMatchLog();

	userList.forEach((user) => {
		const [id, bojId] = user;
		if (id !== "" && bojId !== "")
			addUser(id, bojId);
	});

	matchLog.forEach((match) => {
		const matchType = match[0];
		if (matchType !== "") {
			if (matchType === "makgora") {
				const [id1, id2, result, problem, time, startDatetime, query, timeout, rated] = match.slice(1);
				changeMakgoraRating(id1, id2, result, problem, time, startDatetime, query, timeout, rated);
			}
		}
	});

	console.log(`Ready! Logged in as ${c.user.tag}`);
});

client.on(Events.MessageCreate, async(message) => {
	const commandPrefix = "!";

	const { content } = message;
	if (!content.startsWith(commandPrefix)) return;
	const spacePos = content.indexOf(" ");
	const commandType = content.slice(commandPrefix.length, spacePos < 0 ? content.length : spacePos);

	const command = commands.get(commandType);
	if (command === undefined) return;

	const cleanups: Cleanup[] = [];
	const onCleanup: OnCleanup = (cleanup) => cleanups.push(cleanup);

	try {
		await command.execute(message, onCleanup);
	} catch (error) {
		if (error instanceof AlertMessage) {
			message.reply(error.message);
		} else {
			console.error(error);
			await message.reply({ content: "명령 실행 도중 오류가 발생했습니다!" });
		} /*
			else if (error instanceof FetchError) {
				message.(error.message);
				return;
			}
		*/
	}

	for (const cleanup of cleanups) cleanup();
});

client.login(DISCORD_TOKEN);
