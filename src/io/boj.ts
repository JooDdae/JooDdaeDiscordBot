import { JSDOM } from "jsdom";

const SHARE_URL1 = "https://www.acmicpc.net/source/share/";
const SHARE_URL2 = "http://boj.kr/";
const SHARE_TOKEN = /^[0-9a-f]{32}$/;

const headers = { "User-Agent": "JooDdae Bot" };

export const getAcceptedSubmission = async(userId: string, problemId: number) => {
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

export const getSharedSource = async(url: string) => {
	if (url.startsWith(SHARE_URL1)) url = url.slice(SHARE_URL1.length);
	else if (url.startsWith(SHARE_URL2)) url = url.slice(SHARE_URL2.length);
	if (!SHARE_TOKEN.test(url)) return null;

	url = SHARE_URL1 + url;
	const res = await fetch(url, { headers }).then((res) => res.text());
	const doc = new JSDOM(res).window.document;

	const bojId = doc.querySelector("div.breadcrumbs > div.container:first-child")?.textContent?.split("\n")[3].trim();
	const content = doc.querySelector("div.form-group > div.col-md-12 > textarea:first-child")?.textContent?.split("\n")[0];
	if (!bojId || !content) return null;
	return {
		bojId,
		content,
	};
};
