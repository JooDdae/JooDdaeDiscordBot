export const padCenter = (v: string | number, n: number, m = 0) => {
	const s = v.toString();
	return s.padStart(s.length + n + m >> 1).padEnd(n);
};
