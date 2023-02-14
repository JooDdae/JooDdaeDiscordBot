import { basePresets } from "../base-presets";
import { getQueryAlias } from "../io/db";

export const transformPresetQuery = async(userId: string, query: string) => {
	if (query.length > 1 && (query[0] === "-" || query[0] === "!" || query[0] === "~")) {
		const alias = query.slice(1);
		if (basePresets[alias]) return basePresets[alias];
		const aliasQuery = await getQueryAlias(userId, alias);
		return aliasQuery !== null ? `-(${aliasQuery.query})` : query;
	}
	if (basePresets[query]) return basePresets[query];
	const aliasQuery = await getQueryAlias(userId, query);
	return aliasQuery !== null ? aliasQuery.query : query;
};
