/*
  Warnings:

  - The primary key for the `QueryAlias` table will be changed. If it partially fails, the table could be left without primary key constraint.
  - You are about to drop the column `id` on the `QueryAlias` table. All the data in the column will be lost.

*/
-- RedefineTables
PRAGMA foreign_keys=OFF;
CREATE TABLE "new_QueryAlias" (
    "userId" TEXT NOT NULL,
    "alias" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    CONSTRAINT "QueryAlias_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
INSERT INTO "new_QueryAlias" ("alias", "query", "userId") SELECT "alias", "query", "userId" FROM "QueryAlias";
DROP TABLE "QueryAlias";
ALTER TABLE "new_QueryAlias" RENAME TO "QueryAlias";
CREATE UNIQUE INDEX "QueryAlias_userId_alias_key" ON "QueryAlias"("userId", "alias");
PRAGMA foreign_key_check;
PRAGMA foreign_keys=ON;
