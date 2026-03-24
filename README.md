# Finance Tracker India 🇮🇳

AI-powered Personal Finance Tracker with rule-based optimization for Indian users. Built with FastAPI, Next.js, and Supabase PostgreSQL.

## System Architecture

```mermaid
graph TB
    subgraph "Frontend - Next.js 14"
        UI[React Components]
        Pages[Pages: Dashboard, Expenses, Insights, Login]
        API_Client[API Client - Axios]
        Auth_Client[Supabase Auth Client]
        UI --> Pages
        Pages --> API_Client
        Pages --> Auth_Client
    end

    subgraph "Backend - FastAPI"
        Main[main.py - FastAPI App]
        
        subgraph "Routes Layer"
            UserRoutes[user.py - Auth & Profile]
            ExpenseRoutes[expenses.py - CRUD]
            AnalysisRoutes[analysis.py - Financial Analysis]
            UnifiedRoutes[unified_analysis.py - Unified API]
        end
        
        subgraph "Services Layer"
            FinEngine[financial_engine.py<br/>Decision Engine]
            RuleEngine[rule_engine.py<br/>Constraint Evaluation]
            Optimizer[optimizer.py<br/>Recommendations]
            InflationEngine[inflation_engine.py<br/>Inflation Analysis]
            CPIService[cpi_service.py<br/>CPI Data Fetching]
            RBIService[rbi_service.py<br/>RBI Rate Scraping]
            FuelService[fuel_service.py<br/>Fuel Price Scraping]
            DealsService[deals_service.py<br/>Cost Optimization]
        end
        
        subgraph "Data Layer"
            Models[SQLAlchemy Models]
            Database[database.py<br/>Connection Pool]
        end
        
        Main --> UserRoutes
        Main --> ExpenseRoutes
        Main --> AnalysisRoutes
        Main --> UnifiedRoutes
        
        UserRoutes --> Models
        ExpenseRoutes --> Models
        AnalysisRoutes --> FinEngine
        UnifiedRoutes --> FinEngine
        
        FinEngine --> RuleEngine
        FinEngine --> Optimizer
        FinEngine --> InflationEngine
        FinEngine --> CPIService
        FinEngine --> DealsService
        
        InflationEngine --> CPIService
        
        Models --> Database
        CPIService --> Database
        RBIService --> Database
        FuelService --> Database
    end

    subgraph "Database - Supabase PostgreSQL"
        Users[(users)]
        Expenses[(expenses)]
        Budgets[(budgets)]
        CPIData[(cpi_data)]
        FuelData[(fuel_data)]
        AnalysisHistory[(analysis_history)]
    end

    subgraph "External APIs"
        DataGovAPI[data.gov.in<br/>CPI Data API]
        RBIWebsite[rbi.org.in<br/>Repo Rate]
        FuelWebsite[goodreturns.in<br/>Fuel Prices]
    end

    subgraph "Background Jobs"
        Scheduler[APScheduler<br/>Monthly Data Refresh]
    end

    API_Client -->|HTTP/REST| Main
    Auth_Client -->|JWT Auth| UserRoutes
    
    Database --> Users
    Database --> Expenses
    Database --> Budgets
    Database --> CPIData
    Database --> FuelData
    Database --> AnalysisHistory
    
    CPIService -->|Fetch CPI| DataGovAPI
    RBIService -->|Scrape Rate| RBIWebsite
    FuelService -->|Scrape Prices| FuelWebsite
    
    Scheduler -->|Trigger| CPIService
    Scheduler -->|Trigger| FuelService
    
    style FinEngine fill:#4F46E5,stroke:#312E81,color:#fff
    style Main fill:#10B981,stroke:#065F46,color:#fff
    style Database fill:#3B82F6,stroke:#1E40AF,color:#fff
    style Scheduler fill:#F59E0B,stroke:#B45309,color:#fff
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant FastAPI
    participant FinancialEngine
    participant Database
    participant ExternalAPIs

    User->>Frontend: Login
    Frontend->>FastAPI: POST /auth/login
    FastAPI->>Database: Verify credentials
    Database-->>FastAPI: User data
    FastAPI-->>Frontend: JWT Token
    
    User->>Frontend: Add Expense
    Frontend->>FastAPI: POST /expenses
    FastAPI->>Database: Insert expense
    Database-->>FastAPI: Success
    FastAPI-->>Frontend: Expense created
    
    User->>Frontend: View Dashboard
    Frontend->>FastAPI: GET /dashboard
    FastAPI->>Database: Fetch expenses
    Database-->>FastAPI: Expense data
    FastAPI-->>Frontend: Dashboard data
    
    User->>Frontend: Get Financial Analysis
    Frontend->>FastAPI: GET /financial-analysis
    FastAPI->>Database: Fetch user expenses
    Database-->>FastAPI: Expenses
    FastAPI->>FinancialEngine: analyze_finances()
    FinancialEngine->>Database: Get CPI data
    Database-->>FinancialEngine: Inflation data
    FinancialEngine->>FinancialEngine: Calculate risk score
    FinancialEngine->>FinancialEngine: Detect violations
    FinancialEngine->>FinancialEngine: Generate recommendations
    FinancialEngine-->>FastAPI: FinancialDecision
    FastAPI->>Database: Save analysis history
    FastAPI-->>Frontend: Analysis results
    
    Note over FastAPI,ExternalAPIs: Background Job (Monthly)
    FastAPI->>ExternalAPIs: Fetch CPI data
    ExternalAPIs-->>FastAPI: Latest CPI
    FastAPI->>Database: Update CPI data
```

## Database Schema

```mermaid
erDiagram
    users ||--o{ expenses : "has many"
    users ||--o{ budgets : "has many"
    users ||--o{ analysis_history : "has many"
    
    users {
        uuid id PK
        string email UK
        float income
        int dependents
        string medical_risk
        timestamp created_at
        timestamp updated_at
    }
    
    expenses {
        uuid id PK
        uuid user_id FK
        float amount
        string category
        string subcategory
        string type
        date date
        string note
        timestamp created_at
        timestamp updated_at
    }
    
    budgets {
        uuid id PK
        uuid user_id FK
        float monthly_budget
        string month
        timestamp created_at
        timestamp updated_at
    }
    
    cpi_data {
        uuid id PK
        string month UK
        float value
        timestamp created_at
        timestamp updated_at
    }
    
    fuel_data {
        uuid id PK
        date date UK
        float petrol_price
        float diesel_price
        timestamp created_at
        timestamp updated_at
    }
    
    analysis_history {
        uuid id PK
        uuid user_id FK
        int score
        string risk_level
        float savings_rate
        json inflation_data
        json percentages
        json money_leaks
        json recommendations
        timestamp created_at
    }
```

## Features

- 💰 Expense tracking with categories
- 📊 Real-time dashboard with charts
- 🤖 AI-powered financial recommendations
- 📈 India CPI inflation tracking
- ⛽ Live fuel price monitoring
- 🏦 RBI repo rate tracking
- 🎯 Rule-based budget optimization
- 🔐 Secure authentication (JWT)
- 🗄️ Production-ready Supabase PostgreSQL

## Tech Stack

### Backend
- FastAPI (Python)
- SQLAlchemy ORM
- Supabase PostgreSQL
- JWT Authentication
- APScheduler (background tasks)

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- Recharts
- Framer Motion

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Supabase account (free tier)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Environment is already configured in .env
# Start backend
python -m app.main
```

Backend runs on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend runs on http://localhost:3001

### 3. Login

- Email: `admin@admin.com`
- Password: `admin123`

## Project Structure

```
finance-tracker-india/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   └── database.py          # Supabase PostgreSQL config
│   │   ├── models/
│   │   │   ├── user.py              # User model (UUID)
│   │   │   └── expense.py           # Expense, Budget, CPI models
│   │   ├── routes/
│   │   │   ├── user.py              # Auth endpoints
│   │   │   ├── expenses.py          # Expense CRUD
│   │   │   └── analysis.py          # Financial analysis
│   │   ├── services/
│   │   │   ├── financial_engine.py  # Main decision engine
│   │   │   ├── rule_engine.py       # Budget rules
│   │   │   ├── optimizer.py         # Optimization logic
│   │   │   ├── inflation_engine.py  # Inflation analysis
│   │   │   ├── cpi_service.py       # CPI data fetching
│   │   │   ├── rbi_service.py       # RBI rate scraping
│   │   │   ├── fuel_service.py      # Fuel price scraping
│   │   │   └── deals_service.py     # Personalized deals
│   │   └── main.py                  # FastAPI app
│   ├── .env                         # Environment config
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/
    │   │   ├── dashboard/           # Main dashboard
    │   │   ├── insights/            # Detailed insights
    │   │   ├── expenses/            # Expense management
    │   │   └── login/               # Login page
    │   ├── components/
    │   │   ├── Navbar.tsx
    │   │   └── Sidebar.tsx
    │   └── lib/
    │       ├── api.ts               # API client
    │       └── auth.ts              # Auth utilities
    └── package.json
```

## API Endpoints

### Authentication
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login

### Expenses
- `GET /expenses` - List expenses
- `POST /expenses` - Create expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense

### Dashboard
- `GET /dashboard` - Dashboard data
- `GET /financial-analysis` - Financial insights

### Health
- `GET /health` - Application health
- `GET /health/db` - Database health

### External Data
- `GET /cpi` - CPI data with inflation
- `POST /cpi/refresh` - Refresh CPI data
- `GET /inflation/pressure` - Inflation pressure
- `GET /inflation/thresholds` - Adjusted thresholds

## Financial Decision Engine

The core of the application is a rule-based financial decision engine that:

1. **Categorizes Expenses**: Fixed, Essential, Lifestyle, Savings
2. **Analyzes Inflation**: Uses real India CPI data
3. **Adjusts Thresholds**: Dynamic based on inflation and user profile
4. **Detects Issues**: Money leaks, budget violations
5. **Calculates Risk**: 0-100 score with risk level
6. **Generates Recommendations**: Specific actions with ₹ amounts
7. **Prioritizes Actions**: Top 3 urgent recommendations

### Example Analysis Response

```json
{
  "risk_level": "medium",
  "risk_score": 45,
  "savings_rate": 15.5,
  "inflation": {
    "pressure": "medium",
    "value": 4.85,
    "status": "actual"
  },
  "spending_summary": {
    "fixed_obligations": {"percentage": 40, "amount": 20000},
    "essentials": {"percentage": 25, "amount": 12500},
    "lifestyle": {"percentage": 15, "amount": 7500},
    "savings": {"percentage": 20, "amount": 10000}
  },
  "recommendations": [
    "Increase monthly savings by ₹2,500 to reach 20% target",
    "Reduce lifestyle spending by ₹3,000 per month",
    "Monitor Food spending (₹8,000/month) - inflation impact of 7.3%"
  ],
  "priority_actions": [
    "Build emergency fund: Target ₹300,000 (6 months)",
    "Reduce Entertainment spending by ₹1,500",
    "Monitor Transport costs due to fuel price increase"
  ]
}
```

## Database Schema

### Users (UUID primary key)
- id, email, password_hash, created_at, updated_at

### Expenses (UUID primary key)
- id, user_id, amount, category, date, note, created_at, updated_at
- Indexes: user_id+date, user_id+category

### Budgets (UUID primary key)
- id, user_id, monthly_budget, month, created_at, updated_at
- Unique index: user_id+month

### CPI Data (UUID primary key)
- id, month, value, created_at, updated_at

### Fuel Data (UUID primary key)
- id, date, petrol_price, diesel_price, created_at, updated_at

## Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATA_GOV_API_KEY=your-api-key
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Database Features

- **Connection Pooling**: 5 base + 10 overflow connections
- **SSL Encryption**: Required for Supabase
- **Health Checks**: Pre-ping before connection use
- **Auto Reconnect**: Connection recycling every hour
- **UUID Primary Keys**: Better for distributed systems
- **Composite Indexes**: Optimized for common queries

## Development

### Backend Development
```bash
cd backend
python -m app.main
# Backend runs on http://localhost:8000
# API docs: http://localhost:8000/docs
```

### Frontend Development
```bash
cd frontend
npm run dev
# Frontend runs on http://localhost:3001
```

### Check Health
```bash
curl http://localhost:8000/health/db
```

## Production Deployment

### Backend
1. Set production DATABASE_URL
2. Generate strong SECRET_KEY: `openssl rand -hex 32`
3. Set ACCESS_TOKEN_EXPIRE_MINUTES=60
4. Deploy to Vercel/Railway/Render

### Frontend
1. Update NEXT_PUBLIC_API_URL to production backend
2. Deploy to Vercel

### Database
- Supabase provides automatic backups
- Enable Row Level Security (RLS) for additional security
- Monitor connection pool usage in Supabase Dashboard

## Troubleshooting

### Backend won't start
- Check DATABASE_URL is correct
- Verify Supabase project is active
- Ensure `?sslmode=require` is in connection string

### Frontend can't connect
- Verify backend is running on port 8000
- Check CORS settings in backend/app/main.py
- Clear browser localStorage: `localStorage.clear()`

### Database connection failed
- Check Supabase project status
- Verify database password
- Test connection: `curl http://localhost:8000/health/db`

### Token expired
- Tokens expire after 24 hours
- Clear localStorage and login again
- Check ACCESS_TOKEN_EXPIRE_MINUTES in .env

## Features in Detail

### Dashboard
- Monthly spending overview
- Category breakdown (pie chart)
- Savings rate tracking
- Risk score monitoring
- Inflation impact analysis
- Money leaks detection
- Quick action recommendations

### Insights Page
- Detailed financial analysis
- Personalized deals & offers
- RBI repo rate impact
- Live fuel prices (4 metros)
- Inflation breakdown by category
- Comprehensive recommendations

### Financial Engine
- Rule-based (no ML)
- Real India CPI data
- Dynamic threshold adjustment
- Category sensitivity mapping
- Risk scoring (0-100)
- Specific ₹ recommendations

## Data Sources

- **CPI Data**: data.gov.in API (official government data)
- **Fuel Prices**: goodreturns.in (web scraping)
- **RBI Repo Rate**: rbi.org.in (web scraping)
- **Deals**: Curated based on spending patterns

## Security

- JWT authentication with bcrypt password hashing
- SSL/TLS encryption for database
- Environment variables for secrets
- SQL injection prevention (SQLAlchemy ORM)
- CORS configured for specific origins
- Admin-only access (admin@admin.com)

## Performance

- Connection pooling reduces latency
- Composite indexes speed up queries
- Pre-ping prevents stale connections
- Connection recycling prevents leaks
- Optimized for common query patterns

## License

MIT License

## Support

For issues or questions, check:
- Backend logs: `backend/` directory
- Frontend console: Browser DevTools (F12)
- Database: Supabase Dashboard
- API docs: http://localhost:8000/docs

## Credits

Built with ❤️ for Indian users
