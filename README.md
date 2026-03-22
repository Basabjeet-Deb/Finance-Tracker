# 🇮🇳 Finance Tracker India

An AI-powered personal finance tracker specifically designed for Indian users, featuring real-time inflation data, RBI rate tracking, and personalized financial insights.

## ✨ Features

### Core Features
- 🔐 **Secure Authentication** - JWT-based admin authentication
- 💰 **Expense Tracking** - Track and categorize expenses
- 📊 **Interactive Dashboard** - Beautiful visualizations with charts
- 🎯 **Budget Management** - Set and monitor monthly budgets
- 📈 **Financial Analysis** - AI-powered spending insights

### Advanced Features
- 📉 **Real-time CPI Data** - Live inflation data from data.gov.in API
- 🏦 **RBI Repo Rate Tracking** - Monitor RBI rates and EMI impact
- ⛽ **Fuel Price Tracker** - Real-time petrol prices across 4 metros
- 🎁 **Personalized Deals** - Contextual offers based on spending patterns
- 🤖 **AI Recommendations** - Inflation-adjusted financial advice
- 🎨 **Beautiful UI** - Modern, responsive design with animations

## 🏗️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database
- **JWT** - Secure authentication
- **BeautifulSoup** - Web scraping for live data
- **APScheduler** - Background task scheduling

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Animation library
- **Recharts** - Chart library
- **Axios** - HTTP client

## 📁 Project Structure

```
finance-tracker-india/
├── backend/
│   ├── app/
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   ├── models/          # Database models
│   │   ├── schemas/         # Pydantic schemas
│   │   └── db/              # Database config
│   ├── finance_tracker.db   # SQLite database
│   └── requirements.txt     # Python dependencies
│
└── frontend/
    ├── src/
    │   ├── app/             # Next.js pages
    │   ├── components/      # React components
    │   └── lib/             # Utilities
    └── package.json         # Node dependencies
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. Navigate to backend directory:
```bash
cd finance-tracker-india/backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
DATA_GOV_IN_API_KEY=579b464db66ec23bdd0000019068c43cf6e74bca518f2010329bad4d
```

5. Start the server:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd finance-tracker-india/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🔑 Default Credentials

- **Email**: admin@admin.com
- **Password**: admin123

## 📊 Data Sources

### Real-Time Data Integration
1. **CPI Data** - Government of India (data.gov.in)
   - Monthly inflation metrics
   - Historical data from 2013-2024
   - Automatic updates

2. **RBI Repo Rate** - Reserve Bank of India (rbi.org.in)
   - Current policy rates
   - EMI impact calculations

3. **Fuel Prices** - GoodReturns.in
   - Live petrol prices
   - Coverage: Delhi, Mumbai, Bangalore, Chennai

4. **Contextual Deals**
   - Swiggy, Zomato (Food)
   - Uber, Ola (Transport)
   - Myntra, BookMyShow (Lifestyle)
   - Amazon, Flipkart (Shopping)

## 🎯 Key Features Explained

### Inflation-Adjusted Analysis
- Tracks real CPI data from Government of India
- Adjusts budget recommendations based on inflation
- Identifies categories most affected by price increases
- Provides specific ₹ amounts, not generic advice

### Rule-Based Financial Engine
- Categorizes spending into: Fixed, Essential, Lifestyle, Savings
- Dynamic constraint adjustments based on:
  - EMI burden
  - Medical risk
  - Family dependency
  - Income level
- Generates actionable recommendations

### Risk Assessment
- Calculates financial risk score (0-100)
- Considers multiple factors:
  - Savings rate
  - Fixed obligations
  - Emergency fund status
  - Inflation pressure
- Provides risk level: Low, Medium, High

## 🛠️ API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login and get JWT token

### Expenses
- `GET /expenses` - List all expenses
- `POST /expenses` - Create new expense
- `PUT /expenses/{id}` - Update expense
- `DELETE /expenses/{id}` - Delete expense

### Analysis
- `GET /dashboard` - Dashboard overview
- `GET /financial-analysis` - Comprehensive analysis
- `GET /financial-health` - Quick health summary

### External Data
- `GET /cpi` - CPI data with inflation metrics
- `POST /cpi/refresh` - Refresh CPI data
- `GET /inflation/pressure` - Current inflation pressure
- `GET /inflation/thresholds` - Adjusted thresholds

## 🎨 Screenshots

### Dashboard
- Monthly spending overview
- Savings rate visualization
- Risk score indicator
- Inflation impact metrics
- Spending distribution chart
- Money leaks identification

### Insights Page
- Detailed AI recommendations
- Personalized deals & offers
- RBI rate impact analysis
- Live fuel price tracker
- Inflation insights

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- Admin-only access control
- CORS protection
- Environment variable configuration

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🙏 Acknowledgments

- Data.gov.in for CPI data
- Reserve Bank of India for policy rates
- GoodReturns.in for fuel prices
- All open-source libraries used in this project

---

Made with ❤️ for Indian users
