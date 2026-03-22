# Deployment Guide

## Backend Deployment (Render/Railway)

### Option 1: Render

1. Create a PostgreSQL database on [Render](https://render.com)
2. Create a new Web Service
3. Connect your GitHub repository
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: Generate a secure random string
   - `ALGORITHM`: HS256
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: 30

### Option 2: Railway

1. Create a new project on [Railway](https://railway.app)
2. Add PostgreSQL database
3. Deploy from GitHub
4. Add the same environment variables as above

### Database Setup (Supabase/Neon)

#### Supabase
1. Create a project on [Supabase](https://supabase.com)
2. Get the connection string from Settings > Database
3. Use it as `DATABASE_URL`

#### Neon
1. Create a project on [Neon](https://neon.tech)
2. Copy the connection string
3. Use it as `DATABASE_URL`

## Frontend Deployment (Vercel)

1. Push your code to GitHub
2. Go to [Vercel](https://vercel.com)
3. Import your repository
4. Configure:
   - Framework Preset: Next.js
   - Root Directory: `frontend`
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL`: Your backend URL (from Render/Railway)
6. Deploy

## Post-Deployment

1. Test authentication by signing up
2. Add sample expenses
3. Set a budget
4. Check insights generation
5. Verify CPI and fuel data is loaded

## Troubleshooting

### Database Connection Issues
- Ensure DATABASE_URL is correctly formatted
- Check if database allows external connections
- Verify SSL mode if required

### CORS Issues
- Update `allow_origins` in `backend/main.py` with your frontend URL
- Redeploy backend

### Frontend API Calls Failing
- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check browser console for errors
- Ensure backend is running and accessible

## Monitoring

- Check backend logs on Render/Railway dashboard
- Monitor database usage on Supabase/Neon
- Use Vercel Analytics for frontend monitoring
