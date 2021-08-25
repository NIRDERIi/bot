CREATE TABLE IF NOT EXISTS prefixes (
    guild BIGINT PRIMARY KEY,
    prefix TEXT
);

CREATE TABLE IF NOT EXISTS tags
(
    title TEXT,
    content TEXT,
    author BIGINT,
    guild BIGINT,
    created_at TIMESTAMP WITH TIME ZONE,
    uses BIGINT
);