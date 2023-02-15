-- CreateTable
CREATE TABLE "User" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "bojId" TEXT NOT NULL,
    "rating" REAL NOT NULL,
    "winCount" INTEGER NOT NULL DEFAULT 0,
    "tieCount" INTEGER NOT NULL DEFAULT 0,
    "loseCount" INTEGER NOT NULL DEFAULT 0,
    "rated" BOOLEAN NOT NULL DEFAULT false
);

-- CreateTable
CREATE TABLE "Match" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "startDate" DATETIME NOT NULL,
    "type" INTEGER NOT NULL,
    "authorId" TEXT NOT NULL,
    "rated" BOOLEAN NOT NULL,
    "timeout" INTEGER NOT NULL,
    "ext" TEXT NOT NULL,
    CONSTRAINT "Match_authorId_fkey" FOREIGN KEY ("authorId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "RatingRecord" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "userId" TEXT NOT NULL,
    "matchId" INTEGER NOT NULL,
    "result" INTEGER NOT NULL,
    "prevRating" REAL NOT NULL,
    "delta" REAL NOT NULL,
    CONSTRAINT "RatingRecord_matchId_fkey" FOREIGN KEY ("matchId") REFERENCES "Match" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "RatingRecord_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateTable
CREATE TABLE "QueryAlias" (
    "userId" TEXT NOT NULL,
    "alias" TEXT NOT NULL,
    "query" TEXT NOT NULL,

    PRIMARY KEY ("userId", "alias"),
    CONSTRAINT "QueryAlias_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

-- CreateIndex
CREATE UNIQUE INDEX "User_bojId_key" ON "User"("bojId");

