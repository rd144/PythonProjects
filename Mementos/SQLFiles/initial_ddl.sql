CREATE TABLE IF NOT EXISTS QUESTIONS (
	question_id integer PRIMARY KEY,
	question_text varchar
)
;

CREATE TABLE IF NOT EXISTS EMAILS (
	email_id integer PRIMARY KEY,
	email_address varchar NOT NULL,
	owner_first_name varchar,
	owner_last_name varchar
)
;

CREATE TABLE IF NOT EXISTS RESPONSE (
	response_id	integer PRIMARY KEY,
	email_id	integer NOT NULL,
	response_text	varchar,
	date_sent date NOT NULL,
	date_received date,
	FOREIGN KEY(email_id) REFERENCES EMAILS(email_id)
);

