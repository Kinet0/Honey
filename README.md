# Honeypot + Live Attack Dashboard

A professional, production-ready web application that monitors and visualizes real attack activity from a Cowrie SSH/Telnet honeypot.

## Features

### Core Dashboard
- **Live Attack Feed** - Real-time attacks with WebSocket updates
- **Attack Statistics** - Comprehensive metrics and trends
- **Attacker Profiles** - Detailed information about threat actors
- **Session Replay** - Replay captured attacker commands
- **Threat Intelligence** - Command analysis and behavior patterns
- **Attack Analytics** - Geographic distribution and trends

### Technical Stack

**Frontend:**
- Next.js 14+ with TypeScript
- TailwindCSS for styling
- Socket.IO for real-time updates
- React Query for state management
- Recharts for visualizations

**Backend:**
- FastAPI with Python 3.10+
- PostgreSQL for data persistence
- SQLAlchemy ORM
- Socket.IO for WebSockets
- Cowrie honeypot integration

**Infrastructure:**
- Docker & Docker Compose
- Nginx reverse proxy
- PostgreSQL database
- Ubuntu VPS deployment ready

## Quick Start

### Development

```bash
# Clone repository
git clone <repo>
cd Honeypot_LiveAttack

# Start Docker services
docker-compose up -d

# Or run locally:

# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend (in new terminal)
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000` for the dashboard.

### Production Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- VPS setup on Ubuntu 22.04
- PostgreSQL configuration
- Nginx SSL setup
- Systemd services
- Backup strategies

## Documentation

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow
- **[DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md)** - Database design
- **[API_ENDPOINTS.md](docs/API_ENDPOINTS.md)** - REST API reference
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Production deployment guide
- **[SECURITY.md](docs/SECURITY.md)** - Security hardening

## Project Structure

```
Honeypot_LiveAttack/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # API endpoints
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   ├── websocket/         # WebSocket handlers
│   │   ├── parsers/           # Cowrie log parser
│   │   ├── core/              # Configuration & database
│   │   └── main.py            # FastAPI app
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/               # Next.js pages
│   │   ├── components/        # React components
│   │   ├── lib/               # Utilities (API, WebSocket)
│   │   ├── types/             # TypeScript types
│   │   └── globals.css        # Global styles
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── infrastructure/
│   ├── nginx.conf             # Nginx configuration
│   └── ssl/                   # SSL certificates
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATABASE_SCHEMA.md
│   ├── API_ENDPOINTS.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md
└── docker-compose.yml
```

## Key APIs

### Live Attacks
```
GET /api/v1/attacks/feed?limit=50&offset=0
GET /api/v1/attacks/statistics
POST /api/v1/attacks/search
```

### Sessions & Replay
```
GET /api/v1/sessions
GET /api/v1/sessions/{session_id}
GET /api/v1/sessions/{session_id}/replay
```

### Attacker Intelligence
```
GET /api/v1/attackers
GET /api/v1/attackers/{ip}
GET /api/v1/attackers/{ip}/timeline
```

### Analytics
```
GET /api/v1/analytics/trends?period=hourly
GET /api/v1/analytics/map
GET /api/v1/analytics/toplist/{type}
```

### Real-time WebSocket
```
WS /ws
```

## Severity Scoring

- **INFO** - Connection, failed authentication
- **LOW** - Weak credentials, common exploits
- **MEDIUM** - Successful login, reconnaissance
- **HIGH** - Payload download, command execution
- **CRITICAL** - Privilege escalation, persistence

## Security Features

- Environment-based configuration
- Database encryption support
- CORS protection
- Rate limiting
- SQL injection prevention (ORM)
- XSS protection
- Secure WebSocket (WSS) support
- JWT token support (optional)

## Monitoring & Logging

- Structured application logging
- Database query optimization
- WebSocket connection tracking
- Performance metrics
- Error tracking with Sentry (optional)
- Health check endpoints

## Development

### Backend Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
# Install dev dependencies
npm install

# Run type check
npm run type-check

# Build for production
npm run build
npm start
```

## Data Sources

The dashboard uses **real data only** from Cowrie honeypot:
- SSH/Telnet connection logs
- Authentication attempts
- Command execution history
- Payload download tracking
- Session recordings

## Performance Optimization

- Database indexing on common queries
- API response pagination (default 50, max 1000)
- Connection pooling for database
- WebSocket message batching
- Next.js image optimization
- Lazy loading of components

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This is a personal portfolio project demonstrating cybersecurity skills.

## Support

For issues or questions, refer to the documentation or review the code comments.

## Status

- ✅ Database schema
- ✅ Backend API
- ✅ WebSocket real-time updates
- ✅ Frontend dashboard
- ✅ Docker setup
- ✅ Deployment guides
- 🔄 Sample data loading scripts
- 🔄 Advanced analytics dashboards

