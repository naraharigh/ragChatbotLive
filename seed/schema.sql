-- Application schema for startup; no demo data or destructive statements.

CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(64) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS clusters (
    cluster_id   SERIAL PRIMARY KEY,
    name         VARCHAR(128) UNIQUE NOT NULL,
    region       VARCHAR(64)  NOT NULL,
    environment  VARCHAR(32)  NOT NULL,
    k8s_version  VARCHAR(16)  NOT NULL,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS nodes (
    node_id     SERIAL PRIMARY KEY,
    cluster_id  INTEGER REFERENCES clusters(cluster_id),
    node_type   VARCHAR(32)  NOT NULL,
    cpu_cores   SMALLINT     NOT NULL,
    memory_gb   SMALLINT     NOT NULL,
    status      VARCHAR(32)  NOT NULL DEFAULT 'Ready',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS deployments (
    deployment_id  SERIAL PRIMARY KEY,
    name           VARCHAR(128) NOT NULL,
    namespace      VARCHAR(64)  NOT NULL,
    replicas       SMALLINT     NOT NULL DEFAULT 1,
    image          VARCHAR(256) NOT NULL,
    version        VARCHAR(32)  NOT NULL,
    cluster_id     INTEGER REFERENCES clusters(cluster_id),
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pods (
    pod_id         SERIAL PRIMARY KEY,
    namespace      VARCHAR(64)  NOT NULL,
    deployment_id  INTEGER REFERENCES deployments(deployment_id),
    status         VARCHAR(32)  NOT NULL,
    node_id        INTEGER REFERENCES nodes(node_id),
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id    SERIAL PRIMARY KEY,
    severity       VARCHAR(4)   NOT NULL,
    cluster_id     INTEGER REFERENCES clusters(cluster_id),
    started_at     TIMESTAMPTZ  NOT NULL,
    resolved_at    TIMESTAMPTZ,
    mttr_minutes   INTEGER,
    rca_summary    TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id       SERIAL PRIMARY KEY,
    fired_at       TIMESTAMPTZ  NOT NULL,
    severity       VARCHAR(4)   NOT NULL,
    source_pod_id  INTEGER REFERENCES pods(pod_id),
    alertname      VARCHAR(128) NOT NULL,
    resolved       BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS oncall_logs (
    log_id              SERIAL PRIMARY KEY,
    engineer            VARCHAR(64)  NOT NULL,
    paged_at            TIMESTAMPTZ  NOT NULL,
    incident_id         INTEGER REFERENCES incidents(incident_id),
    response_time_mins  INTEGER      NOT NULL
);

-- Useful indexes for Text2SQL query performance
CREATE INDEX IF NOT EXISTS idx_nodes_cluster        ON nodes(cluster_id);
CREATE INDEX IF NOT EXISTS idx_pods_deployment      ON pods(deployment_id);
CREATE INDEX IF NOT EXISTS idx_pods_node            ON pods(node_id);
CREATE INDEX IF NOT EXISTS idx_pods_status          ON pods(status);
CREATE INDEX IF NOT EXISTS idx_incidents_cluster    ON incidents(cluster_id);
CREATE INDEX IF NOT EXISTS idx_incidents_severity   ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_fired_at      ON alerts(fired_at);
CREATE INDEX IF NOT EXISTS idx_alerts_severity      ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_oncall_incident      ON oncall_logs(incident_id);
