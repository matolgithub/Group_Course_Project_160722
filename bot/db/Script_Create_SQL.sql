CREATE TABLE IF NOT EXISTS user_data (
	user_id INTEGER PRIMARY KEY,
	profile_link VARCHAR(60),
                age INTEGER CHECK(age<150),
	first_name VARCHAR(40),
	last_name VARCHAR(40),
                sex INTEGER,
	city VARCHAR(60),
	token VARCHAR(200),
	groups INTEGER,
                interests TEXT,
	music TEXT,
	books TEXT
);

CREATE TABLE IF NOT EXISTS elected_list (
                user_data_user_id INTEGER NOT NULL REFERENCES user_data(user_id),
	bot_user_user_id INTEGER NOT NULL REFERENCES user_data(user_id),
	CONSTRAINT pk_el PRIMARY KEY (user_data_user_id, bot_user_user_id)
);

CREATE TABLE IF NOT EXISTS black_list (
	user_data_user_id INTEGER NOT NULL REFERENCES user_data(user_id),
	bot_user_user_id INTEGER NOT NULL REFERENCES user_data(user_id),
	CONSTRAINT pk_bl PRIMARY KEY (user_data_user_id, bot_user_user_id)
);

CREATE TABLE IF NOT EXISTS photo_list (
	id SERIAL PRIMARY KEY,
                photo_link VARCHAR(250),
	photo_id INTEGER,
	user_data_user_id INTEGER NOT NULL REFERENCES user_data(user_id)
);

CREATE TABLE IF NOT EXISTS likes_list (
	id SERIAL PRIMARY KEY,
	bot_user_user_id INTEGER NOT NULL REFERENCES user_data(user_id),
	photo_list_id INTEGER NOT NULL REFERENCES photo_list(id)
);