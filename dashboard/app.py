import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from queries.queries import *

# ── PAGE CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="ML Program Health Tracker",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ML Program Health Tracker")
st.caption("Pinterest ATG TPM II — Interview Portfolio Project | " + str(date.today()))

# ── DB CONNECTION ────────────────────────────────────────
@st.cache_resource
def get_connection():
    return sqlite3.connect("data/program_health.db", check_same_thread=False)

conn = get_connection()

# ── HELPER: RAG COLOR ────────────────────────────────────
def rag_color(val):
    if val == "RED":
        return "background-color: #FFCCCC"
    elif val == "YELLOW":
        return "background-color: #FFF3CC"
    elif val == "GREEN":
        return "background-color: #CCFFCC"
    return ""

def aging_color(val):
    if val == "CRITICAL":
        return "background-color: #FFCCCC; font-weight: bold"
    elif val == "ESCALATE":
        return "background-color: #FFF3CC"
    return ""

# ════════════════════════════════════════════════════════
# SECTION 1: PROGRAM HEALTH SUMMARY
# ════════════════════════════════════════════════════════
st.header("🟢 Program Health Summary")

df_health = pd.read_sql(QUERY_WORKSTREAM_HEALTH, conn)
df_burn = pd.read_sql(QUERY_MILESTONE_BURNDOWN, conn)

col1, col2, col3, col4 = st.columns(4)
total = len(df_burn)
on_track = len(df_burn[df_burn["status"] == "on_track"])
at_risk = len(df_burn[df_burn["status"] == "at_risk"])
delayed = len(df_burn[df_burn["status"] == "delayed"])

col1.metric("Total Milestones", total)
col2.metric("On Track", on_track, delta=None)
col3.metric("At Risk", at_risk, delta=f"-{at_risk}" if at_risk > 0 else None, delta_color="inverse")
col4.metric("Delayed", delayed, delta=f"-{delayed}" if delayed > 0 else None, delta_color="inverse")

st.subheader("Workstream RAG Status")
styled = df_health.style.applymap(rag_color, subset=["rag_status"])
st.dataframe(styled, use_container_width=True, hide_index=True)

st.subheader("Milestone Burn-Down")
st.dataframe(df_burn, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════
# SECTION 2: AGING BLOCKERS
# ════════════════════════════════════════════════════════
st.header("🔴 Aging Blockers")

df_blockers = pd.read_sql(QUERY_AGING_BLOCKERS, conn)
df_critical = pd.read_sql(QUERY_CRITICAL_TASKS, conn)

col1, col2 = st.columns(2)
col1.metric("Blockers Open > 7 Days", len(df_blockers))
critical_count = len(df_blockers[df_blockers["aging_status"] == "CRITICAL"])
col2.metric("CRITICAL (>14 days)", critical_count)

st.subheader("Blockers Requiring Action")
if len(df_blockers) > 0:
    styled_b = df_blockers.style.applymap(aging_color, subset=["aging_status"])
    st.dataframe(styled_b, use_container_width=True, hide_index=True)
else:
    st.success("No blockers open > 7 days!")

st.subheader("All Open P0 / P1 Tasks")
st.dataframe(df_critical, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════
# SECTION 3: RISK REGISTER
# ════════════════════════════════════════════════════════
st.header("⚠️ Risk Register")

df_top3 = pd.read_sql(QUERY_TOP_RISKS, conn)
df_heatmap = pd.read_sql(QUERY_RISK_HEATMAP, conn)
df_all_risks = pd.read_sql(QUERY_ALL_RISKS, conn)

st.subheader("🚨 Top 3 Risks for Leadership")
for _, row in df_top3.iterrows():
    score = row["risk_score"]
    color = "🔴" if score >= 16 else "🟡" if score >= 9 else "🟢"
    with st.expander(f"{color} [{row['category']}] {row['title']} — Score: {score}/25"):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Probability", f"{row['probability']}/5")
        c2.metric("Impact", f"{row['impact']}/5")
        c3.metric("Risk Score", f"{score}/25")
        c4.metric("Status", row["mitigation_status"].upper())
        st.write(f"**Owner:** {row['owner']} | **Days Open:** {row['days_open']}")

st.subheader("Risk Category Heatmap")
st.dataframe(df_heatmap, use_container_width=True, hide_index=True)

st.subheader("Full Risk Register")
st.dataframe(df_all_risks, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════
# SECTION 4: DEPENDENCY MAP
# ════════════════════════════════════════════════════════
st.header("🔗 Dependency Map")

df_deps = pd.read_sql(QUERY_AT_RISK_DEPENDENCIES, conn)
df_dep_scores = pd.read_sql(QUERY_DEPENDENCY_RISK_SCORE, conn)

col1, col2 = st.columns(2)
delayed_deps = len(df_deps[df_deps["status"] == "delayed"])
atrisk_deps = len(df_deps[df_deps["status"] == "at_risk"])
col1.metric("Delayed Dependencies", delayed_deps)
col2.metric("At-Risk Dependencies", atrisk_deps)

st.subheader("At-Risk & Delayed Dependencies")
if len(df_deps) > 0:
    def dep_color(val):
        if val == "delayed":
            return "background-color: #FFCCCC"
        elif val == "at_risk":
            return "background-color: #FFF3CC"
        return ""
    styled_d = df_deps.style.applymap(dep_color, subset=["status"])
    st.dataframe(styled_d, use_container_width=True, hide_index=True)
else:
    st.success("No at-risk dependencies!")

st.subheader("Dependency Risk Score by Milestone")
st.dataframe(df_dep_scores, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════
# SECTION 5: EXPERIMENT DECISIONS
# ════════════════════════════════════════════════════════
st.header("🧪 Experiment Decisions")

df_graduate = pd.read_sql(QUERY_READY_TO_SCALE, conn)
df_stop = pd.read_sql(QUERY_STOP_EXPERIMENTS, conn)
df_stale = pd.read_sql(QUERY_STALE_EXPERIMENTS, conn)
df_all_exp = pd.read_sql(QUERY_ALL_EXPERIMENTS, conn)
df_exp_summary = pd.read_sql(QUERY_EXPERIMENT_SUMMARY, conn)

col1, col2, col3 = st.columns(3)
col1.metric("✅ Ready to Graduate", len(df_graduate), delta="Ship these")
col2.metric("🛑 Guardrail Violations", len(df_stop), delta="Stop these", delta_color="inverse")
col3.metric("⏸️ Stale (No Signal)", len(df_stale), delta="Review these", delta_color="off")

if len(df_graduate) > 0:
    st.subheader("✅ Graduate to Production")
    st.dataframe(df_graduate, use_container_width=True, hide_index=True)

if len(df_stop) > 0:
    st.subheader("🛑 STOP — Guardrail Metric Degradation")
    st.warning("These experiments show primary metric improvement BUT a guardrail metric has degraded. Do NOT ship.")
    st.dataframe(df_stop, use_container_width=True, hide_index=True)

if len(df_stale) > 0:
    st.subheader("⏸️ Stale Experiments — Review & Decide")
    st.dataframe(df_stale, use_container_width=True, hide_index=True)

st.subheader("All Experiments")
st.dataframe(df_all_exp, use_container_width=True, hide_index=True)

st.divider()

# ════════════════════════════════════════════════════════
# SECTION 6: LAUNCH READINESS + EXEC SUMMARY
# ════════════════════════════════════════════════════════
st.header("🚀 Launch Readiness")

df_gates = pd.read_sql(QUERY_LAUNCH_GATE_STATUS, conn)
df_blocking = pd.read_sql(QUERY_BLOCKING_ITEMS, conn)
df_decision = pd.read_sql(QUERY_LAUNCH_DECISION, conn)

launch_decision = df_decision.iloc[0]["launch_decision"]
gates_complete = df_decision.iloc[0]["gates_complete"]

if launch_decision == "GO":
    st.success(f"## ✅ LAUNCH DECISION: GO  |  Gates: {gates_complete}")
else:
    st.error(f"## ❌ LAUNCH DECISION: {launch_decision}  |  Gates: {gates_complete}")

st.subheader("Gate Status by Category")
st.dataframe(df_gates, use_container_width=True, hide_index=True)

if len(df_blocking) > 0:
    st.subheader("🚧 Blocking Items Not Complete")
    st.dataframe(df_blocking, use_container_width=True, hide_index=True)

st.divider()

# ── EXEC SUMMARY ─────────────────────────────────────────
st.header("📋 Executive Summary")
st.caption("Auto-generated from live query results")

n_critical_blockers = len(df_blockers[df_blockers["aging_status"] == "CRITICAL"])
n_escalate_blockers = len(df_blockers[df_blockers["aging_status"] == "ESCALATE"])
top_risk_title = df_top3.iloc[0]["title"] if len(df_top3) > 0 else "None identified"
top_risk_score = df_top3.iloc[0]["risk_score"] if len(df_top3) > 0 else 0
n_graduate = len(df_graduate)
n_stop = len(df_stop)
n_delayed_deps = delayed_deps

red_ws = df_health[df_health["rag_status"] == "RED"]["workstream"].tolist()
yellow_ws = df_health[df_health["rag_status"] == "YELLOW"]["workstream"].tolist()

health_line = ""
if red_ws:
    health_line += f"**{', '.join(red_ws)}** {'is' if len(red_ws)==1 else 'are'} RED. "
if yellow_ws:
    health_line += f"**{', '.join(yellow_ws)}** {'is' if len(yellow_ws)==1 else 'are'} YELLOW. "
if not red_ws and not yellow_ws:
    health_line = "All workstreams are GREEN. "

summary = f"""
**Program Status — {date.today()}**

**Overall Health:** {health_line}

**Blockers:** {n_critical_blockers} critical blocker(s) open >14 days requiring immediate escalation.
{n_escalate_blockers} additional blocker(s) open >7 days requiring owner follow-up.

**Top Risk:** {top_risk_title} (score: {top_risk_score}/25). See risk register for full mitigation status.

**Dependencies:** {n_delayed_deps} delayed dependency/dependencies impacting milestone delivery.

**Experiments:** {n_graduate} experiment(s) ready to graduate to production.
{n_stop} experiment(s) flagged for guardrail metric violations — recommend stopping despite positive primary metric.

**Launch Decision:** {launch_decision} | {gates_complete} gates complete.
"""

st.markdown(summary)

st.download_button(
    label="📥 Download Exec Summary",
    data=summary,
    file_name=f"exec_summary_{date.today()}.md",
    mime="text/markdown"
)