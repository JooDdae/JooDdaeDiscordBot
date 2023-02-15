export * from "./assert";
export * from "./elo";
export * from "./color";
export * from "./pad";
export * from "./discord";
export * from "./transform";

export type Cleanup = () => void;
export type OnCleanup = (cleanup: Cleanup) => void;
