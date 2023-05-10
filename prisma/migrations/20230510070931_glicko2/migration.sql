/*
  Warnings:

  - You are about to drop the column `delta` on the `RatingRecord` table. All the data in the column will be lost.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_RatingRecord" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "userId" TEXT NOT NULL,
    "matchId" INTEGER NOT NULL,
    "result" INTEGER NOT NULL,
    "prevRating" REAL NOT NULL DEFAULT 0,
    "newRating" REAL NOT NULL DEFAULT 0,
    CONSTRAINT "RatingRecord_matchId_fkey" FOREIGN KEY ("matchId") REFERENCES "Match" ("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "RatingRecord_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_RatingRecord" ("id", "matchId", "prevRating", "result", "userId") SELECT "id", "matchId", "prevRating", "result", "userId" FROM "RatingRecord";
DROP TABLE "RatingRecord";
ALTER TABLE "new_RatingRecord" RENAME TO "RatingRecord";
CREATE TABLE "new_User" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "bojId" TEXT NOT NULL,
    "rating" REAL NOT NULL,
    "rd" REAL NOT NULL DEFAULT 350,
    "vol" REAL NOT NULL DEFAULT 0.06,
    "winCount" INTEGER NOT NULL DEFAULT 0,
    "tieCount" INTEGER NOT NULL DEFAULT 0,
    "loseCount" INTEGER NOT NULL DEFAULT 0,
    "rated" BOOLEAN NOT NULL DEFAULT false
);
INSERT INTO "new_User" ("bojId", "id", "loseCount", "rated", "rating", "tieCount", "winCount") SELECT "bojId", "id", "loseCount", "rated", "rating", "tieCount", "winCount" FROM "User";
DROP TABLE "User";
ALTER TABLE "new_User" RENAME TO "User";
CREATE UNIQUE INDEX "User_bojId_key" ON "User"("bojId");
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
