-- Baseline migration: application metadata key/value table.
-- Applied migrations are immutable. Change the schema with a NEW V<timestamp>__*.sql file.

CREATE TABLE app_meta (
    key        VARCHAR(100) NOT NULL,
    value      VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CONSTRAINT pk_app_meta PRIMARY KEY (key)
);
