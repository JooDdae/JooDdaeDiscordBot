import { PrismaClient, User } from "@prisma/client";

export type { Match, RatingRecord, User, QueryPreset } from "@prisma/client";

export const db = new PrismaClient();
const activeSet = new Set<string>();

export const TYPE_MAKGORA = 1;

export const getUser = (id: string) => db.user.findUnique({ where: { id } });
export const getUserByBojId = (bojId: string) => db.user.findUnique({ where: { bojId } });
export const getUsers = (count = 50) => db.user.findMany({ take: count });
export const getUserBojIds = (count = 50) => db.user.findMany({
	select: { bojId: true },
	take: count,
});
export const getRanking = (skip = 0, take = 10) => db.user.findMany({
	where: { rated: true },
	orderBy: { rating: "desc" },
	skip,
	take,
});
export const getMatches = (id1: string, id2: string, skip = 0, take = 10) => db.match.findMany({
	where: {
		AND: [
			{ participants: { some: { userId: id1 } } },
			{ participants: { some: { userId: id2 } } },
		],
	},
	include: { participants: true },
	orderBy: { id: "desc" },
	skip,
	take,
});
export const getActive = (id: string) => activeSet.has(id);

export const setActive = (ids: string[], active = true) => {
	for (const id of ids) {
		if (active) activeSet.add(id);
		else activeSet.delete(id);
	}
};


export const addUser = (id: string, bojId: string, rating: number) => db.user.create({
	data: {
		id,
		bojId,
		rating,
	},
});
export const addMakgora = (
	user: User,
	target: User,
	result: -1 | 0 | 1,
	startTime: number,
	rated: boolean,
	delta: number,
	timeout: number,
	problemId: number,
	query: string,
) => db.$transaction([
	// 막고라 정보 기록
	db.match.create({
		data: {
			startDate: new Date(startTime),
			type: TYPE_MAKGORA,
			authorId: user.id,
			rated,
			timeout,
			ext: JSON.stringify({
				problemId,
				query,
			}),

			// 참가자 레이팅 변화 기록
			participants: {
				create: [
					{
						userId: user.id,
						result,
						prevRating: user.rating,
						delta,
					},
					{
						userId: target.id,
						result: -result,
						prevRating: target.rating,
						delta: -delta,
					},
				],
			},
		},
	}),

	// 본인 및 상대방 레이팅 실제 변화 업데이트
	db.user.update({
		where: { id: user.id },
		data: {
			rating: user.rating + delta,
			winCount: user.winCount + Number(result === 1),
			tieCount: user.tieCount + Number(result === 0),
			loseCount: user.loseCount + Number(result === -1),
			rated: user.rated || rated,
		},
	}),
	db.user.update({
		where: { id: target.id },
		data: {
			rating: target.rating - delta,
			winCount: target.winCount + Number(result === -1),
			tieCount: target.tieCount + Number(result === 0),
			loseCount: target.loseCount + Number(result === 1),
			rated: target.rated || rated,
		},
	}),
]);


export const addQueryPreset = (userId: string, name: string, query: string) => db.queryPreset.create({
	data: {
		userId,
		name,
		query,
	},
});
export const getQueryPresets = (userId: string) => db.queryPreset.findMany({ where: { userId } });
export const getQueryPreset = (userId: string, name: string) => db.queryPreset.findUnique({
	where: {
		userId_name: {
			userId,
			name,
		},
	},
});
export const deleteQueryPreset = (userId: string, name: string) => db.queryPreset.delete({
	where: {
		userId_name: {
			userId,
			name,
		},
	},
});
export const editQueryPreset = (userId: string, name: string, query: string) => db.queryPreset.update({
	where: {
		userId_name: {
			userId,
			name,
		},
	},
	data: { query },
});
export const getPresetQueryTable = async(userId: string) => {
	const presetQueryTable: Record<string, string> = Object.create(null);
	for (const { name, query } of await getQueryPresets(userId)) presetQueryTable[name] = query;
	return presetQueryTable;
};
