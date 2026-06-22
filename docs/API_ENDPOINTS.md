# API Endpoints Documentation

## Base URL
- Development: `http://localhost:8000`
- Production: `https://api.yourdomain.com`

## Authentication
Currently, the API is public for a portfolio project. Optional JWT authentication can be implemented for sensitive endpoints.

---

## Attack Endpoints

### Get Recent Attacks
```
GET /api/v1/attacks/feed
```
**Query Parameters:**
- `limit` (int, default=50): Number of attacks to return
- `offset` (int, default=0): Pagination offset
- `severity` (enum): Filter by INFO, LOW, MEDIUM, HIGH, CRITICAL

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "timestamp": "2024-06-23T15:30:45Z",
      "session_id": "session_id",
      "attacker_ip": "192.168.1.100",
      "country_code": "CN",
      "event_type": "command",
      "severity": "HIGH",
      "asn": 4134,
      "metadata": {}
    }
  ],
  "total": 1500,
  "limit": 50,
  "offset": 0
}
```

### Get Attack Statistics
```
GET /api/v1/attacks/statistics
```

**Response:**
```json
{
  "attacks_today": 234,
  "attacks_this_week": 1842,
  "attacks_this_month": 7234,
  "unique_attackers": 412,
  "unique_countries": 48,
  "total_commands": 3421,
  "total_downloads": 89,
  "avg_session_duration": 145
}
```

### Search/Filter Attacks
```
GET /api/v1/attacks/search
```

**Query Parameters:**
- `country` (string): Country code filter
- `asn` (integer): ASN filter
- `username` (string): Username filter
- `command` (string): Command text search
- `severity` (enum): Severity filter
- `start_date` (datetime): Start date filter
- `end_date` (datetime): End date filter
- `limit` (int): Results per page
- `offset` (int): Pagination offset

**Response:**
```json
{
  "data": [...],
  "total": 234,
  "filters_applied": {
    "country": "CN",
    "severity": "CRITICAL"
  }
}
```

### Get Attack Details
```
GET /api/v1/attacks/{attack_id}
```

**Response:**
```json
{
  "id": "uuid",
  "timestamp": "2024-06-23T15:30:45Z",
  "session_id": "session_id",
  "attacker_ip": "192.168.1.100",
  "attacker": {
    "country": "China",
    "country_code": "CN",
    "asn": 4134,
    "isp": "China Telecom",
    "threat_level": "CRITICAL"
  },
  "event_type": "command",
  "severity": "HIGH",
  "metadata": {}
}
```

---

## Session Endpoints

### List Sessions
```
GET /api/v1/sessions
```

**Query Parameters:**
- `status` (enum): active, complete, failed
- `limit` (int): Results per page
- `offset` (int): Pagination offset

**Response:**
```json
{
  "data": [
    {
      "id": "session_id",
      "attacker_ip": "192.168.1.100",
      "country": "China",
      "start_time": "2024-06-23T15:30:45Z",
      "end_time": "2024-06-23T15:45:30Z",
      "duration_seconds": 900,
      "status": "complete",
      "total_commands": 23,
      "protocol": "ssh"
    }
  ],
  "total": 1200
}
```

### Get Session Details
```
GET /api/v1/sessions/{session_id}
```

**Response:**
```json
{
  "id": "session_id",
  "attacker_ip": "192.168.1.100",
  "attacker": {
    "country": "China",
    "asn": 4134,
    "isp": "China Telecom",
    "first_seen": "2024-01-15T10:00:00Z",
    "last_seen": "2024-06-23T15:45:30Z",
    "session_count": 15,
    "command_count": 342
  },
  "start_time": "2024-06-23T15:30:45Z",
  "end_time": "2024-06-23T15:45:30Z",
  "duration_seconds": 900,
  "status": "complete",
  "protocol": "ssh",
  "commands": [
    {
      "timestamp": "2024-06-23T15:31:00Z",
      "command": "whoami",
      "classification": "reconnaissance",
      "success": true,
      "output": "root"
    }
  ],
  "downloads": [
    {
      "timestamp": "2024-06-23T15:42:00Z",
      "filename": "malware.bin",
      "file_hash": "sha256hash",
      "file_size": 4096
    }
  ],
  "credentials_attempted": [
    {
      "username": "root",
      "password": "password123",
      "success": true
    }
  ]
}
```

### Get Session Replay Data
```
GET /api/v1/sessions/{session_id}/replay
```

**Response:**
```json
{
  "session_id": "session_id",
  "duration_seconds": 900,
  "events": [
    {
      "timestamp": "2024-06-23T15:30:45Z",
      "type": "connection",
      "data": {}
    },
    {
      "timestamp": "2024-06-23T15:31:00Z",
      "type": "command",
      "data": {
        "command": "whoami",
        "output": "root"
      }
    }
  ]
}
```

---

## Attacker Endpoints

### List Attackers
```
GET /api/v1/attackers
```

**Query Parameters:**
- `threat_level` (enum): low, medium, high, critical
- `country` (string): Country code
- `limit` (int): Results per page
- `offset` (int): Pagination offset

**Response:**
```json
{
  "data": [
    {
      "ip_address": "192.168.1.100",
      "country": "China",
      "country_code": "CN",
      "asn": 4134,
      "isp": "China Telecom",
      "first_seen": "2024-01-15T10:00:00Z",
      "last_seen": "2024-06-23T15:45:30Z",
      "session_count": 15,
      "command_count": 342,
      "download_count": 7,
      "max_severity": "CRITICAL",
      "threat_level": "CRITICAL"
    }
  ],
  "total": 412
}
```

### Get Attacker Profile
```
GET /api/v1/attackers/{ip}
```

**Response:**
```json
{
  "ip_address": "192.168.1.100",
  "country": "China",
  "country_code": "CN",
  "asn": 4134,
  "isp": "China Telecom",
  "first_seen": "2024-01-15T10:00:00Z",
  "last_seen": "2024-06-23T15:45:30Z",
  "session_count": 15,
  "command_count": 342,
  "download_count": 7,
  "max_severity": "CRITICAL",
  "threat_level": "CRITICAL",
  "recent_sessions": [...],
  "top_commands": [...],
  "downloads": [...]
}
```

### Get Attacker Timeline (Attack Story)
```
GET /api/v1/attackers/{ip}/timeline
```

**Response:**
```json
{
  "ip_address": "192.168.1.100",
  "timeline": [
    {
      "stage": "connection",
      "timestamp": "2024-06-23T15:30:45Z",
      "details": "SSH connection established"
    },
    {
      "stage": "authentication",
      "timestamp": "2024-06-23T15:31:00Z",
      "details": "Failed authentication attempt (root:password123)"
    },
    {
      "stage": "login",
      "timestamp": "2024-06-23T15:31:15Z",
      "details": "Successful login as root"
    },
    {
      "stage": "reconnaissance",
      "timestamp": "2024-06-23T15:31:30Z",
      "details": "Executed: whoami, uname -a, id"
    },
    {
      "stage": "download",
      "timestamp": "2024-06-23T15:42:00Z",
      "details": "Downloaded malware.bin (4096 bytes)"
    },
    {
      "stage": "execution",
      "timestamp": "2024-06-23T15:42:30Z",
      "details": "Executed downloaded payload"
    }
  ]
}
```

---

## Intelligence Endpoints

### Get Command Frequency
```
GET /api/v1/intelligence/commands
```

**Query Parameters:**
- `limit` (int, default=20): Number of top commands
- `classification` (enum): Filter by classification

**Response:**
```json
{
  "data": [
    {
      "command": "whoami",
      "count": 342,
      "classification": "reconnaissance",
      "success_rate": 0.98
    }
  ]
}
```

### Get Credentials Analysis
```
GET /api/v1/intelligence/credentials
```

**Query Parameters:**
- `type` (enum): usernames, passwords
- `limit` (int, default=20): Number of top items

**Response:**
```json
{
  "top_usernames": [
    {
      "username": "root",
      "count": 234,
      "success_count": 45,
      "success_rate": 0.19
    }
  ],
  "top_passwords": [
    {
      "password": "password123",
      "count": 123,
      "success_count": 12,
      "success_rate": 0.10
    }
  ]
}
```

### Get Payload Analysis
```
GET /api/v1/intelligence/payloads
```

**Response:**
```json
{
  "total_downloads": 89,
  "unique_payloads": 23,
  "payloads": [
    {
      "filename": "malware.bin",
      "count": 12,
      "file_hash": "sha256hash",
      "file_size": 4096,
      "file_type": "executable"
    }
  ]
}
```

---

## Analytics Endpoints

### Get Activity Trends
```
GET /api/v1/analytics/trends
```

**Query Parameters:**
- `period` (enum): hourly, daily, weekly (default=hourly)
- `days` (int, default=7): Number of days to return

**Response:**
```json
{
  "period": "hourly",
  "data": [
    {
      "timestamp": "2024-06-23T15:00:00Z",
      "attacks": 45,
      "unique_attackers": 23,
      "unique_countries": 8
    }
  ]
}
```

### Get World Map Data
```
GET /api/v1/analytics/map
```

**Response:**
```json
{
  "data": [
    {
      "country_code": "CN",
      "country_name": "China",
      "latitude": 35.8617,
      "longitude": 104.1954,
      "attack_count": 234,
      "unique_attackers": 89,
      "intensity": 0.85
    }
  ]
}
```

### Get Top Lists
```
GET /api/v1/analytics/toplist/{type}
```

**Types:**
- `countries`
- `asns`
- `usernames`
- `commands`
- `payloads`

**Response:**
```json
{
  "type": "countries",
  "data": [
    {
      "rank": 1,
      "name": "China",
      "code": "CN",
      "value": 1234,
      "percentage": 0.34
    }
  ]
}
```

---

## Real-Time WebSocket Events

### Connection
```
WS ws://localhost:8000/ws
```

### Events from Server

**New Attack Event**
```json
{
  "type": "attack:new",
  "data": {
    "id": "uuid",
    "timestamp": "2024-06-23T15:30:45Z",
    "attacker_ip": "192.168.1.100",
    "severity": "HIGH",
    "event_type": "command",
    "country_code": "CN"
  }
}
```

**Session Update**
```json
{
  "type": "session:update",
  "data": {
    "session_id": "session_id",
    "status": "complete",
    "command_count": 25
  }
}
```

**Statistics Update**
```json
{
  "type": "stats:update",
  "data": {
    "attacks_today": 234,
    "unique_attackers": 89,
    "unique_countries": 15
  }
}
```

### Commands from Client

**Subscribe to Attacks**
```json
{
  "type": "subscribe:attacks",
  "filters": {
    "severity": ["HIGH", "CRITICAL"],
    "countries": ["CN", "RU"]
  }
}
```

**Unsubscribe**
```json
{
  "type": "unsubscribe:attacks"
}
```

