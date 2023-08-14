--
-- Do not forget to create db before running scripts
--

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tl_user_id INTEGER NOT NULL UNIQUE ,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    is_admin INTEGER NOT NULL default FALSE
);

CREATE TABLE IF NOT EXISTS scheduler_test (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    schedule_data TEXT NOT NULL ,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES user(id)
)