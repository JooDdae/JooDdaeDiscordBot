import { UserInfo } from "./user";

export interface RecordInfo {
    matchType: string;
    challenger: UserInfo;
    challenged: UserInfo;
    result: number;
    delta: number;
    problem: number;
    time: number;
    startTime: number;
    query: string;
    timeout: number;
    rated: boolean;
}

const headToHead: Record<string, RecordInfo[]> = Object.create(null);

const recordDict: Record<string, RecordInfo[]> = Object.create(null);


// eslint-disable-next-line max-len
export const newRecord = (matchType: string, challenger: UserInfo, challenged: UserInfo, result: number, delta: number, problem: number, time: number, startTime: number, query: string, timeout: number, rated: boolean): RecordInfo => ({
	matchType,
	challenger,
	challenged,
	result,
	delta,
	problem,
	time,
	startTime,
	query,
	timeout,
	rated,
});

// eslint-disable-next-line max-len
export const addRecord = (matchType: string, challenger: UserInfo, challenged: UserInfo, result: number, delta: number, problem: number, time: number, startTime: number, query: string, timeout: number, rated: boolean): void => {
	// eslint-disable-next-line max-len
	const record = newRecord(matchType, structuredClone(challenger), structuredClone(challenged), result, delta, problem, time, startTime, query, timeout, rated);
	if (!recordDict[challenger.id]) recordDict[challenger.id] = [];
	if (!recordDict[challenged.id]) recordDict[challenged.id] = [];
	recordDict[challenger.id].push(record);
	recordDict[challenged.id].push(record);
	if (!headToHead[challenger.bojId.concat(challenged.bojId)]) headToHead[challenger.bojId.concat(challenged.bojId)] = [];
	if (!headToHead[challenged.bojId.concat(challenger.bojId)]) headToHead[challenged.bojId.concat(challenger.bojId)] = [];
	headToHead[challenger.bojId.concat(challenged.bojId)].push(record);
	headToHead[challenged.bojId.concat(challenger.bojId)].push(record);
};

export const getHeadToHeadRecord = (bojId1: string, bojId2: string): RecordInfo[] | undefined => headToHead[bojId1.concat(bojId2)];
export const getRecord = (discordId: string): RecordInfo[] | undefined => recordDict[discordId];
