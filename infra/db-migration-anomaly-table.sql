CREATE TABLE anomalies (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    metric_name TEXT NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    threshold DOUBLE PRECISION,
    status TEXT NOT NULL
);

ALTER TABLE anomalies
    ADD COLUMN detection_method TEXT;

ALTER TABLE anomalies
    ADD COLUMN anomaly_score FLOAT;

ALTER TABLE anomalies
    ADD COLUMN context JSONB;

ALTER TABLE anomalies
    ADD COLUMN config JSONB;
