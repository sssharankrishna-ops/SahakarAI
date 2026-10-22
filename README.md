 SahakarAI — Collective Bargaining for Weaver Cooperatives
SahakarAI is a hackathon prototype that helps handloom-weaver cooperatives plan demand, combine production capacity for bulk orders, estimate sustainable prices, and review buyer offers before making a decision.
Prototype status: This demo uses synthetic data and transparent, rule-based logic. It is intended for demonstration and evaluation, not for making real commercial commitments.

What the prototype demonstrates
- Weaver registry: View the participating sample weavers, product types, capacities, costs, and quality levels.
- Demand intelligence: Generate a simple demand estimate from historical sample data.
- Bulk-order aggregation: Allocate an order across available weaver capacity and show any unmet quantity.
- Price protection: Estimate production costs, shared expenses, break-even pricing, and a target price.
- Negotiation support: Evaluate a buyer's offer using price and payment-delay rules, and provide a suggested next action.
- Officer approvals: Record a review decision and reason.
- Audit and reports: Review recorded events and export data as CSV.
Architecture at a glance
The application is organised into three main layers:
User
  |
  v
app.py  — Streamlit screens, forms, workflow and results
  |
  +----------------------+
  |                      |
  v                      v
agents.py              db.py
Forecasting            SQLite connection, schema,
Allocation             queries, writes and audit log
Pricing                  |
Negotiation              v
  |                  sahakarai.db
  +------ results/data ---+
What happens when a bulk order is created?
1. The user enters the product, quantity, quality requirement, and deadline in the Bulk Orders page.
2. app.py passes the relevant order details and available weaver information to AggregationAgent in agents.py.
3. The allocation logic assigns quantities based on the eligible weavers' available capacity and cost ordering. If capacity is insufficient, the result identifies the shortage.
4. PricingEngine calculates the order's estimated production cost, shared expenses, break-even amount, and target price.
5. app.py displays the proposed allocation and pricing information. When the user saves the order, the application records the order and allocations through db.py in SQLite.
6. Related actions can then be reviewed through the pricing, negotiation, approval, and audit pages.
Project file guide
File	Responsibility	When you would change it
app.py	Streamlit interface, page navigation, forms, button actions, and coordination between logic and database	Add or modify a page, form, displayed result, or user workflow
agents.py	Core decision logic: forecasting, order allocation, pricing, and negotiation	Change a forecast method, capacity allocation rule, price calculation, or offer evaluation rule
db.py	SQLite database path, table creation, seed data, queries, writes, and audit records	Add a stored field/table or change database read/write behaviour
test_agents.py	Automated tests for core business logic	Add or update tests after changing a rule
requirements.txt	Python package dependencies	Add a required third-party Python package
.env.example	Example environment configuration, including an optional database path	Document an additional environment variable
.gitignore	Files and local artefacts Git should ignore	Exclude additional local or generated files
README.md	Setup instructions, architecture, demo guide, and project limitations	Update project documentation


Main components in agents.py
- ForecastingAgent.forecast(...) — creates a baseline forecast from historical demand values.
- AggregationAgent.allocate(...) — proposes a capacity-aware allocation for a product and order quantity.
- PricingEngine.calculate(...) — calculates production cost, shared expenses, and price thresholds.
- NegotiationAgent.evaluate(...) — evaluates a buyer offer against the supplied pricing and payment conditions.
Database tables
db.py creates tables for weavers, demand, orders, allocations, offers, approvals, and audit. The default database file is sahakarai.db in the project folder. The database path can be overridden with the SAHAKARAI_DB environment variable.
Where to make a change
Use this as a quick guide during a code walkthrough:
Requested change	Start here	Also check
Add a dashboard page or change a form	app.py	db.py if new data must be saved
Change demand forecasting	ForecastingAgent in agents.py	Demand page in app.py; tests in test_agents.py
Change bulk-order allocation	AggregationAgent in agents.py	Bulk Orders workflow in app.py; allocation tests
Change target price or cost calculation	PricingEngine in agents.py	Price Protection and Negotiation pages in app.py
Change buyer-offer or payment-delay rules	NegotiationAgent in agents.py	Offer display/save flow in app.py; tests
Store a new property	db.py	Every relevant insert/query and form in app.py
Add a dependency	requirements.txt	Installation instructions if needed


API note: The current prototype is a Streamlit application. It does not expose a separate REST API or HTTP endpoints. When describing a change, refer to the relevant page, workflow, class, or method rather than claiming a REST endpoint exists.
Requirements
- Python 3.10 or newer
- Internet access only to install the Python packages; the application itself does not call an external service
Run locally
Windows PowerShell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
If PowerShell blocks environment activation, you can run the environment's executable directly instead:
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\streamlit.exe run app.py
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
Open the local URL printed in the terminal. It is normally http://localhost:8501.
Suggested live demo (3–5 minutes)
1. Overview: Introduce the problem and show the sample demand and capacity overview.
2. Weavers: Explain that the prototype starts with synthetic weaver records.
3. Demand Intelligence: Select a product and generate a forecast.
4. Bulk Orders: Create an example order, generate an allocation, explain capacity constraints, and save it.
5. Price Protection: Explain estimated cost, break-even price, and target price.
6. Negotiation: Evaluate a buyer offer and explain why the rules recommend an action.
7. Officer Approvals: Record a review decision and reason.
8. Audit & Reports: Show the recorded events and demonstrate a CSV export.
Use Load Demo Scenario in the sidebar to reload the sample scenario. This reset action is for the demo and should not be used with data that needs to be retained.
Run the tests
From the project directory, run:
python -m unittest -v
The tests cover key behaviours such as forecasting, allocation capacity, shortage reporting, below-floor offer handling, and long-payment-delay escalation.
Current limitations and future work
- Synthetic data: Weaver profiles, demand history, costs, and buyer offers are demonstration data, not live market information.
- Forecasting: The forecast is a simple historical baseline. It has not been validated against real-world outcomes and is not a trained machine-learning model.
- Allocation: The allocator uses a greedy cost/capacity strategy. It is not guaranteed to find the globally optimal allocation for every order.
- Negotiation: Offer evaluation is deterministic and rule-based. An external LLM is not required or currently connected in the core workflow.
- Security: The demo officer-role selection is not production-grade authentication or authorisation.
- Commercial safeguards: Before real use, enforce pricing and approval policies in every relevant decision path, validate the cost-sharing and compensation model with cooperatives, and add proper permissions, privacy controls, transaction safeguards, and legal review.
- Future extensions: Real demand and market-price integrations, validated forecasting models, a production database such as PostgreSQL, stronger authentication, and field testing with cooperatives.
Project principle
SahakarAI is designed to support collective decisions by making capacity, estimated costs, price thresholds, and offer trade-offs easier to inspect. The cooperative remains responsible for reviewing and approving real-world commercial decisions.