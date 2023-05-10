/* eslint-disable no-await-in-loop */
import { PrismaClient, User } from "@prisma/client";

import { battle } from "../src/common/rating";
import { getSolvedacUser } from "../src/io/solvedac";

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

const db = new PrismaClient();

export const replay = async() => {
	const matches = await db.match.findMany({ include: { participants: true } });
	const users: Record<string, User> = Object.create(null);
	for (const user of await db.user.findMany()) {
		users[user.id] = user;

		let solvedRating = 1000;
		let solvedUser = await getSolvedacUser(user.bojId);
		if (solvedUser === null) {
			for (let retry = 0; retry < 3; retry++) {
				await delay(3000);
				solvedUser = await getSolvedacUser(user.bojId);
			}
		}
		if (solvedUser !== null) solvedRating = solvedUser.rating;
		user.rating = 1000 + solvedRating / 2;
		console.log(`${user.bojId}: ${user.rating}`);
	}
	console.log("Hi!");

	for (const { authorId, rated, participants } of matches) {
		let [authorRecord, targetRecord] = participants;
		if (authorRecord.userId !== authorId) [authorRecord, targetRecord] = [targetRecord, authorRecord];
		const targetId = targetRecord.userId;

		const user = users[authorId];
		const target = users[targetId];
		const result = authorRecord.result as (-1 | 0 | 1);
		const eloResult = result === 1 ? 1 : result === -1 ? 0 : 0.5;
		const [newUser, newTarget] = battle(user, target, eloResult, rated);
		await db.$transaction([
			db.ratingRecord.update(
				{
					where: { id: authorRecord.id },
					data: {
						prevRating: user.rating,
						newRating: newUser.getRating(),
					},
				},
			),
			db.ratingRecord.update(
				{
					where: { id: targetRecord.id },
					data: {
						prevRating: target.rating,
						newRating: newTarget.getRating(),
					},
				},
			),
		]);
		user.rating = newUser.getRating();
		user.rd = newUser.getRd();
		user.vol = newUser.getVol();
		target.rating = newTarget.getRating();
		target.rd = newTarget.getRd();
		target.vol = newTarget.getVol();
	}

	await db.$transaction(
		Object.values(users)
			.map((user) => db.user.update({
				where: { id: user.id },
				data: {
					rating: user.rating,
					vol: user.vol,
					rd: user.rd,
				},
			})),
	);
};

// TODO: replay 실행 스크립트 별도 파일로 분리
replay();
