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

INSERT INTO vcs (
    original_national_base, rank, division, security_clearance_level,
    health_code, nationality, full_name, holder_id, initial_date,
    final_date, did_identifier, issuer_id
)
SELECT * FROM (
    SELECT 'NAT-00123', 'Captain', 'Infantry', 'Top Secret',
           5, 'USA', 'John A. Smith', 'HID-123456', '2023-01-15',
           '2026-01-15', 'did:example:123abc', 101
    UNION ALL
    SELECT 'NAT-00456', 'Lieutenant', 'Air Force', 'Secret',
           3, 'Canada', 'Marie Curie', 'HID-654321', '2024-05-10',
           '2027-05-10', 'did:example:456def', 102
    UNION ALL
    SELECT 'NAT-00789', 'Major', 'Navy', 'Confidential',
           4, 'UK', 'Liam Johnson', 'HID-789123', '2022-09-01',
           '2025-09-01', 'did:example:789ghi', 103
    UNION ALL
    SELECT 'NAT-00234', 'Sergeant', 'Engineering', 'Top Secret',
           2, 'Australia', 'Chloe Nguyen', 'HID-321987', '2023-03-20',
           '2026-03-20', 'did:example:234jkl', 104
    UNION ALL
    SELECT 'NAT-00987', 'Colonel', 'Medical Corps', 'Secret',
           1, 'Germany', 'Hans Müller', 'HID-987654', '2021-11-11',
           '2024-11-11', 'did:example:987mno', 105
) AS tmp
WHERE NOT EXISTS (SELECT 1 FROM vcs);
