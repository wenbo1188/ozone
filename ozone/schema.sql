create table if not exists message(
	timestamp integer,
	owner string not null,
	content string not null
);

create table if not exists essay(
	timestamp integer,
	owner string not null,
	title string not null,
	content string not null,
	user1_read integer default 0,
	user2_read integer default 0
);
