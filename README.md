# SahakarAI — Collective Intelligence for Weaver Cooperatives

A runnable Streamlit prototype demonstrating three modular agents: demand forecasting, cooperative supply aggregation, and policy-constrained negotiation. Includes SQLite persistence, pricing calculations, officer review, audit logs, synthetic seed data and CSV exports.

## Requirements
- Python 3.10+
- Internet only if installing dependencies; the app itself uses no external API.

## Run locally

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal (normally http://localhost:8501).

## 3-minute demo
1. Overview: show seeded demand and capacity charts.
2. Demand Intelligence: select a product and generate a forecast.
3. Bulk Orders: create a 100-unit order, generate allocation, review cost and save it.
4. Negotiation: select the order and evaluate a below-target or below-floor buyer offer.
5. Officer Approvals: record a decision with a reason.
6. Audit & Reports: show the saved audit events and export CSV.

Use the sidebar's **Load Demo Scenario** button to reset seed data. The database is `sahakarai.db` in the project folder. Set `SAHAKARAI_DB` to use another path.

## Important scope notes
- All people, costs, historical demand and buyers are simulated.
- Forecasting is a transparent moving-average baseline, not a validated market forecast.
- Allocation uses a simple greedy cost/capacity ordering, not a globally optimal solver.
- The LLM integration is intentionally optional; the deterministic negotiation agent works without an API key.
- Demo officer role selection is not production authentication. Add real authentication, authorisation, data protection and legal review before real-world use.
- The cost-floor check is based on configured order costs. Real cooperatives should approve the shared-expense allocation method and individual compensation rules.
