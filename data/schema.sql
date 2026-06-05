CREATE TABLE IF NOT EXISTS milestones (
    id           INTEGER PRIMARY KEY,
    name         TEXT NOT NULL,
    workstream   TEXT NOT NULL,
    owner        TEXT NOT NULL,
    due_date     DATE NOT NULL,
    status       TEXT NOT NULL,
    pct_complete INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS experiments (
    id               INTEGER PRIMARY KEY,
    name             TEXT NOT NULL,
    model_version    TEXT NOT NULL,
    workstream       TEXT NOT NULL,
    precision_score  REAL,
    recall_score     REAL,
    ndcg_score       REAL,
    ctr_delta_pct    REAL,
    save_rate_delta  REAL,
    days_running     INTEGER DEFAULT 0,
    sample_size      INTEGER,
    status           TEXT NOT NULL,
    decision_log     TEXT
);

CREATE TABLE IF NOT EXISTS jira_tickets (
    id           INTEGER PRIMARY KEY,
    milestone_id INTEGER REFERENCES milestones(id),
    title        TEXT NOT NULL,
    assignee     TEXT NOT NULL,
    team         TEXT NOT NULL,
    status       TEXT NOT NULL,
    is_blocker   INTEGER DEFAULT 0,
    days_open    INTEGER DEFAULT 0,
    priority     TEXT DEFAULT 'P2'
);

CREATE TABLE IF NOT EXISTS risks (
    id                 INTEGER PRIMARY KEY,
    title              TEXT NOT NULL,
    category           TEXT,
    probability        INTEGER,
    impact             INTEGER,
    owner              TEXT,
    mitigation_status  TEXT DEFAULT 'open',
    days_open          INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dependencies (
    id           INTEGER PRIMARY KEY,
    from_team    TEXT NOT NULL,
    to_team      TEXT NOT NULL,
    description  TEXT NOT NULL,
    due_date     DATE NOT NULL,
    status       TEXT NOT NULL,
    milestone_id INTEGER REFERENCES milestones(id),
    delay_days   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS launch_readiness (
    id           INTEGER PRIMARY KEY,
    gate_name    TEXT NOT NULL,
    category     TEXT NOT NULL,
    owner        TEXT NOT NULL,
    status       TEXT NOT NULL,
    is_blocking  INTEGER DEFAULT 1,
    last_updated DATE
);