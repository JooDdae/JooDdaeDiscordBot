export class AlertMessage extends Error {}

type Assert = <A extends unknown[]>(
	condition: unknown,
	fn: string | ((...args: A) => string),
	...args: A
) => asserts condition;

export const assert: Assert = <A extends unknown[]>(
	condition: unknown,
	fn: string | ((...args: A) => string),
	...args: A
): asserts condition => {
	if (!condition) {
		const message = typeof fn === "string" ? fn : fn(...args);
		throw new AlertMessage(message);
	}
};
