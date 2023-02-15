-- CreateTable
CREATE TABLE "QueryAlias" (
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "userId" TEXT NOT NULL,
    "alias" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    CONSTRAINT "QueryAlias_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User" ("id") ON DELETE RESTRICT ON UPDATE CASCADE
);
