-- +goose Up
CREATE TABLE IF NOT EXISTS requests (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    method TEXT NOT NULL,
    path TEXT NOT NULL,
    headers JSONB NOT NULL DEFAULT '{}'::jsonb,
    body_ref TEXT,
    target_service TEXT NOT NULL,
    response_status INT,
    response_body_ref TEXT,
    latency_ms INT,
    replayed_from UUID REFERENCES requests(id)
);

CREATE INDEX IF NOT EXISTS requests_timestamp_idx ON requests (timestamp DESC);
CREATE INDEX IF NOT EXISTS requests_target_service_idx ON requests (target_service);
CREATE INDEX IF NOT EXISTS requests_response_status_idx ON requests (response_status);
CREATE INDEX IF NOT EXISTS requests_replayed_from_idx ON requests (replayed_from);

-- +goose Down
DROP TABLE IF EXISTS requests;
