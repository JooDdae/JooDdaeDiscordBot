/* eslint-disable no-unmodified-loop-condition */
import { Message } from "discord.js";


export const getReactions = async(
	message: Message,
	time: number,
	emojis: Record<string, string[]>,
	maxUsers = 1,
) => {
	// eslint-disable-next-line no-await-in-loop
	for (const emoji of Object.keys(emojis)) await message.react(emoji);

	const reactions = await message.awaitReactions({
		filter: ({ emoji: { name } }, { id }) => {
			if (name === null) return false;
			const ids = emojis[name];
			return ids !== undefined && ids.includes(id);
		},
		maxUsers,
		time,
	});

	await message.reactions.removeAll();

	return reactions;
};

export const getCommands = async(
	{ channel }: Message,
	time: number,
	commands: Record<string, string[]>,
	max = 1,
) => {
	const messages = await channel.awaitMessages({
		filter: ({ content, author: { id } }) => {
			if (content === null || content.length === 0) return false;
			const key = Object.keys(commands).find((command) => content.startsWith(command));
			return key !== undefined && commands[key].includes(id);
		},
		max,
		time,
	});

	return messages;
};

export const getTwoStepCommands = async<T, U = void>(
	message: Message,
	time: number,
	commands: Record<string, string[]>,
	onCleanup: (cleanup: () => void) => void,
	callback: (message: Message) => Promise<T>,
	fallbackValue: U,
) => {
	let end = false;
	onCleanup(() => (end = true));
	const endTime = Date.now() + time;
	while (Date.now() < endTime && !end) {
		// eslint-disable-next-line no-await-in-loop
		const command = (await getCommands(message, endTime - Date.now(), commands)).first();
		if (command === undefined || end) break;
		// eslint-disable-next-line no-await-in-loop
		const result = await callback(command);
		if (result !== undefined) return result;
	}
	return fallbackValue;
};

export const sendTimer = async(
	{ channel }: Message,
	timer: (remainTime: number) => string,
	time: number,
	onCleanup: (cleanup: () => void) => void,
	interval = 1000,
) => {
	const endTime = Date.now() + time;
	const timerMessage = await channel.send(timer(endTime - Date.now()));

	const intervalId = setInterval(() => {
		const { content } = timerMessage;
		const newContent = timer(endTime - Date.now());
		if (content !== newContent) timerMessage.edit(newContent);
	}, interval);
	onCleanup(() => clearInterval(intervalId));

	return timerMessage;
};
