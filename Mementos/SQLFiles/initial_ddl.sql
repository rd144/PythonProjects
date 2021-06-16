CREATE TABLE IF NOT EXISTS QUESTIONS (
	question_id integer PRIMARY KEY,
	question_text varchar,
	sent integer DEFAULT 0 NOT NULL --0 for False, 1 for True
)
;

CREATE TABLE IF NOT EXISTS EMAILS (
	email_id integer PRIMARY KEY,
	email_address varchar NOT NULL,
	owner_first_name varchar,
	owner_last_name varchar
)
;

CREATE TABLE IF NOT EXISTS CORRESPONDENCE (
	response_id	integer PRIMARY KEY,
	email_id	integer NOT NULL,
	question_id integer NOT NULL,
	datetime_sent varchar NOT NULL,
    datetime_received varchar,
	response_text	varchar,
	FOREIGN KEY(email_id) REFERENCES EMAILS(email_id),
	FOREIGN KEY(question_id) REFERENCES QUESTIONS(question_id)
);

