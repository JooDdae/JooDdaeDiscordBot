export interface UserInfo {
	id: string;
	bojId: string;
	rating: number;
	count: {
		[-1]: number;
		[0]: number;
		[1]: number;
	};
	active: boolean;
}

const userDict: Record<string, UserInfo> = Object.create(null);

const bojUserDict: Record<string, string> = Object.create(null);

const discordUserDict: Record<string, string> = Object.create(null);

export const newUser = (id: string, bojId: string): UserInfo => ({
	id,
	bojId,
	rating: 1500,
	count: {
		[-1]: 0,
		0: 0,
		1: 0,
	},
	active: false,
});

export const getBojId = (id: string): string | undefined => discordUserDict[id];
export const getDiscordId = (bojId: string): string | undefined => bojUserDict[bojId];

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
export const getBojUser = (bojId: string): UserInfo => userDict[getDiscordId(bojId)!];
export const getUser = (id: string): UserInfo => userDict[id];

export const getUsers = () => Object.values(userDict);
export const getUserBojIds = () => Object.keys(bojUserDict);
export const getUserDiscordIds = () => Object.keys(discordUserDict);

export const addUser = (id: string, bojId: string): void => {
	userDict[id] = newUser(id, bojId);
	bojUserDict[bojId] = id;
	discordUserDict[id] = bojId;
};

addUser("599129630330454037", "cgiosy");
addUser("266477348000497664", "kyo20111");
