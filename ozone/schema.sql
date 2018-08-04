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

create table if not exists album(
	id string primary key not null,
	title string(50) not null,
	about string,
	cover string,
	timestamp integer not null
);

create table if not exists photo(
	id string primary key not null,
	name string(100) not null,
	album string,
	timestamp integer not null
);