# Backend - Personal Finance Tracker

FastAPI backend with clean architecture and inflation-aware financial optimization.

## Structure

```
app/
├── main.py                    # FastAPI entry point + all endpoints
├── routes/
│   ├── user.py               # Authentication
│   ├── expenses.py           # Expense CRUD + Dashboard
│   └── analysis.py           # Financial analysis
├── services/
│   ├── cpi_service.py        # CPI data fetching
│   ├── inflation_engine.py   # Inflation decision engine
│   ├── rule_engine.py        # Financial rules
│   └── optimizer.py          # Optimization engine
├── models/
│   ├── user.py
│   └── expense.py
├── schemas/
│   └── __init__.py
└── db/
    └── database.py
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Server: http://localhost:8000
Docs: http://localhost:8000/docs

## Key Features

### Inflation Decision Engine
Transforms CPI data into actionable financial logic:

- **Inflation Pressure**: Calculates low/medium/high from YoY inflation
- **Dynamic Thresholds**: Adjusts budgets based on inflation (high inflation: +5% essential, -5% lifestyle)
- **Category Impact**: High sensitivity (Food, Transport) vs Low (Entertainment)
- **Specific Insights**: "Reduce lifestyle by ₹2,500/month" not "save more"

### API Endpoints

**Auth**
- POST /auth/signup
- POST /auth/login

**Expenses**
- GET /expenses
- POST /expenses
- PUT /expenses/{id}
- DELETE /expenses/{id}

**Budget**
- POST /budget
- GET /budget/{month}

**Analytics**
- GET /dashboard
- POST /financial-analysis (inflation-adjusted)
- GET /financial-health

**Inflation**
- GET /inflation/pressure
- GET /inflation/thresholds

**External Data**
- GET /cpi
- POST /cpi/refresh
- GET /external/cpi
- GET /external/fuel

## Environment Variables

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./finance_tracker.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
