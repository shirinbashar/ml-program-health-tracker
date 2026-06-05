import sqlite3
import random
from datetime import date, timedelta

DB_PATH = "data/program_health.db"

def random_date(days_from_today_min, days_from_today_max):
    delta = random.randint(days_from_today_min, days_from_today_max)
    return (date.today() + timedelta(days=delta)).isoformat()

def past_date(days_ago):
    return (date.today() - timedelta(days=days_ago)).isoformat()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Load schema
with open("data/schema.sql") as f:
    cur.executescript(f.read())

# ── MILESTONES ──────────────────────────────────────────────
milestones = [
    ("Ranking model v2 offline eval complete",  "Ranking",       "Ana Torres",    random_date(-5, 5),   "on_track", 85),
    ("Ranking model v2 online experiment start","Ranking",       "Ana Torres",    random_date(5, 15),   "on_track", 40),
    ("Ads relevance model retrain",             "Ads Relevance", "Ben Kim",       random_date(-10, 0),  "at_risk",  60),
    ("Ads relevance A/B test launch",           "Ads Relevance", "Ben Kim",       random_date(10, 20),  "on_track", 20),
    ("Feature pipeline migration to v3",        "Infra",         "Carla Diaz",    random_date(-3, 3),   "on_track", 75),
    ("GPU cluster capacity expansion",          "Infra",         "Carla Diaz",    random_date(15, 25),  "at_risk",  30),
    ("Safety classifier update",                "Quality",       "David Park",    random_date(-15, -5), "delayed",  50),
    ("Spam detection model refresh",            "Quality",       "David Park",    random_date(5, 10),   "on_track", 65),
    ("Pinner interest model v4 eval",           "Ranking",       "Ana Torres",    random_date(20, 30),  "on_track", 10),
    ("Ads CTR prediction model ship",           "Ads Relevance", "Ben Kim",       random_date(25, 35),  "on_track", 5),
    ("Logging pipeline deprecation",            "Infra",         "Carla Diaz",    random_date(-20,-10), "delayed",  40),
    ("Content quality score v2",                "Quality",       "David Park",    random_date(10, 20),  "on_track", 55),
    ("Retrieval model latency optimization",    "Ranking",       "Ana Torres",    random_date(30, 45),  "on_track", 0),
    ("Budget pacing algorithm update",          "Ads Relevance", "Ben Kim",       random_date(-5, 5),   "at_risk",  70),
    ("Model serving infra upgrade",             "Infra",         "Carla Diaz",    random_date(40, 60),  "on_track", 0),
]
cur.executemany(
    "INSERT INTO milestones (name,workstream,owner,due_date,status,pct_complete) VALUES (?,?,?,?,?,?)",
    milestones
)

# ── EXPERIMENTS ─────────────────────────────────────────────
experiments = [
    ("Ranking v2 w/ user history features",  "v2.1", "Ranking",       0.74, 0.68, 0.81, 1.8,  0.5,  14, 120000, "running",        "Strong offline. Online trending positive."),
    ("Ads relevance BERT embeddings",        "v3.0", "Ads Relevance", 0.79, 0.71, 0.85, 2.1, -0.4,  10, 85000,  "running",        "CTR up but save rate down — guardrail concern."),
    ("Pinner interest graph v4",             "v4.0", "Ranking",       0.71, 0.65, 0.78, 0.3,  0.1,  25, 60000,  "running",        "No significant signal after 25 days."),
    ("Spam classifier XGBoost refresh",      "v1.4", "Quality",       0.88, 0.83, 0.90, 0.9,  0.6,   8, 95000,  "running",        "Early results positive."),
    ("CTR prediction LightGBM v2",           "v2.0", "Ads Relevance", 0.76, 0.70, 0.82, 1.5,  0.3,  12, 110000, "running",        "Solid metrics, approaching graduation."),
    ("Content quality score v2 test",        "v2.0", "Quality",       0.80, 0.75, 0.87, 0.6,  0.4,   5, 40000,  "running",        "Too early to call."),
    ("Retrieval two-tower model",            "v1.1", "Ranking",       0.69, 0.63, 0.76, 2.4,  0.8,  18, 130000, "ready_to_scale", "Strong online and offline. Recommend graduation."),
    ("Budget pacing RL model",               "v0.9", "Ads Relevance", 0.72, 0.66, 0.79,-0.2,  0.1,   7, 30000,  "iterate",        "Primary metric negative. Needs iteration."),
    ("Safety NSFW classifier v3",            "v3.0", "Quality",       0.92, 0.88, 0.94, 0.0,  0.0,   3, 20000,  "running",        "Accuracy-focused, no engagement metrics."),
    ("Ads diversity ranker",                 "v1.0", "Ads Relevance", 0.70, 0.64, 0.77, 1.1, -0.6,  15, 75000,  "running",        "CTR up but save rate degraded — review needed."),
    ("Homefeed ranking ensemble",            "v5.2", "Ranking",       0.77, 0.72, 0.84, 1.9,  0.7,  21, 140000, "ready_to_scale", "Consistent lifts across all metrics."),
    ("Related Pins embedding model",         "v2.3", "Ranking",       0.73, 0.67, 0.80, 0.1,  0.0,  28, 55000,  "running",        "30 days, no signal. Recommend stopping."),
    ("Ads frequency cap optimizer",          "v1.2", "Ads Relevance", 0.68, 0.61, 0.74, 0.8,  0.5,   9, 65000,  "running",        "Moderate positive signal."),
    ("Interest taxonomy classifier",         "v3.1", "Quality",       0.85, 0.80, 0.89, 0.4,  0.3,   6, 45000,  "running",        "Early stage."),
    ("Video ranking model v1",               "v1.0", "Ranking",       0.66, 0.60, 0.72,-0.5,  0.2,  11, 38000,  "iterate",        "Primary metric negative. Needs work."),
]
cur.executemany(
    """INSERT INTO experiments
       (name,model_version,workstream,precision_score,recall_score,ndcg_score,
        ctr_delta_pct,save_rate_delta,days_running,sample_size,status,decision_log)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
    experiments
)

# ── JIRA TICKETS ─────────────────────────────────────────────
tickets = [
    (1,  "Offline eval pipeline broken on GPU cluster",     "Ana Torres",  "Ranking",       "blocked",     1, 12, "P0"),
    (1,  "NDCG metric calculation bug in eval harness",     "Sam Lee",     "Ranking",       "in_progress", 1,  8, "P1"),
    (1,  "Write offline eval results doc",                  "Ana Torres",  "Ranking",       "open",        0,  3, "P2"),
    (2,  "Set up A/B test config in experimentation platform","Sam Lee",   "Ranking",       "open",        0,  1, "P1"),
    (2,  "Define primary and guardrail metrics for exp",    "Ana Torres",  "Ranking",       "done",        0,  0, "P1"),
    (3,  "Training data pipeline missing Nov-Dec data",     "Ben Kim",     "Ads Relevance", "blocked",     1, 18, "P0"),
    (3,  "Model retraining job OOM on 80GB GPU",            "Priya Nair",  "Ads Relevance", "in_progress", 1,  9, "P1"),
    (3,  "Validate feature store schema changes",           "Ben Kim",     "Ads Relevance", "open",        0,  4, "P2"),
    (4,  "A/B test ramp plan approval from leadership",     "Ben Kim",     "Ads Relevance", "open",        1,  5, "P1"),
    (5,  "Migrate batch feature jobs to new pipeline",      "Carla Diaz",  "Infra",         "in_progress", 0,  6, "P2"),
    (5,  "Validate data parity between v2 and v3 pipelines","Carla Diaz",  "Infra",         "open",        0,  2, "P2"),
    (6,  "GPU procurement blocked on vendor approval",      "Carla Diaz",  "Infra",         "blocked",     1, 22, "P0"),
    (6,  "Capacity planning doc not reviewed",              "Carla Diaz",  "Infra",         "open",        0,  7, "P2"),
    (7,  "Safety classifier training dataset audit",        "David Park",  "Quality",       "blocked",     1, 16, "P1"),
    (7,  "Legal review of training data sources",           "David Park",  "Quality",       "open",        1, 11, "P1"),
    (7,  "Write safety eval test plan",                     "Maria Chen",  "Quality",       "in_progress", 0,  5, "P2"),
    (8,  "Spam model eval on new test set",                 "Maria Chen",  "Quality",       "done",        0,  0, "P2"),
    (8,  "Deploy spam model to staging",                    "David Park",  "Quality",       "in_progress", 0,  3, "P2"),
    (9,  "Pinner interest feature spec review",             "Ana Torres",  "Ranking",       "open",        0,  1, "P3"),
    (10, "CTR model serving latency benchmark",             "Ben Kim",     "Ads Relevance", "open",        0,  2, "P2"),
    (11, "Deprecation communication to downstream teams",   "Carla Diaz",  "Infra",         "blocked",     1, 20, "P1"),
    (11, "Runbook for logging pipeline cutover",            "Carla Diaz",  "Infra",         "open",        0,  8, "P2"),
    (12, "Content score v2 offline benchmark",             "David Park",  "Quality",       "in_progress", 0,  4, "P2"),
    (13, "Latency profiling on retrieval model",            "Ana Torres",  "Ranking",       "open",        0,  1, "P3"),
    (14, "Budget pacing backtest results review",           "Ben Kim",     "Ads Relevance", "blocked",     1, 15, "P1"),
    (14, "Stakeholder sign-off on pacing changes",          "Ben Kim",     "Ads Relevance", "open",        1,  9, "P1"),
    (15, "Model serving load test plan",                    "Carla Diaz",  "Infra",         "open",        0,  2, "P2"),
]
cur.executemany(
    """INSERT INTO jira_tickets
       (milestone_id,title,assignee,team,status,is_blocker,days_open,priority)
       VALUES (?,?,?,?,?,?,?,?)""",
    tickets
)

# ── RISKS ────────────────────────────────────────────────────
risks = [
    ("GPU cluster capacity insufficient for Q3 launches", "Resource",   5, 5, "Carla Diaz",  "open",      22),
    ("Safety classifier delay blocks launch gate",        "Timeline",   4, 5, "David Park",  "open",      16),
    ("Training data pipeline missing 2 months of data",   "Technical",  4, 4, "Ben Kim",     "open",      18),
    ("Legal review turnaround unknown for data sources",  "Dependency", 3, 4, "David Park",  "open",      11),
    ("Vendor approval for GPU procurement stalled",       "Dependency", 4, 4, "Carla Diaz",  "open",      22),
    ("Ranking eval harness bug may invalidate metrics",   "Technical",  3, 3, "Ana Torres",  "open",       8),
    ("A/B test ramp approval dependency on VP schedule",  "Resource",   2, 3, "Ben Kim",     "mitigated",  5),
    ("Ads relevance guardrail metric degradation",        "Technical",  3, 4, "Ben Kim",     "open",      10),
    ("Logging deprecation downstream team not ready",     "Dependency", 4, 3, "Carla Diaz",  "open",      20),
    ("Model serving infra upgrade timeline slipping",     "Timeline",   2, 3, "Carla Diaz",  "mitigated",  7),
    ("Feature store schema change breaks downstream",     "Technical",  3, 3, "Ben Kim",     "open",       4),
    ("Key engineer on ranking team going on leave",       "Resource",   2, 4, "Ana Torres",  "accepted",   3),
]
cur.executemany(
    """INSERT INTO risks
       (title,category,probability,impact,owner,mitigation_status,days_open)
       VALUES (?,?,?,?,?,?,?)""",
    risks
)

# ── DEPENDENCIES ─────────────────────────────────────────────
dependencies = [
    ("Ranking",       "Infra",         "GPU cluster ready for online experiment",        random_date(5,10),   "at_risk",  2,  5),
    ("Ads Relevance", "Infra",         "Feature pipeline v3 live before retraining",     random_date(-2,2),   "delayed",  3, 10),
    ("Quality",       "Legal",         "Training data legal sign-off",                   random_date(5,15),   "at_risk",  7,  0),
    ("Ranking",       "Quality",       "Safety classifier cleared before model ship",    random_date(10,20),  "at_risk",  7,  0),
    ("Ads Relevance", "Quality",       "Spam model updated before ads relevance launch", random_date(3,8),    "on_track", 4,  0),
    ("Infra",         "Vendor",        "GPU hardware delivered on schedule",             random_date(-5,0),   "delayed",  6, 14),
    ("Ranking",       "Ads Relevance", "Shared embedding layer finalized",               random_date(15,25),  "on_track", 2,  0),
    ("Quality",       "Infra",         "New logging pipeline for quality signals",       random_date(-10,-3), "delayed", 11, 18),
    ("Ads Relevance", "Ranking",       "Pinner interest features available in store",    random_date(20,30),  "on_track", 9,  0),
    ("Infra",         "Data Eng",      "Batch pipeline migration sign-off",              random_date(0,5),    "at_risk",  5,  3),
    ("Ranking",       "Data Eng",      "Historical click data backfill complete",        random_date(5,12),   "on_track", 1,  0),
    ("Ads Relevance", "Finance",       "Budget approval for compute scaling",            random_date(-3,3),   "at_risk", 14,  7),
    ("Quality",       "Infra",         "Safety eval environment provisioned",            random_date(2,8),    "on_track", 7,  0),
    ("Ranking",       "Infra",         "Model serving capacity for retrieval model",     random_date(35,50),  "on_track",15,  0),
    ("Ads Relevance", "Infra",         "A/B test platform supports new metric schema",   random_date(8,15),   "at_risk",  4,  2),
]
cur.executemany(
    """INSERT INTO dependencies
       (from_team,to_team,description,due_date,status,milestone_id,delay_days)
       VALUES (?,?,?,?,?,?,?)""",
    dependencies
)

# ── LAUNCH READINESS ─────────────────────────────────────────
launch_gates = [
    ("Offline eval metrics meet bar",           "Quality",  "Ana Torres",  "complete",     1, past_date(5)),
    ("Online experiment statistical significance","Quality", "Ana Torres",  "in_progress",  1, past_date(2)),
    ("Guardrail metrics reviewed and approved",  "Quality",  "Ben Kim",     "in_progress",  1, past_date(1)),
    ("Safety classifier sign-off",               "Safety",   "David Park",  "blocked",      1, past_date(16)),
    ("Legal training data review complete",      "Legal",    "David Park",  "not_started",  1, past_date(11)),
    ("Privacy review approved",                  "Legal",    "Legal Team",  "complete",     1, past_date(8)),
    ("Model serving load test passed",           "Ops",      "Carla Diaz",  "in_progress",  1, past_date(3)),
    ("Rollback plan documented",                 "Ops",      "Carla Diaz",  "complete",     1, past_date(4)),
    ("On-call runbook updated",                  "Ops",      "Carla Diaz",  "complete",     0, past_date(6)),
    ("Latency P99 under 100ms in staging",       "Perf",     "Carla Diaz",  "complete",     1, past_date(7)),
    ("GPU capacity confirmed for launch scale",  "Perf",     "Carla Diaz",  "blocked",      1, past_date(22)),
    ("Experiment ramp plan approved",            "Quality",  "Ben Kim",     "complete",     1, past_date(3)),
    ("Leadership launch review scheduled",       "Quality",  "Ana Torres",  "complete",     0, past_date(2)),
    ("Ads policy compliance check",              "Legal",    "Legal Team",  "in_progress",  1, past_date(1)),
    ("Monitoring dashboards live",               "Ops",      "Carla Diaz",  "complete",     0, past_date(5)),
    ("Feature flag config reviewed",             "Ops",      "Sam Lee",     "complete",     0, past_date(4)),
    ("Post-launch success metrics defined",      "Quality",  "Ana Torres",  "complete",     0, past_date(6)),
    ("Incident escalation path confirmed",       "Ops",      "Carla Diaz",  "not_started",  0, past_date(1)),
]
cur.executemany(
    """INSERT INTO launch_readiness
       (gate_name,category,owner,status,is_blocking,last_updated)
       VALUES (?,?,?,?,?,?)""",
    launch_gates
)

conn.commit()
conn.close()
print("Database seeded successfully!")
print("Tables populated: milestones, experiments, jira_tickets, risks, dependencies, launch_readiness")