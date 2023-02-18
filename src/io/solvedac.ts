const headers = { "Content-Type": "application/json" };

const ID = /^[0-9a-z_]{3,20}$/;

export type SolvedacOrganization = {
	organizationId: number;
	name: string;
	type: "community" | "university" | "company" | "high_school";
	rating: number;
	userCount: number;
	voteCount: number;
	solvedCount: number;
	color: string;
};

export type SolvedacBadge = {
	badgeId: string;
	badgeImageUrl: string;
	displayName: string;
	displayDescription: string;
};

export type SolvedacBackground = {
	backgroundId: string;
	backgroundImageUrl: string;
	author: string;
	authorUrl: string;
	displayName: string;
	displayDescription: string;
};

export type SolvedacUser = {
	handle: string;
	bio: string;
	organizations: SolvedacOrganization[];
	badge: SolvedacBadge;
	background: SolvedacBackground;
	profileImageUrl: string;
	solvedCount: number;
	voteCount: number;
	exp: number;
	tier: number;
	rating: number;
	ratingByProblemsSum: number;
	ratingByClass: number;
	ratingBySolvedCount: number;
	ratingByVoteCount: number;
	class: number;
	classDecoration: "none" | "silver" | "gold";
	rivalCount: number;
	reverseRivalCount: number;
	maxStreak: number;
	rank: number;
	isRival: boolean;
	isReverseRival: boolean;
};

export type SolvedacProblem = {
	problemId: number;
	titleKo: string;
	isSolvable: boolean;
	isPartial: boolean;
	acceptedUserCount: number;
	level: number;
	votedUserCount: number;
	isLevelLocked: boolean;
	averageTries: number;
};
export type SolvedacSearchResult = {
	count: number;
	items: SolvedacProblem[];
};


export const getRandomProblems = async(query: string, count = 1) => {
	const url = `https://solved.ac/api/v3/search/problem?query=${encodeURIComponent(query)}&sort=random`;
	const res: SolvedacSearchResult = await fetch(url, { headers }).then((res) => res.json());
	return res.items.slice(0, count);
};

export const getSolvedacUser = async(id: string) => {
	if (!ID.test(id)) return null;
	const url = `https://solved.ac/api/v3/user/show?handle=${id}`;
	const res = await fetch(url, { headers });
	if (res.status !== 200) return null;
	const user: SolvedacUser = await res.json();
	return user;
};
