import { Message } from "discord.js";

import { basePresets } from "../base-presets";
import { addQueryAlias, deleteQueryAlias, editQueryAlias, getQueryAlias, getQueryAliases, getUser } from "../io/db";
import { assert, transformPresetQuery } from "../common";

const usage = "쿼리에 프리셋을 추가하여 입력에 사용할 수 있습니다. 등록된 프리셋은 남들과 공유하지 않습니다.\n"
			+ "`!프리셋 추가`, `!프리셋 제거`, `!프리셋 변경`, `!프리셋 목록`으로 각 기능의 자세한 설명을 볼 수 있습니다.";

const usageAdd = "`!프리셋 추가 <프리셋 이름> <query>`으로 프리셋을 추가할 수 있습니다.\n";

const usageDelete = "`!프리셋 삭제 <프리셋 이름>`으로 프리셋을 삭제할 수 있습니다.";

const usageEdit = "`!프리셋 변경 <프리셋 이름> <query>`으로 추가된 프리셋을 변경할 수 있습니다.";

const usageList = "`!프리셋 목록`으로 봇에 등록된 프리셋을 확인할 수 있습니다.";

const notRegisteredUser = (userId: string) => (
	`<@${userId}>님은 아직 봇에 등록하지 않았습니다. \`!등록 <백준 아이디>\` 명령어로 등록해주세요.`
);

const isBasePreset = (alias: string, query: string) => (
	`\`${alias}\`은 기본 프리셋으로 \`${query}\`가 설정되어 변경이 불가능합니다.`
);


const invalidAlias = `프리셋은 한글 혹은 영어로만 이루어져야 합니다.`;

const aliasAlreadyExist = (alias: string, query: string) => (
	`프리셋 \`${alias}\`은 \`${query}\`로 이미 등록되어 있습니다.`
);


const aliasNotFound = (alias: string) => (
	`프리셋 \`${alias}\`을 찾을 수 없습니다. \`!프리셋 목록\`으로 등록된 프리셋을 확인해주세요.`
);


const noAlias = (id: string) => (
	`<@${id}>님에게 등록된 프리셋이 없습니다. \`!프리셋 추가\`로 프리셋을 추가해주세요.`
);


const addSuccess = (alias: string, query: string) => (
	`프리셋 \`${alias}\`을 \`${query}\`로 추가했습니다.`
);

const deleteSuccess = (alias: string) => (
	`프리셋 \`${alias}\`을 제거했습니다.`
);

const editSuccess = (alias: string, beforeQuery: string, query: string) => (
	`프리셋 \`${alias}\`을 \`${beforeQuery}\`에서 \`${query}\`로 변경했습니다.`
);

export default {
	command: "프리셋",
	execute: async(message: Message) => {
		const { author, content } = message;
		const { id } = author;

		const user = await getUser(id);
		assert(user !== null, notRegisteredUser, id);

		const args = content.split(" ").slice(1);
		const command = args[0];

		if (command === "추가") {
			assert(args.length >= 3, usageAdd);
			const alias = args[1];
			assert(!basePresets[alias], isBasePreset(alias, basePresets[alias]));

			let query = "";
			for (const arg of args.slice(2)) {
				// eslint-disable-next-line no-await-in-loop
				query += `${query === "" ? "" : " "}${await transformPresetQuery(id, arg)}`;
			}

			const regex = /^[a-zA-Z가-힣]+$/;
			assert(regex.test(alias), invalidAlias);
			const existQuery = await getQueryAlias(id, alias);
			assert(existQuery === null, aliasAlreadyExist(alias, existQuery?.query as string));
			await addQueryAlias(id, alias, query);

			await message.reply(addSuccess(alias, query));
		} else if (command === "제거") {
			const args = content.split(" ").slice(2);
			assert(args.length === 1, usageDelete);
			const alias = args[0];
			assert(!basePresets[alias], isBasePreset(alias, basePresets[alias]));

			const existQuery = await getQueryAlias(id, alias);
			assert(existQuery !== null, aliasNotFound(alias));
			await deleteQueryAlias(id, alias);

			await message.reply(deleteSuccess(alias));
		} else if (command === "변경") {
			const args = content.split(" ").slice(2);
			assert(args.length >= 2, usageEdit);
			const alias = args[0];
			assert(!basePresets[alias], isBasePreset(alias, basePresets[alias]));

			const existQuery = await getQueryAlias(id, alias);
			assert(existQuery !== null, aliasNotFound(alias));

			let query = "";
			for (const arg of args.slice(1)) {
				// eslint-disable-next-line no-await-in-loop
				query += `${query === "" ? "" : " "}${await transformPresetQuery(id, arg)}`;
			}

			const beforeQuery = existQuery.query;
			await editQueryAlias(id, alias, query);

			await message.reply(editSuccess(alias, beforeQuery, query));
		} else if (command === "목록") {
			const args = content.split(" ").slice(2);
			assert(args.length === 0, usageList);
			const aliases = await getQueryAliases(id);
			assert(aliases.length !== 0, noAlias(id));

			let output = `<@${id}>님의 프리셋 목록입니다.\n\`\`\`ansi\n`;
			for (const { alias, query } of aliases) {
				output += `${alias} ⇒ ${query}\n`;
			}
			output += "```";
			await message.reply(output);
		} else {
			assert(false, usage);
		}
	},
};
