import { Collection, Message } from "discord.js";

import { OnCleanup } from "../common";
import compare from "./compare";
import help from "./help";
import makgora from "./makgora";
import matches from "./matches";
import presets from "./presets";
import ranking from "./ranking";
import register from "./register";
import users from "./users";

export type Command = {
	command: string;
	execute: (message: Message, onCleanup: OnCleanup) => Promise<void>;
};

const commands = new Collection<string, Command>();

commands.set(compare.command, compare);
commands.set(help.command, help);
commands.set(users.command, users);
commands.set(ranking.command, ranking);
commands.set(makgora.command, makgora);
commands.set(register.command, register);
commands.set(presets.command, presets);
commands.set(matches.command, matches);

export default commands;
