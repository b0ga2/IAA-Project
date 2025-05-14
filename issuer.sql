CREATE TABLE IF NOT EXISTS vcs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    original_national_base TEXT NOT NULL,
    rank TEXT NOT NULL,
    division TEXT NOT NULL,
    security_clearance_level TEXT NOT NULL,
    health_code INT NOT NULL,
    nationality TEXT NOT NULL,
    full_name TEXT NOT NULL,
    holder_id TEXT NOT NULL,
    initial_date DATE NOT NULL,
    final_date DATE NOT NULL,
    did_identifier TEXT NOT NULL,

    issuer_id INT NOT NULL
);
