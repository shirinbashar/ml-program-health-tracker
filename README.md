# 📊 ML Program Health Tracker

> A SQL-backed TPM dashboard simulating AI/ML program health tracking:
> experiment lifecycle management, milestone burn-down, blocker aging,
> dependency risk scoring, and auto-generated executive summaries.



---

## 🎯 Project Framing

"I built a lightweight SQL-backed TPM dashboard to model how I would track
program health for an AI/ML launch: milestones, blockers, risks, dependencies,
experiment results, and launch readiness. The goal was to turn raw execution
data into decisions and leadership-ready reporting."

This project demonstrates:
- **SQL proficiency** — 15 queries answering real TPM decision questions
- **Dashboard creation** — 6-section Streamlit app matching a real program review cadence
- **ML experimentation thinking** — experiment graduation logic including guardrail metric checks
- **Leadership reporting** — auto-generated exec summary from live query results

---

## 📸 Dashboard Preview

### Program Health Summary
<img width="1752" height="437" alt="image" src="https://github.com/user-attachments/assets/b5c46282-5126-406d-94b4-ba1a6015f4ae" />


### Aging Blockers
<img width="1782" height="797" alt="image" src="https://github.com/user-attachments/assets/7af48e0a-43a1-4fa6-81bd-5cda219688fc" />


### Risk Register
<img width="1777" height="752" alt="image" src="https://github.com/user-attachments/assets/78caa7ae-c8e8-4ec8-a97a-9ede8025a49b" />


### Experiment Decisions
<img width="1772" height="810" alt="image" src="https://github.com/user-attachments/assets/e4574051-f092-410c-bd1e-dcd37648769b" />


### Launch Readiness
<img width="1741" height="840" alt="image" src="https://github.com/user-attachments/assets/c3729634-179a-40a8-acbe-85f50caee9d2" />


### Executive Summary
<img width="1766" height="682" alt="image" src="https://github.com/user-attachments/assets/7ee8487a-0714-41b7-b35a-c23020f316ac" />


---

## 🗂️ Schema

6 tables covering the full lifecycle of a TPM-managed ML launch:

| Table | Purpose |
|---|---|
| `milestones` | Program milestones by workstream with RAG status |
| `experiments` | ML experiment tracker with offline + online metrics |
| `jira_tickets` | Tasks and blockers linked to milestones |
| `risks` | Risk register with probability × impact scoring |
| `dependencies` | Cross-team dependencies with delay tracking |
| `launch_readiness` | Launch gate checklist with blocking item flags |

---

## 🔍 Key Questions This Dashboard Answers

1. Which workstreams are RED / YELLOW / GREEN right now?
2. Which blockers have been open more than 7 days — and who owns them?
3. What are the top 3 risks I should put in front of leadership?
4. Which experiments are ready to graduate to production?
5. Which experiments should I STOP despite a positive primary metric?
6. Is the program GO or NO-GO for launch?
7. What is the auto-generated exec summary for my leadership review?

---

## 🚀 How to Run Locally

**Requirements:** Python 3.8+

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/ml-program-health-tracker.git
cd ml-program-health-tracker
```

**2. Install dependencies**
```bash
pip install streamlit pandas faker
```

**3. Seed the database**
```bash
python data/seed.py
```

**4. Launch the dashboard**
```bash
python -m streamlit run dashboard/app.py
```

**5. Open your browser to:** `http://localhost:8501`

---

## 📁 Project Structure
ml-program-health-tracker/
├── data/
│   ├── schema.sql        # DDL for all 6 tables
│   ├── seed.py           # Realistic fake data generator
│   └── program_health.db # SQLite database
├── queries/
│   └── queries.py        # 15 SQL queries as Python constants
├── dashboard/
│   └── app.py            # Streamlit dashboard (6 sections)
├── assets/               # Screenshots for README
└── README.md
