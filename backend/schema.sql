-- TimescaleDB Schema for Cloudscope AIOps

-- Create the table for raw vitals and the generated anomaly score
CREATE TABLE IF NOT EXISTS metrics_history (
    time TIMESTAMPTZ NOT NULL,
    instance_id TEXT NOT NULL,
    cpu_usage_percent DOUBLE PRECISION,
    memory_usage_percent DOUBLE PRECISION,
    network_in_bytes DOUBLE PRECISION,
    hourly_spend DOUBLE PRECISION,
    suspicion_score DOUBLE PRECISION,
    is_anomaly BOOLEAN DEFAULT FALSE
);

-- Convert to a hypertable (TimescaleDB specific functionality)
-- Only run this if the hypertable doesn't already exist.
-- Assuming chunk_time_interval of 1 day for this scale.
-- SELECT create_hypertable('metrics_history', 'time', if_not_exists => TRUE);

-- Index for querying by instance
CREATE INDEX IF NOT EXISTS ix_metrics_instance_time ON metrics_history (instance_id, time DESC);
