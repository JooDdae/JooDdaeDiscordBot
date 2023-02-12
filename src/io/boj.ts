import { JSDOM } from "jsdom";

const headers = { "User-Agent": "JooDdae Bot" };

export const getAcceptedSubmission = async(userId: string, problemId: string | number) => {
	const url = `https://www.acmicpc.net/status?problem_id=${problemId}&userId=${userId}&result_id=4`;
	const res = await fetch(url, { headers }).then((res) => res.text());
	const doc = new JSDOM(res).window.document;
	const time = doc.querySelector("tbody > tr:last-child > td:first-child")?.textContent;
	return time ? Number(time) : Infinity;
};
