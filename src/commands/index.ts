import { Collection, Message } from "discord.js";

import { OnCleanup } from "../common";
import headtohead from "./headtohead";
import help from "./help";
import makgora from "./makgora";
import ranking from "./ranking";
import register from "./register";
import users from "./users";

export type Command = {
	command: string;
	execute: (message: Message, onCleanup: OnCleanup) => Promise<void>;
};

const commands = new Collection<string, Command>();

commands.set(headtohead.command, headtohead);
commands.set(help.command, help);
commands.set(users.command, users);
commands.set(ranking.command, ranking);
commands.set(makgora.command, makgora);
commands.set(register.command, register);

export default commands;
