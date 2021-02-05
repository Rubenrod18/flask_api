CREATE TABLE celery_taskmeta (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	task_id VARCHAR(155),
	status VARCHAR(50),
	result BLOB,
	date_done DATETIME,
	traceback TEXT,
	name VARCHAR(155),
	args BLOB,
	kwargs BLOB,
	worker VARCHAR(155),
	retries INTEGER,
	queue VARCHAR(155),
	UNIQUE (task_id)
)