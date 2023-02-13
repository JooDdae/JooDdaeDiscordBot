import { JSDOM } from "jsdom";

const headers = { "User-Agent": "JooDdae Bot" };

export const getAcceptedSubmission = async(userId: string, problemId: string | number) => {
	const url = `https://www.acmicpc.net/status?problem_id=${problemId}&user_id=${userId}&result_id=4`;
	const res = await fetch(url, { headers }).then((res) => res.text());
	const doc = new JSDOM(res).window.document;
	const time = doc.querySelector("tbody > tr:last-child > td:first-child")?.textContent;
	return time ? Number(time) : Infinity;
};

export const existBojId = async(bojId: string) => {
	const url = `https://www.acmicpc.net/user/${bojId}`;
	const res = await fetch(url, { headers }).then((res) => res.status === 200);
	return res;
};

export const getSharedSource = async(sharedUrl: string | undefined) => {
	if (sharedUrl === undefined || !sharedUrl.startsWith("http")) return undefined;
	const res = await fetch(sharedUrl, { headers }).then((res) => res.text());
	const doc = new JSDOM(res).window.document;
	const input = doc.querySelector("div.form-group > div.col-md-12 > textarea:first-child")?.textContent?.split("\n")[0];
	if (!input) return undefined;
	const inputBojId = doc.querySelector("div.breadcrumbs > div.container:first-child")?.textContent?.split("\n")[3].trim();
	return [inputBojId, input];
};
