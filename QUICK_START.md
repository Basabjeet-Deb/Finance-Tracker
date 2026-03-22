# Quick Start Guide

## Current Status
✅ Backend: Running on http://localhost:8000
✅ Frontend: Running on http://localhost:3001
✅ CORS: Configured for port 3001

## Access the Application

1. **Open Browser**: http://localhost:3001

2. **Login**:
   - Email: `admin@admin.com`
   - Password: `admin123`

3. **If "SYNCING ENGINE..." doesn't disappear**:
   - Open browser DevTools (F12)
   - Go to Console tab
   - Look for error messages
   - Check Network tab for failed requests

## Common Issues

### Issue: Infinite Loading (SYNCING ENGINE...)

**Solution 1: Check Browser Console**
- Press F12 to open DevTools
- Look for CORS errors or network errors
- If you see "CORS policy" errors, the backend needs restart

**Solution 2: Clear Browser Data**
- Clear localStorage: In Console, type `localStorage.clear()` and press Enter
- Hard refresh: Ctrl + Shift + R (Windows) or Cmd + Shift + R (Mac)
- Try logging in again

**Solution 3: Verify Backend is Running**
```bash
# Test backend health
curl http://localhost:8000/health
```

**Solution 4: Check Token**
- In browser Console, type: `localStorage.getItem('token')`
- If null, you need to login again
- If present, try: `localStorage.getItem('user')`

### Issue: CORS Errors

**Solution**: Restart backend
```bash
# Stop backend (Ctrl+C in backend terminal)
# Start again:
cd finance-tracker-india/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Issue: 401 Unauthorized

**Solution**: Token expired or invalid
1. Clear localStorage: `localStorage.clear()`
2. Refresh page
3. Login again

### Issue: Frontend on wrong port

**Solution**: Update API URL
1. Check which port frontend is on (shown in terminal)
2. If not 3001, backend CORS needs that port added
3. Edit `backend/app/main.py` and add your port to `allow_origins`

## Debugging Steps

### 1. Test Backend Directly
```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@admin.com","password":"admin123"}'

# Copy the access_token from response

# Test dashboard (replace YOUR_TOKEN)
curl http://localhost:8000/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Check Frontend API Calls
Open browser DevTools (F12) → Network tab:
- Look for requests to localhost:8000
- Check if they're returning 200 OK or errors
- Click on failed requests to see details

### 3. Check Console Logs
The dashboard now has detailed logging:
- "Fetching dashboard data..." - API call started
- "Dashboard data received:" - Dashboard API succeeded
- "Analysis data received:" - Analysis API succeeded  
- "Setting loading to false" - Loading should stop
- Any errors will show with details

## Manual Testing

### Test Login
1. Go to http://localhost:3001/login
2. Enter credentials
3. Check Console for any errors
4. Should redirect to /dashboard

### Test Dashboard API
1. Login first
2. Open Console (F12)
3. Type:
```javascript
fetch('http://localhost:8000/dashboard', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(d => console.log(d))
```
4. Should see dashboard data in console

### Test Financial Analysis API
```javascript
fetch('http://localhost:8000/financial-analysis?monthly_income=50000', {
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
})
.then(r => r.json())
.then(d => console.log(d))
```

## Success Indicators

When everything is working:
1. Login redirects to dashboard immediately
2. "SYNCING ENGINE..." appears briefly (1-2 seconds)
3. Dashboard loads with:
   - Monthly spend amount
   - Savings rate percentage
   - Risk score
   - Inflation percentage
   - Pie chart with spending categories
   - Money leaks section
   - AI recommendations

## Still Not Working?

### Check Backend Logs
Look at the terminal where backend is running:
- Should see incoming requests
- Look for any ERROR messages
- Check for 500 Internal Server Error

### Check Frontend Logs
Look at the terminal where frontend is running:
- Should see page compilations
- Look for any errors

### Nuclear Option: Full Restart
```bash
# Stop both services (Ctrl+C in both terminals)

# Backend
cd finance-tracker-india/backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd finance-tracker-india/frontend
npm run dev

# Clear browser data
# In browser Console: localStorage.clear()
# Hard refresh: Ctrl+Shift+R
# Login again
```

## Contact Info

If issues persist, check:
1. Backend terminal for errors
2. Frontend terminal for errors  
3. Browser Console (F12) for errors
4. Browser Network tab (F12) for failed requests

All four sources will give clues about what's failing.
