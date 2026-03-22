# ✅ Admin User Created

## Login Credentials

**Email:** `admin@admin.com`  
**Password:** `admin123`

## Usage

### For Frontend Login Page

Use these credentials in your login form:

```javascript
{
  "email": "admin@admin.com",
  "password": "admin123"
}
```

### API Endpoint

```
POST http://localhost:8000/auth/login
Content-Type: application/json

{
  "email": "admin@admin.com",
  "password": "admin123"
}
```

### Response

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Testing

✅ Admin user created in database  
✅ Login tested and working  
✅ JWT token generated successfully

## Using the Token

Include the token in subsequent requests:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Creating Additional Users

Run the script again to create more users:

```bash
cd backend
python create_admin.py
```

Or use the signup endpoint:

```
POST /auth/signup
{
  "email": "user@example.com",
  "password": "password123"
}
```

## Database Location

User data stored in: `backend/finance_tracker.db`

---

**Status:** Ready for frontend integration ✅
