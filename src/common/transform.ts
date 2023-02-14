import { getQueryAlias } from "../io/db";

export const transformPresetQuery = async(userId: string, query: string) => {
	if (query.length > 1 && (query[0] === "-" || query[0] === "!" || query[0] === "~")) {
		const alias = query.slice(1);
		const aliasQuery = await getQueryAlias(userId, alias);
		return aliasQuery !== null ? `-(${aliasQuery.query})` : query;
	}
	const aliasQuery = await getQueryAlias(userId, query);
	return aliasQuery !== null ? aliasQuery.query : query;
};
