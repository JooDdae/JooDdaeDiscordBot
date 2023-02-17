import { basePresets } from "../base-presets";
import { getQueryPreset } from "../io/db";

export const transformQueryPreset = async(userId: string, query: string) => {
	const neg = query.length > 1 && "-!~".includes(query[0]);
	const name = query.slice(neg ? 1 : 0);

	const basePreset = basePresets[name];
	if (basePreset !== undefined) return basePreset;

	const preset = await getQueryPreset(userId, query);
	if ()
	return preset !== null ? preset.query : query;
};
