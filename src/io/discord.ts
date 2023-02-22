/* eslint-disable no-await-in-loop */
/* eslint-disable no-unmodified-loop-condition */
import { AwaitMessagesOptions, Collection, Message, MessageReaction } from "discord.js";


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


export type ReactionCallback<T> = (reactions: Collection<string, MessageReaction>) => T;
export const reactionFilter = <T = Collection<string, MessageReaction>>(
	emoji: string,
	ids: string[],
	then?: T,
	maxUsers = 1,
) => ({
		type: "reaction" as const,
		emoji,
		ids,
		then: (
			typeof then === "function"
				? then
				: then === undefined
					? (x) => x
					: () => then
		) as (
			T extends ReactionCallback<unknown>
				? T
				: ReactionCallback<T>
		),
		maxUsers,
	});
export type ReactionFilter<T> = ReturnType<typeof reactionFilter<T>>;

export const messageFilter = <T, U = undefined>(
	prefix: string,
	ids: string[],
	then: (message: Message) => Promise<T>,
	fallback?: U,
) => ({
		type: "message" as const,
		prefix,
		ids,
		then,
		fallback: fallback as (U extends undefined ? undefined : Exclude<U, undefined>),
	});
export type MessageFilter<T, U> = ReturnType<typeof messageFilter<T, U>>;


export type Command<T, U> = ReactionFilter<T> | MessageFilter<T, U>;

export type CommandResult<T extends Command<unknown, unknown>> =
	| T extends ReactionFilter<unknown> ? ReturnType<T["then"]>
	: T extends MessageFilter<unknown, unknown> ? (Exclude<Awaited<ReturnType<T["then"]>>, undefined> | T["fallback"])
	: never;

export const getCommands = async<T extends Command<unknown, unknown>[]>(
	message: Message,
	time: number,
	...commands: T
): Promise<{ [K in keyof T]: CommandResult<T[K]> }[number]> => {
	let end = false;

	const promises = [];
	for (const command of commands) {
		if (command.type === "reaction") {
			const { emoji, ids, then, maxUsers } = command;

			await message.react(emoji);

			const reactionPromise = message.awaitReactions({
				filter: ({ emoji: { name } }, { id }) => name === emoji && ids.includes(id),
				maxUsers,
				time,
			});
			promises.push(reactionPromise.then((messages) => then(messages.clone())));
		} else if (command.type === "message") {
			const { prefix, ids, then, fallback } = command;

			const options: AwaitMessagesOptions = {
				filter: ({ content, author: { id } }: Message) => (
					content !== null
					&& content.startsWith(prefix)
					&& ids.includes(id)
				),
				max: 1,
				time,
			};

			const messagePromise = (async() => {
				const endTime = Date.now() + time;
				while (Date.now() < endTime && !end) {
					const messages = await message.channel.awaitMessages(options);
					const commandMessage = messages.first();
					if (commandMessage === undefined || end) break;

					const result = await then(commandMessage);
					if (result !== undefined) return result;
				}
				return fallback;
			})();
			promises.push(messagePromise);
		}
	}

	const result = await Promise.race<any>(promises);

	end = true;
	await message.reactions.removeAll();

	return result;
};
