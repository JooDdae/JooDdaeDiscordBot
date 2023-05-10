export const padCenter = (v: string | number, n: number, m = 0) => {
	const s = typeof v === "string" ? v : v.toFixed(0);
	return s.padStart(s.length + n + m >> 1).padEnd(n);
};
