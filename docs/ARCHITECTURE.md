# Honeypot Live Attack Dashboard - System Architecture

## Overview

A full-stack cybersecurity monitoring application that processes real-time attack data from a Cowrie SSH/Telnet honeypot and presents it in a professional, interactive dashboard.

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
│                    (Next.js + TypeScript)                            │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Modern Dark-Mode Security Dashboard                 │   │
│  │  • Live Attack Feed    • Session Replay                     │   │
│  │  • Attacker Profiles   • Attack Timeline                    │   │
│  │  • Command Intelligence • World Attack Map                  │   │
│  │  • Statistics & Trends  • Search & Filters                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↕ (WebSocket)                           │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                               │
│                    (FastAPI + Python)                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              WebSocket Server + REST API                     │   │
│  │  • Real-time Event Broadcasting                            │   │
│  │  • Aggregation & Analysis Services                         │   │
│  │  • Severity Scoring Engine                                 │   │
│  │  • GeoIP & ASN Lookup Services                            │   │
│  │  • Session Replay Engine                                   │   │
│  │  • Search & Filter Engine                                  │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↕                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                       │
│                    (PostgreSQL)                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         Normalized Schema for Attack Data                  │   │
│  │  • Events      • Sessions    • Commands    • Downloads     │   │
│  │  • Attackers   • Passwords   • Payloads    • ASN Lookups   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↕                                       │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                      DATA SOURCE LAYER                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │     Cowrie Honeypot (Running on VPS)                       │   │
│  │  • SSH/Telnet Listener                                     │   │
│  │  • JSON Log Output                                         │   │
│  │  • Session Recordings                                      │   │
│  │  • Command History                                         │   │
│  │  • Download Events                                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↑                                       │
│                  (Log Parser / File Watcher)                         │
└─────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS + Custom CSS
- **UI Components**: shadcn/ui
- **Charting**: Recharts
- **State Management**: React Query (TanStack Query)
- **Real-time**: Socket.IO Client
- **Maps**: Leaflet (optional, for world map)

### Backend
- **Framework**: FastAPI (Python 3.10+)
- **Language**: Python
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **Real-time**: Socket.IO (python-socketio)
- **Validation**: Pydantic V2
- **Task Queue**: Celery (optional, for async jobs)

### Infrastructure
- **Honeypot**: Cowrie SSH/Telnet
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Database**: PostgreSQL
- **VPS**: Ubuntu 22.04 LTS

## Key Features

### 1. Live Attack Feed
- Real-time attack event streaming via WebSocket
- Displays: timestamp, source IP, country, username, password, event type, severity
- Auto-refresh with newest events at top

### 2. Active Sessions
- Live session tracking
- Status: Active, Complete, Failed
- Duration and command count
- Click to view detailed session data

### 3. Session Replay
- Play recorded attacker commands
- Speed controls (0.5x - 2x)
- Pause/resume functionality
- Exact command rendering

### 4. Attacker Profile
- Country, ASN, ISP information
- First/Last seen timestamps
- Session count
- Command execution history
- Downloaded payloads
- Behavior timeline

### 5. Attack Story View
- Visual timeline: Connection → Auth → Login → Recon → Download → Execution
- Command context at each stage
- Attack progression analysis

### 6. Command Intelligence
- Auto-classification:
  - Reconnaissance
  - File Download
  - Execution
  - Persistence
  - Networking
  - Privilege Escalation
- Command frequency analysis
- Payload tracking

### 7. Attack Statistics
- Attacks today/week/month
- Unique attackers/countries
- Total commands executed
- Total payloads downloaded

### 8. World Attack Map
- Geographic attack origin visualization
- Color intensity = attack frequency
- Hover for country details

### 9. Top Lists
- Top usernames
- Top passwords
- Top countries
- Top commands
- Top ASNs

### 10. Attack Trends
- Hourly activity chart
- Daily activity chart
- Weekly activity chart
- Trend analysis

### 11. Severity Scoring
- **INFO**: Reconnaissance, failed auth
- **LOW**: Weak credentials, common exploits
- **MEDIUM**: Successful login, command execution
- **HIGH**: Payload download, persistence attempts
- **CRITICAL**: Privilege escalation, system compromise

### 12. Search & Filters
- Filter by country, ASN, username, command
- Date range selection
- Full-text search
- Saved filter presets

## Database Schema

### Core Tables

1. **attacks** - Individual attack events
2. **sessions** - Attack sessions (may contain multiple events)
3. **commands** - Commands executed during sessions
4. **downloads** - Payload downloads
5. **attackers** - Attacker profiles/IPs
6. **credentials** - Captured credentials
7. **asn_lookups** - ASN/ISP lookup cache
8. **activity_stats** - Pre-calculated statistics

## API Endpoints

### Attack Data
- `GET /api/attacks/feed` - Recent attacks
- `GET /api/attacks/statistics` - Attack stats
- `GET /api/attacks/search` - Search/filter attacks
- `GET /api/attacks/{attack_id}` - Attack details

### Sessions
- `GET /api/sessions` - List sessions
- `GET /api/sessions/{session_id}` - Session details
- `GET /api/sessions/{session_id}/replay` - Session data for replay

### Attackers
- `GET /api/attackers` - List attackers
- `GET /api/attackers/{ip}` - Attacker profile
- `GET /api/attackers/{ip}/timeline` - Attack story timeline

### Intelligence
- `GET /api/intelligence/commands` - Command frequency
- `GET /api/intelligence/credentials` - Top credentials
- `GET /api/intelligence/payloads` - Payload analysis

### Analytics
- `GET /api/analytics/trends` - Activity trends
- `GET /api/analytics/map` - Geographic data
- `GET /api/analytics/toplist/{type}` - Top lists

### Real-time
- `WebSocket /ws` - Live event stream

## WebSocket Events

### Server → Client
- `attack:new` - New attack event
- `session:update` - Session status change
- `stats:update` - Statistics update
- `connection:established` - WS connection confirmed

### Client → Server
- `subscribe:attacks` - Request attack events
- `subscribe:stats` - Request stat updates
- `filter:set` - Apply filters

## Data Flow

```
Cowrie Honeypot
    ↓ (JSON Logs)
Log Parser/Watcher
    ↓
PostgreSQL Database
    ↓
FastAPI Backend
    ├→ REST API Endpoints
    └→ WebSocket Server
    ↓
Next.js Frontend
    ├→ Dashboard Components
    ├→ Real-time Updates
    └→ User Interactions
```

## Deployment Architecture

```
Internet
    ↓
Nginx (Port 80/443)
    ├→ Static Assets
    └→ Reverse Proxy
    ↓
Next.js (Port 3000)
    └→ Frontend App
    
PostgreSQL (Port 5432)
    └→ Data Persistence
    
FastAPI (Port 8000)
    ├→ REST API
    └→ WebSocket Server

Cowrie Honeypot (Port 22/23)
    └→ Attack Capture
```

## Security Considerations

1. **Authentication**: Optional JWT for admin features
2. **CORS**: Restrict to trusted origins
3. **Rate Limiting**: API endpoint protection
4. **HTTPS/WSS**: Encrypted connections
5. **Database**: Strong passwords, backups
6. **Log Sanitization**: No sensitive data exposure
7. **Input Validation**: Pydantic validation on all inputs

## Performance Optimization

1. **Database Indexing**: Optimized for common queries
2. **Caching**: Redis for frequently accessed data
3. **Pagination**: Efficient data loading
4. **WebSocket Batching**: Group updates for efficiency
5. **Component Code Splitting**: Lazy loading in frontend
6. **Image Optimization**: Next.js image optimization
7. **Database Connection Pooling**: Efficient DB usage

## Monitoring & Logging

1. **Application Logs**: Structured logging with timestamps
2. **Performance Metrics**: Response times, queue depth
3. **Error Tracking**: Comprehensive error handling
4. **Uptime Monitoring**: Health check endpoints
5. **Database Monitoring**: Query performance analysis

