-- AlterTable

ALTER TABLE "QueryAlias" RENAME TO "QueryPreset";
ALTER TABLE "QueryPreset" RENAME COLUMN "alias" to "name";
