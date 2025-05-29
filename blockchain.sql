CREATE TABLE IF NOT EXISTS did_document (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    public_key_low_loa TEXT NOT NULL,
    public_key_susbtantial_loa TEXT NOT NULL,

    did_identifier TEXT NOT NULL
);
