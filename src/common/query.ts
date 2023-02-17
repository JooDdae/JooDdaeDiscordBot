import { getPresetQueryTable } from "../io/db";

export const transformQuery = (query: string, presetQueries: Record<string, string>) => {
	const neg = query.length > 1 && "-!~".includes(query[0]);
	const name = query.slice(neg ? 1 : 0);
	const result = presetQueries[name];
	if (result === undefined) return query;
	return neg ? `-(${result})` : result;
};

export const transformQueries = async(id: string, queries: string[]) => {
	const presetQueries = await getPresetQueryTable(id);
	return queries.map((query) => transformQuery(query, presetQueries));
};
