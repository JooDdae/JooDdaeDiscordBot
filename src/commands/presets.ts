import { Message } from "discord.js";

import { basePresets } from "../constants/base-presets";
import {
	QueryPreset,
	addQueryPreset,
	deleteQueryPreset,
	editQueryPreset,
	getQueryPreset,
	getQueryPresets,
	getUser,
} from "../io/db";
import { assert, transformQueries } from "../common";

const usage = "쿼리에 프리셋을 추가하여 입력에 사용할 수 있습니다. 등록된 프리셋은 남들과 공유하지 않습니다.\n"
			+ "`!프리셋 추가`, `!프리셋 제거`, `!프리셋 변경`, `!프리셋 목록`으로 각 기능의 자세한 설명을 볼 수 있습니다.";

const usageAdd = "`!프리셋 추가 <프리셋 이름> <쿼리>`로 프리셋을 추가할 수 있습니다.\n";

const usageDelete = "`!프리셋 제거 <프리셋 이름>`으로 프리셋을 제거할 수 있습니다.";

const usageEdit = "`!프리셋 변경 <프리셋 이름> <쿼리>`로 추가된 프리셋을 변경할 수 있습니다.";

const usageList = "`!프리셋 목록`으로 봇에 등록된 프리셋을 확인할 수 있습니다.";

const notRegisteredUser = (userId: string) => (
	`<@${userId}>님은 아직 봇에 등록하지 않았습니다. \`!등록 <백준 아이디>\` 명령어로 등록해주세요.`
);

const isBasePreset = (presetName: string) => (
	`\`${presetName}\`은 이미 \`${basePresets[presetName]}\`로 등록되어 있으며, 봇에서 제공하는 기본 프리셋이므로 변경이 불가능합니다.`
);


const invalidPreset = `프리셋은 한글 혹은 영어로만 이루어져야 합니다.`;

const presetAlreadyExist = (presetName: string, { query }: QueryPreset) => (
	`프리셋 \`${presetName}\`은 이미 \`${query}\`로 등록되어 있습니다. 변경을 원하실 경우, \`!프리셋 변경\`으로 다시 시도해 주세요.`
);


const presetNotFound = (presetName: string) => (
	`프리셋 \`${presetName}\`을 찾을 수 없습니다. \`!프리셋 목록\`으로 등록된 프리셋을 확인해주세요.`
);


const noPreset = (id: string) => (
	`<@${id}>님에게 등록된 프리셋이 없습니다. \`!프리셋 추가\`로 프리셋을 추가해주세요.`
);


const addSuccess = (presetName: string, query: string) => (
	`프리셋 \`${presetName}\`을 \`${query}\`로 추가했습니다.`
);

const deleteSuccess = (presetName: string) => (
	`프리셋 \`${presetName}\`을 제거했습니다.`
);

const editSuccess = (presetName: string, prevQuery: string, query: string) => (
	`프리셋 \`${presetName}\`을 \`${prevQuery}\`에서 \`${query}\`로 변경했습니다.`
);

const ALPHABET_HANGUL_REGEX = /^[a-zA-Z가-힣]+$/;

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

			const presetName = args[1];
			assert(!(presetName in basePresets), isBasePreset(presetName));
			assert(ALPHABET_HANGUL_REGEX.test(presetName), invalidPreset);

			const query = (await transformQueries(id, args.slice(2))).join(" ");
			const preset = await getQueryPreset(id, presetName);
			assert(preset === null, presetAlreadyExist, presetName, preset!);

			await addQueryPreset(id, presetName, query);
			await message.reply(addSuccess(presetName, query));
		} else if (command === "제거") {
			assert(args.length === 2, usageDelete);

			const presetName = args[1];
			assert(!(presetName in basePresets), isBasePreset(presetName));

			const preset = await getQueryPreset(id, presetName);
			assert(preset !== null, presetNotFound(presetName));

			await deleteQueryPreset(id, presetName);
			await message.reply(deleteSuccess(presetName));
		} else if (command === "변경") {
			assert(args.length >= 3, usageEdit);

			const presetName = args[1];
			assert(!(presetName in basePresets), isBasePreset(presetName));

			const preset = await getQueryPreset(id, presetName);
			assert(preset !== null, presetNotFound(presetName));
			const { query: prevQuery } = preset;

			const newQuery = (await transformQueries(id, args.slice(2))).join(" ");
			await editQueryPreset(id, presetName, newQuery);
			await message.reply(editSuccess(presetName, prevQuery, newQuery));
		} else if (command === "목록") {
			assert(args.length === 1, usageList);

			const presets = await getQueryPresets(id);
			assert(presets.length > 0, noPreset(id));

			let output = `<@${id}>님의 프리셋 목록입니다.\n\`\`\`ansi\n`;
			for (const { name, query } of presets) output += `${name} ⇒ ${query}\n`;
			output += "```";

			await message.reply(output);
		} else {
			assert(false, usage);
		}
	},
};
