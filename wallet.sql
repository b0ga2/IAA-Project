CREATE TABLE IF NOT EXISTS vcs (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Automatic

    original_national_base TEXT NOT NULL, -- Issuer 
    rank TEXT NOT NULL, -- Issuer 
    division TEXT NOT NULL,-- Issuer 
    security_clearance_level TEXT NOT NULL,-- Issuer 
    health_code INT NOT NULL, --holder
    nationality TEXT NOT NULL, --holder
    full_name TEXT NOT NULL, --holder
    holder_id TEXT NOT NULL, -- Issuer
    initial_date DATE NOT NULL, -- Issuer 
    final_date DATE NOT NULL, -- Issuer 
    did_identifier TEXT NOT NULL, -- Issuer 
 
    issuer_id INT NOT NULL -- Issuer 
);


