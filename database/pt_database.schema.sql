CREATE TABLE IF NOT EXISTS "role" (
	"id"	INTEGER UNIQUE,
	"type"	TEXT NOT NULL,
	"character"	TEXT,
	"people_id"	INTEGER NOT NULL,
	"tv_show_id"	INTEGER NOT NULL,
	"season_id"	INTEGER NOT NULL,
	FOREIGN KEY("season_id") REFERENCES "season"("id"),
	FOREIGN KEY("tv_show_id") REFERENCES "tv_show"("id"),
	FOREIGN KEY("people_id") REFERENCES "people"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "season" (
	"id"	INTEGER UNIQUE,
	"tv_show_id"	INTEGER NOT NULL,
	"title"	TEXT NOT NULL,
	"season_number"	INTEGER NOT NULL,
	"year"	INTEGER,
	"plot"	TEXT,
	"writer"	TEXT,
	"rating"	TEXT,
	"premiered"	TEXT,
	"releasedate"	TEXT,
	FOREIGN KEY("tv_show_id") REFERENCES "tv_show"("id"),
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "tv_show" (
	"id"	INTEGER UNIQUE,
	"tmdb_id"	INTEGER NOT NULL UNIQUE,
	"title"	TEXT NOT NULL,
	"original_title"	TEXT,
	"year"	INTEGER,
	"plot"	TEXT,
	"rating"	TEXT,
	"mpaa"	TEXT,
	"seasons"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "people" (
	"id"	INTEGER UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	"full_name"	TEXT,
	"birthday"	TEXT,
	"birthday_year"	INTEGER,
	"birth_place"	TEXT,
	"biography"	TEXT,
	"famous_roles"	TEXT,
	"photo_src_url"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE UNIQUE INDEX unique_role_constraint

ON role (character, people_id, tv_show_id, season_id);
CREATE UNIQUE INDEX unique_season_constraint

ON season (tv_show_id, season_number);
