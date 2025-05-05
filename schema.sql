CREATE TABLE IF NOT EXISTS banks (
    swift_code VARCHAR(11) PRIMARY KEY,
    address TEXT,
    bank_name TEXT,
    country_iso2 CHAR(2),
    country_name TEXT,
    is_headquarter BOOLEAN,
    associated_headquarter VARCHAR(11)
);

CREATE INDEX IF NOT EXISTS idx_swift_code ON banks(swift_code);
CREATE INDEX IF NOT EXISTS idx_country_iso2 ON banks(country_iso2);