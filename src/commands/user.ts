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

export const getBojId = (discordId: string): string | undefined => discordUserDict[discordId];
export const getDiscordId = (bojId: string): string | undefined => bojUserDict[bojId];

// eslint-disable-next-line @typescript-eslint/no-non-null-assertion
export const getBojUser = (bojId: string): UserInfo => userDict[getBojId(bojId)!];
export const getUser = (id: string): UserInfo => userDict[id];

export const getUsers = () => Object.values(userDict);
export const getUserBojIds = () => Object.keys(bojUserDict);
export const getUserDiscordIds = () => Object.keys(discordUserDict);

export const addUser = (discordId: string, bojId: string): void => {
	userDict[bojId] = newUser(discordId, bojId);
	bojUserDict[bojId] = discordId;
	discordUserDict[discordId] = bojId;
};
