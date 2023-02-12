import { UserInfo } from "./user";

export interface RecordInfo {
    matchType: string;
    challenger: UserInfo;
    challenged: UserInfo;
    result: string;
    delta: number;
    problem: number;
    time: number;
    startDatetime: number;
    query: string;
    timeout: number;
    rated: boolean;
}

const headToHead: Record<string, Record<string, RecordInfo[]>> = Object.create(null);

const recordDict: Record<string, RecordInfo[]> = Object.create(null);


// eslint-disable-next-line max-len
export const newRecord = (matchType: string, challenger: UserInfo, challenged: UserInfo, result: string, delta: number, problem: number, time: number, startDatetime: number, query: string, timeout: number, rated: boolean): RecordInfo => ({
	matchType,
	challenger,
	challenged,
	result,
	delta,
	problem,
	time,
	startDatetime,
	query,
	timeout,
	rated,
});

// eslint-disable-next-line max-len
export const addRecord = (matchType: string, challenger: UserInfo, challenged: UserInfo, result: string, delta: number, problem: number, time: number, startDatetime: number, query: string, timeout: number, rated: boolean): void => {
	const record = newRecord(matchType, challenger, challenged, result, delta, problem, time, startDatetime, query, timeout, rated);
	recordDict[challenger.id].push(record);
	recordDict[challenged.id].push(record);
	headToHead[challenger.bojId][challenged.bojId].push(record);
	headToHead[challenged.bojId][challenger.bojId].push(record);
};

export const getHeadToHeadRecord = (bojId1: string, bojId2: string): RecordInfo[] | undefined => headToHead[bojId1][bojId2];
export const getRecord = (discordId: string): RecordInfo[] | undefined => recordDict[discordId];
