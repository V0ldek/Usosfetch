CREATE TABLE grades
(
	id VARCHAR(25) NOT NULL
		CONSTRAINT grades_pkey
			PRIMARY KEY,
	list VARCHAR(2048) NOT NULL
)
;

CREATE UNIQUE INDEX grades_id_uindex
	ON grades (id)
;

CREATE TABLE logs
(
	id SERIAL NOT NULL
		CONSTRAINT logs_pkey
			PRIMARY KEY,
	log VARCHAR(20480) NOT NULL,
	is_error BOOLEAN DEFAULT FALSE NOT NULL
)
;

CREATE UNIQUE INDEX logs_id_uindex
	ON logs (id)
;

