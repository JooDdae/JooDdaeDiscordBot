export * from "./assert";
export * from "./elo";
export * from "./color";
export * from "./pad";
export * from "./query";

export type Cleanup = () => void;
export type OnCleanup = (cleanup: Cleanup) => void;
