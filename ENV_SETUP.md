# Honeypot Dashboard - Environment Configuration

## Backend Setup

```bash
# .env file for backend
DATABASE_URL=postgresql+asyncpg://honeypot_user:password@localhost/honeypot_dashboard
SECRET_KEY=your-super-secret-key
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

## Frontend Setup

```bash
# .env.local file for frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws
```

## Docker Environment

```bash
# .env file for docker-compose
DB_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Production Deployment

See DEPLOYMENT.md for complete production setup instructions.
