export const eloDelta = (rating: number, targetRating: number, myGameResult: 0 | 0.5 | 1) => Math.round(
	32 * (myGameResult - (1 / (1 + 10 ** ((targetRating - rating) / 400)))),
);
