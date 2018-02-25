create table if not exists message(
	timestamp integer,
	owner string not null,
	content string not null
);

