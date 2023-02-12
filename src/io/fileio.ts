import { readFileSync, writeFileSync } from "fs";

export const getUserList = () => {
	const userListFile = readFileSync("./src/io/userList.txt", "utf8");
	const userList: string[][] = [];
	userListFile.split("\n").forEach((user) => {
		if (user !== "")
			userList.push(user.split(" "));
	});
	return userList;
};

export const saveUser = (id: string, bojId: string): void => {
	writeFileSync("./src/io/userList.txt", `${id} ${bojId}\n`, { flag: "a" });
};

export const getMatchLog = () => {
	const matchLogFile = readFileSync("./src/io/matchLog.txt", "utf8");
	const matchLog: string[][] = [];
	matchLogFile.split("\n").forEach((match) => {
		if (match !== "")
			matchLog.push(match.split(" "));
	});
	return matchLog;
};

// eslint-disable-next-line max-len
export const saveMatchLog = (matchType: string, challenger: string, challenged: string, result: -1 | 0 | 1, problem: number, time: number, startDatetime: number, query: string, timeout: number, rated: boolean): void => {
	writeFileSync("./src/io/matchLog.txt", `${matchType} ${challenger} ${challenged} ${result} ${problem} ${time} ${startDatetime} ${query} ${timeout} ${rated}\n`, { flag: "a" });
};
