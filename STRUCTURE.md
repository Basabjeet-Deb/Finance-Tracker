# Project Structure

## Backend Structure ✅

```
backend/
├── app/
│   ├── main.py                    # FastAPI entry point with all endpoints
│   ├── routes/
│   │   ├── user.py               # Authentication (includes auth utilities)
│   │   ├── expenses.py           # Expense CRUD + Dashboard
│   │   └── analysis.py           # Financial analysis
│   ├── services/
│   │   ├── cpi_service.py        # CPI data fetching
│   │   ├── rule_engine.py        # Financial rules
│   │   └── optimizer.py          # Optimization engine
│   ├── models/
│   │   ├── user.py               # User model
│   │   └── expense.py            # Expense, Budget, CPI, Fuel models
│   ├── schemas/
│   │   └── __init__.py           # All Pydantic schemas
│   └── db/
│       └── database.py           # Database config
├── .env
├── .env.example
├── requirements.txt
├── scheduler.py
└── finance_tracker.db
```

## Key Points

- ✅ No test files in main structure
- ✅ No Docker files
- ✅ Auth utilities in user.py route
- ✅ All endpoints in main.py
- ✅ Clean, minimal structure
- ✅ Everything working in main

## Running

```bash
cd backend
uvicorn app.main:app --reload
```

## API Endpoints

All endpoints are defined in `app/main.py`:

- `/auth/signup` - Register
- `/auth/login` - Login
- `/expenses` - CRUD operations
- `/budget` - Budget management
- `/dashboard` - Analytics
- `/financial-analysis` - Financial analysis
- `/cpi` - CPI data
- `/external/cpi` - Basic CPI
- `/external/fuel` - Fuel prices

## File Count

- Routes: 3 files (user, expenses, analysis)
- Services: 3 files (cpi_service, rule_engine, optimizer)
- Models: 2 files (user, expense)
- Schemas: 1 file
- Database: 1 file
- Main: 1 file

**Total: 11 core files**
