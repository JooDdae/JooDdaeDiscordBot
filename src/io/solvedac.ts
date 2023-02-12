const headers = { "Content-Type": "application/json" };

export const getRandomProblems = async(query: string, count = 1) => {
	const url = `https://solved.ac/api/v3/search/problem?query=${encodeURIComponent(query)}&sort=random`;
	const res: any = await fetch(url, { headers }).then((res) => res.json());
	return res.items.slice(0, count);
};
