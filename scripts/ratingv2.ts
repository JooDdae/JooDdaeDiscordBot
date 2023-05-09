import { PrismaClient } from "@prisma/client";
import { getSolvedacUser } from "../src/io/solvedac";

const db = new PrismaClient();

const main = async() => {
	const users = await db.user.findMany();
	for (const user of users) {
		// eslint-disable-next-line no-await-in-loop
		await getSolvedacUser(user.bojId).then(async(solvedUser) => {
			if (solvedUser === null) return false;
			const updatedUser = await db.user.update({
				where: { bojId: user.bojId },
				data: { rating: user.rating + (solvedUser.ratingByProblemsSum >> 1) - 500 },
			});
			if (updatedUser === null) return false;
			console.log(`ID: ${user.bojId}, Rating: ${user.rating} > ${updatedUser.rating}`);
			return true;
		});
	}
};

main().then(async() => {
	await db.$disconnect();
})
	.catch(async(e) => {
		console.error(e);
		await db.$disconnect();
		process.exit(1);
	});
