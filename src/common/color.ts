/* eslint-disable @typescript-eslint/no-non-null-assertion */
import { RatingRecord } from "@prisma/client";

const signChar = (x: number) => (x > 0 || Object.is(x, +0) ? "\x1B[34m+" : "\x1B[31m-");

export const maxPadding = (records: RatingRecord[][], id: string) => {
	let paddingL = 1;
	let paddingR = 1;

	for (const participants of records) {
		const {
			prevRating: rating1,
			newRating: newRating1,
		} = participants.find(({ userId }) => userId === id)!;
		const {
			prevRating: rating2,
			newRating: newRating2,
		} = participants.find(({ userId }) => userId !== id)!;
		paddingL = Math.max(paddingL, Math.abs(newRating1 - rating1).toFixed(0).length);
		paddingR = Math.max(paddingR, Math.abs(newRating2 - rating2).toFixed(0).length);
	}
	return [paddingL, paddingR];
};

export const colorDelta = (delta: number, padding = 0) => {
	delta = Math.round(delta);
	const abs = Math.abs(delta);
	return `${signChar(delta)}${abs.toFixed(0).padStart(padding)}\x1B[0m`;
};
