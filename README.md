# Finance Tracker India 🇮🇳

AI-powered Personal Finance Tracker with rule-based optimization for Indian users. Built with FastAPI, Next.js, and Supabase PostgreSQL.

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
