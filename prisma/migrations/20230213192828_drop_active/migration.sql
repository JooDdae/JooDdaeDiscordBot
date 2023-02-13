/*
  Warnings:

  - You are about to drop the column `active` on the `User` table. All the data in the column will be lost.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_User" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "bojId" TEXT NOT NULL,
    "rating" REAL NOT NULL,
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
