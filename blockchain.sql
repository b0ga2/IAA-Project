CREATE TABLE IF NOT EXISTS did_document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    public_key TEXT NOT NULL,
    did_identifier TEXT NOT NULL
);
