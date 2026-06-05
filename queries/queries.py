# ═══════════════════════════════════════════════════════
# ML Program Health Tracker — Core SQL Queries
# ═══════════════════════════════════════════════════════

# ── SECTION 1: PROGRAM HEALTH ───────────────────────────

QUERY_WORKSTREAM_HEALTH = """
SELECT
    workstream,
    COUNT(*) AS total_milestones,
    SUM(CASE WHEN status = 'done' THEN 1 ELSE 0 END) AS completed,
    SUM(CASE WHEN status IN ('at_risk','delayed') THEN 1 ELSE 0 END) AS at_risk,
    ROUND(AVG(pct_complete), 1) AS avg_pct_complete,
    CASE
        WHEN SUM(CASE WHEN status='delayed' THEN 1 ELSE 0 END) > 0 THEN 'RED'
        WHEN SUM(CASE WHEN status='at_risk' THEN 1 ELSE 0 END) > 0  THEN 'YELLOW'
        ELSE 'GREEN'
    END AS rag_status
FROM milestones
GROUP BY workstream
ORDER BY rag_status DESC;
"""

QUERY_MILESTONE_BURNDOWN = """
SELECT
    m.name AS milestone,
    m.workstream,
    m.owner,
    m.due_date,
    m.pct_complete,
    m.status,
    COUNT(j.id) AS total_tickets,
    SUM(CASE WHEN j.status = 'done' THEN 1 ELSE 0 END) AS done_tickets,
    SUM(CASE WHEN j.is_blocker = 1 AND j.status != 'done' THEN 1 ELSE 0 END) AS open_blockers
FROM milestones m
LEFT JOIN jira_tickets j ON j.milestone_id = m.id
GROUP BY m.id
ORDER BY m.due_date ASC;
"""

# ── SECTION 2: AGING BLOCKERS ───────────────────────────

QUERY_AGING_BLOCKERS = """
SELECT
    j.title,
    j.assignee,
    j.team,
    j.priority,
    j.days_open,
    m.name AS milestone,
    CASE
        WHEN j.days_open > 14 THEN 'CRITICAL'
        WHEN j.days_open > 7  THEN 'ESCALATE'
        ELSE 'MONITOR'
    END AS aging_status
FROM jira_tickets j
LEFT JOIN milestones m ON j.milestone_id = m.id
WHERE j.is_blocker = 1
  AND j.status != 'done'
  AND j.days_open > 7
ORDER BY j.days_open DESC;
"""

QUERY_CRITICAL_TASKS = """
SELECT
    j.title,
    j.assignee,
    j.team,
    j.priority,
    j.status,
    j.days_open,
    m.name AS milestone
FROM jira_tickets j
JOIN milestones m ON j.milestone_id = m.id
WHERE j.priority IN ('P0', 'P1')
  AND j.status != 'done'
ORDER BY j.priority ASC, j.days_open DESC;
"""

# ── SECTION 3: RISK REGISTER ────────────────────────────

QUERY_TOP_RISKS = """
SELECT
    title,
    category,
    probability,
    impact,
    (probability * impact) AS risk_score,
    owner,
    mitigation_status,
    days_open
FROM risks
WHERE mitigation_status != 'mitigated'
ORDER BY (probability * impact) DESC
LIMIT 3;
"""

QUERY_RISK_HEATMAP = """
SELECT
    category,
    COUNT(*) AS total_risks,
    MAX(probability * impact) AS max_score,
    ROUND(AVG(probability * impact), 1) AS avg_score,
    SUM(CASE WHEN mitigation_status = 'open' THEN 1 ELSE 0 END) AS unmitigated
FROM risks
GROUP BY category
ORDER BY max_score DESC;
"""

QUERY_ALL_RISKS = """
SELECT
    title,
    category,
    probability,
    impact,
    (probability * impact) AS risk_score,
    owner,
    mitigation_status,
    days_open
FROM risks
ORDER BY (probability * impact) DESC;
"""

# ── SECTION 4: DEPENDENCIES ─────────────────────────────

QUERY_AT_RISK_DEPENDENCIES = """
SELECT
    d.from_team,
    d.to_team,
    d.description,
    d.due_date,
    d.status,
    d.delay_days,
    m.name AS milestone
FROM dependencies d
LEFT JOIN milestones m ON d.milestone_id = m.id
WHERE d.status IN ('at_risk', 'delayed')
ORDER BY d.delay_days DESC;
"""

QUERY_DEPENDENCY_RISK_SCORE = """
SELECT
    m.name AS milestone,
    m.workstream,
    COUNT(d.id) AS total_deps,
    SUM(CASE WHEN d.status = 'delayed' THEN 1 ELSE 0 END) AS delayed_deps,
    SUM(CASE WHEN d.status = 'at_risk' THEN 1 ELSE 0 END) AS at_risk_deps,
    SUM(CASE WHEN d.status='delayed' THEN 2 ELSE 0 END)
    + SUM(CASE WHEN d.status='at_risk' THEN 1 ELSE 0 END) AS dep_risk_score
FROM milestones m
LEFT JOIN dependencies d ON d.milestone_id = m.id
GROUP BY m.id
HAVING dep_risk_score > 0
ORDER BY dep_risk_score DESC;
"""

# ── SECTION 5: EXPERIMENTS ──────────────────────────────

QUERY_READY_TO_SCALE = """
SELECT
    name,
    model_version,
    workstream,
    ctr_delta_pct,
    save_rate_delta,
    ndcg_score,
    sample_size,
    days_running,
    'GRADUATE' AS recommendation
FROM experiments
WHERE status = 'running'
  AND ctr_delta_pct > 0.5
  AND save_rate_delta >= 0
  AND sample_size >= 50000
  AND days_running >= 7
ORDER BY ctr_delta_pct DESC;
"""

QUERY_STOP_EXPERIMENTS = """
SELECT
    name,
    model_version,
    ctr_delta_pct,
    save_rate_delta,
    days_running,
    'STOP — guardrail violation' AS recommendation
FROM experiments
WHERE status = 'running'
  AND ctr_delta_pct > 0
  AND save_rate_delta < -0.3
ORDER BY save_rate_delta ASC;
"""

QUERY_STALE_EXPERIMENTS = """
SELECT
    name,
    model_version,
    days_running,
    sample_size,
    ctr_delta_pct,
    'REVIEW — stale experiment' AS recommendation
FROM experiments
WHERE status = 'running'
  AND days_running > 21
  AND ABS(ctr_delta_pct) < 0.2
ORDER BY days_running DESC;
"""

QUERY_EXPERIMENT_SUMMARY = """
SELECT
    status,
    COUNT(*) AS count,
    ROUND(AVG(ctr_delta_pct), 2) AS avg_ctr_delta,
    ROUND(AVG(save_rate_delta), 2) AS avg_save_delta
FROM experiments
GROUP BY status
ORDER BY count DESC;
"""

QUERY_ALL_EXPERIMENTS = """
SELECT
    name,
    model_version,
    workstream,
    ctr_delta_pct,
    save_rate_delta,
    ndcg_score,
    days_running,
    sample_size,
    status,
    decision_log
FROM experiments
ORDER BY
    CASE status
        WHEN 'ready_to_scale' THEN 1
        WHEN 'running' THEN 2
        WHEN 'iterate' THEN 3
        WHEN 'stopped' THEN 4
    END,
    ctr_delta_pct DESC;
"""

# ── SECTION 6: LAUNCH READINESS ─────────────────────────

QUERY_LAUNCH_GATE_STATUS = """
SELECT
    category,
    COUNT(*) AS total_gates,
    SUM(CASE WHEN status = 'complete' THEN 1 ELSE 0 END) AS complete,
    SUM(CASE WHEN status != 'complete' AND is_blocking = 1 THEN 1 ELSE 0 END) AS blocking_open,
    ROUND(100.0 * SUM(CASE WHEN status='complete' THEN 1 ELSE 0 END) / COUNT(*), 0) AS pct_complete
FROM launch_readiness
GROUP BY category
ORDER BY blocking_open DESC;
"""

QUERY_BLOCKING_ITEMS = """
SELECT
    gate_name,
    category,
    owner,
    status,
    last_updated
FROM launch_readiness
WHERE is_blocking = 1
  AND status != 'complete'
ORDER BY category, status;
"""

QUERY_LAUNCH_DECISION = """
SELECT
    CASE
        WHEN SUM(CASE WHEN is_blocking=1 AND status!='complete' THEN 1 ELSE 0 END) = 0
        THEN 'GO'
        ELSE 'NO-GO — ' ||
             SUM(CASE WHEN is_blocking=1 AND status!='complete' THEN 1 ELSE 0 END) ||
             ' blocking items open'
    END AS launch_decision,
    SUM(CASE WHEN status='complete' THEN 1 ELSE 0 END) || '/' ||
    COUNT(*) AS gates_complete
FROM launch_readiness;
"""