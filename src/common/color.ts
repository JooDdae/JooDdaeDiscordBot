const signChar = (x: number) => (x > 0 || Object.is(x, +0) ? "\x1B[34m+" : "\x1B[31m-");

export const colorDelta = (delta: number) => {
	delta = Math.round(delta);
	const abs = Math.abs(delta);
	return `${signChar(delta)}${abs < 10 ? " " : ""}${abs}\x1B[0m`;
};
