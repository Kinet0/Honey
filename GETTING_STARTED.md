# Getting Started Guide - Honeypot Dashboard

## 📋 Project Overview

You now have a **complete, production-ready Honeypot + Live Attack Dashboard** with:
- Modern Next.js frontend
- FastAPI backend
- PostgreSQL database
- Real-time WebSocket updates
- Comprehensive documentation
- Docker deployment ready

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Docker & Docker Compose
- Git

### Option 1: Docker (Easiest)

```bash
# Clone and navigate
cd Honeypot_LiveAttack

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Start everything
docker-compose -f docker-compose.dev.yml up -d

# Access dashboard
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## 📁 Project Structure

```
Honeypot_LiveAttack/
│
├── backend/                          # FastAPI application
│   ├── app/
│   │   ├── api/routes/              # REST API endpoints
│   │   │   ├── attacks.py           # Attack data endpoints
│   │   │   ├── sessions.py          # Session management
│   │   │   ├── attackers.py         # Attacker profiles
│   │   │   ├── intelligence.py      # Threat intelligence
│   │   │   └── analytics.py         # Analytics endpoints
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   └── attack.py            # Database models
│   │   ├── schemas/                 # Pydantic validation schemas
│   │   ├── websocket/               # Real-time WebSocket
│   │   │   ├── manager.py           # Connection management
│   │   │   └── routes.py            # WebSocket endpoints
│   │   ├── parsers/                 # Cowrie log parser
│   │   ├── services/                # Business logic layer
│   │   ├── core/                    # Configuration, logging, database
│   │   └── main.py                  # FastAPI app factory
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Container image
│   └── .env.example                 # Environment template
│
├── frontend/                        # Next.js dashboard
│   ├── src/
│   │   ├── app/                     # Next.js pages
│   │   │   ├── page.tsx             # Home/dashboard
│   │   │   ├── layout.tsx           # Root layout
│   │   │   ├── attackers/page.tsx   # Attackers list
│   │   │   ├── intelligence/page.tsx # Threat intelligence
│   │   │   └── analytics/page.tsx   # Analytics
│   │   ├── components/
│   │   │   ├── common/              # Reusable components
│   │   │   │   ├── Badge.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── StatCard.tsx
│   │   │   │   └── Loading.tsx
│   │   │   └── dashboard/           # Dashboard-specific
│   │   │       ├── LiveAttackFeed.tsx
│   │   │       └── StatisticsOverview.tsx
│   │   ├── lib/                     # Utilities
│   │   │   ├── api.ts               # API client
│   │   │   ├── websocket.ts         # WebSocket client
│   │   │   └── utils.ts             # Formatting utilities
│   │   ├── types/                   # TypeScript types
│   │   │   └── index.ts             # All API types
│   │   ├── globals.css              # Global styles
│   │   └── services/                # Services
│   ├── package.json                 # Node dependencies
│   ├── tailwind.config.ts           # Tailwind configuration
│   ├── next.config.mjs              # Next.js configuration
│   ├── Dockerfile                   # Container image
│   └── .env.example                 # Environment template
│
├── infrastructure/
│   ├── nginx.conf                   # Reverse proxy configuration
│   └── ssl/                         # SSL certificates directory
│
├── docs/                            # Documentation
│   ├── ARCHITECTURE.md              # System design
│   ├── DATABASE_SCHEMA.md           # Database structure
│   ├── API_ENDPOINTS.md             # API reference
│   ├── DEPLOYMENT.md                # Production deployment
│   └── SECURITY.md                  # Security hardening
│
├── docker-compose.yml               # Production compose
├── docker-compose.dev.yml           # Development compose
├── README.md                        # Project overview
├── PROJECT_STATUS.md                # Completion status
├── ENV_SETUP.md                     # Environment setup
├── GETTING_STARTED.md               # This file
└── .gitignore                       # Git ignore rules
```

## 🔌 API Endpoints

### Attacks
- `GET /api/v1/attacks/feed` - Live attack stream
- `GET /api/v1/attacks/statistics` - Attack stats
- `POST /api/v1/attacks/search` - Search/filter attacks

### Sessions
- `GET /api/v1/sessions` - List sessions
- `GET /api/v1/sessions/{id}` - Session details
- `GET /api/v1/sessions/{id}/replay` - Replay data

### Attackers
- `GET /api/v1/attackers` - List attackers
- `GET /api/v1/attackers/{ip}` - Attacker profile
- `GET /api/v1/attackers/{ip}/timeline` - Attack timeline

### Intelligence
- `GET /api/v1/intelligence/commands` - Command frequency
- `GET /api/v1/intelligence/credentials` - Top credentials
- `GET /api/v1/intelligence/payloads` - Payload analysis

### Analytics
- `GET /api/v1/analytics/trends` - Activity trends
- `GET /api/v1/analytics/map` - Geographic data
- `GET /api/v1/analytics/toplist/{type}` - Top lists

### WebSocket
- `WS /ws` - Real-time event stream

## 🎨 UI Design

**Color Scheme:**
- Background: `#0B1220` (dark blue-black)
- Panels: `#111827` (dark gray)
- Borders: `#1F2937` (medium gray)
- Primary: `#22C55E` (bright green)
- Warning: `#F59E0B` (amber)
- Critical: `#EF4444` (red)

**Severity Badges:**
- INFO: Blue
- LOW: Yellow
- MEDIUM: Orange
- HIGH: Red
- CRITICAL: Dark Red

**Status Indicators:**
- Active: Green (pulsing)
- Complete: Gray
- Failed: Red

## 🛠 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
SECRET_KEY=your-secret-key
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

## 📊 Features Implementation Guide

### Adding a New Feature

1. **Backend:**
   - Add model in `backend/app/models/attack.py`
   - Create schema in `backend/app/schemas/attack.py`
   - Add endpoint in `backend/app/api/routes/`
   - Add service logic in `backend/app/services/`

2. **Frontend:**
   - Create component in `src/components/`
   - Create page in `src/app/`
   - Add API call in `src/lib/api.ts`
   - Add types in `src/types/index.ts`

3. **Database:**
   - Update model relationships
   - Add indexes for performance
   - Run migrations

## 🔐 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for production domain
- [ ] Enable firewall rules
- [ ] Set strong database passwords
- [ ] Configure SSH key-based authentication
- [ ] Enable security headers in Nginx
- [ ] Set up automated backups
- [ ] Configure rate limiting
- [ ] Enable audit logging

## 📈 Performance Optimization

- Database indexes on frequently queried columns
- Connection pooling (20 connections)
- WebSocket message batching
- Next.js image optimization
- Gzip compression in Nginx
- Redis caching (optional)
- API response pagination

## 🚢 Production Deployment

See `docs/DEPLOYMENT.md` for complete guide:

1. **VPS Setup**
   ```bash
   # Ubuntu 22.04 LTS
   sudo apt update && upgrade
   sudo apt install docker.io docker-compose postgresql nginx
   ```

2. **Application Setup**
   ```bash
   git clone <repo> /opt/honeypot-dashboard
   cd /opt/honeypot-dashboard
   docker-compose up -d
   ```

3. **SSL/TLS**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

4. **Cowrie Integration**
   - Install Cowrie on same/different VPS
   - Configure log output to JSON
   - Set up log watcher to ingest data

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/

# Type checking
mypy app/

# Code formatting
black app/

# Frontend tests
cd frontend
npm run type-check
npm test
```

## 📚 Learning Resources

- **FastAPI:** https://fastapi.tiangolo.com
- **Next.js:** https://nextjs.org/docs
- **SQLAlchemy:** https://docs.sqlalchemy.org
- **Cowrie:** https://cowrie.readthedocs.io
- **Socket.IO:** https://socket.io/docs
- **TailwindCSS:** https://tailwindcss.com/docs

## 🐛 Troubleshooting

### Database connection error
```bash
# Check PostgreSQL is running
docker-compose ps

# Check connection string in .env
# Format: postgresql+asyncpg://user:password@host:5432/database
```

### WebSocket connection failed
```bash
# Ensure backend is running
curl http://localhost:8000/api/v1/health

# Check WebSocket is accessible
# Frontend should connect to: ws://localhost:8000/ws
```

### Missing module error
```bash
# Backend
pip install -r requirements.txt

# Frontend
npm install
```

## 📞 Support

- Check documentation in `/docs`
- Review code comments in source files
- Check GitHub issues for similar problems
- Review Docker logs: `docker-compose logs -f backend`

## 🎓 What This Project Demonstrates

✅ **Cybersecurity Knowledge**
- Attack pattern analysis
- Honeypot implementation
- Threat assessment
- Command classification

✅ **Full-Stack Development**
- Modern frontend (Next.js, React, TypeScript)
- Professional backend (FastAPI, Python)
- Real-time communication (WebSocket)
- Database design (PostgreSQL)

✅ **DevOps & Infrastructure**
- Docker containerization
- Nginx reverse proxy
- SSL/TLS setup
- Ubuntu server management
- Deployment automation

✅ **Code Quality**
- Type-safe code (TypeScript + Python)
- API documentation
- Comprehensive error handling
- Security best practices
- Database optimization

## 🎉 You're Ready!

1. Start the dashboard: `docker-compose up -d`
2. Open browser: `http://localhost:3000`
3. Explore the API: `http://localhost:8000/docs`
4. Read the documentation in `/docs`
5. Customize for your needs
6. Deploy to production

Happy monitoring! 🔍

