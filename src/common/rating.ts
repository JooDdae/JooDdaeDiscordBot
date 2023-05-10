import { User } from "@prisma/client";
import { Glicko2, Player } from "glicko2.ts";

const ranking = new Glicko2();

export const battle = (user1: User, user2: User, result: number, rated: boolean): [Player, Player] => {
	const p1 = ranking.makePlayer(user1.rating, user1.rd, user1.vol);
	const p2 = ranking.makePlayer(user2.rating, user2.rd, user2.vol);
	ranking.updateRatings(rated ? [[p1, p2, result]] : []);
	return [p1, p2];
};
