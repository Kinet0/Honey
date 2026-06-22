# Database Schema

## PostgreSQL Schema Design

### Tables Overview

```
attacks (Main event table)
├── id (UUID, PK)
├── timestamp (DateTime)
├── session_id (FK → sessions)
├── attacker_ip (VARCHAR, FK → attackers)
├── event_type (ENUM: connection, auth_attempt, login, command, download)
├── severity (ENUM: INFO, LOW, MEDIUM, HIGH, CRITICAL)
├── country_code (VARCHAR)
├── asn (INTEGER)
└── metadata (JSONB)

sessions (Attack session records)
├── id (VARCHAR, PK)
├── attacker_ip (FK → attackers)
├── start_time (DateTime)
├── end_time (DateTime, nullable)
├── duration_seconds (INTEGER)
├── status (ENUM: active, complete, failed)
├── total_commands (INTEGER)
├── protocol (ENUM: ssh, telnet)
└── honeypot_version (VARCHAR)

commands (Executed commands)
├── id (UUID, PK)
├── session_id (FK → sessions)
├── timestamp (DateTime)
├── command (TEXT)
├── classification (ENUM: recon, download, execution, persistence, networking, privesc)
├── success (BOOLEAN)
└── output (TEXT, nullable)

downloads (Payload downloads)
├── id (UUID, PK)
├── session_id (FK → sessions)
├── timestamp (DateTime)
├── filename (VARCHAR)
├── file_path (VARCHAR)
├── file_hash (VARCHAR, SHA256)
├── file_size (INTEGER)
├── url (VARCHAR, nullable)
└── file_type (VARCHAR)

attackers (Attacker profiles)
├── ip_address (VARCHAR, PK)
├── country_code (VARCHAR)
├── asn (INTEGER)
├── isp (VARCHAR)
├── first_seen (DateTime)
├── last_seen (DateTime)
├── total_sessions (INTEGER)
├── total_commands (INTEGER)
├── total_downloads (INTEGER)
├── max_severity (ENUM)
└── threat_level (ENUM: low, medium, high, critical)

credentials (Captured usernames & passwords)
├── id (UUID, PK)
├── session_id (FK → sessions)
├── timestamp (DateTime)
├── username (VARCHAR)
├── password (VARCHAR)
├── success (BOOLEAN)
├── attempt_count (INTEGER)
└── last_used (DateTime)

asn_lookups (Cached ASN/ISP data)
├── asn (INTEGER, PK)
├── isp (VARCHAR)
├── country_code (VARCHAR)
├── last_updated (DateTime)
└── lookup_count (INTEGER)

activity_stats (Pre-calculated statistics)
├── id (UUID, PK)
├── date (DATE)
├── hour (INTEGER, 0-23)
├── attack_count (INTEGER)
├── unique_attackers (INTEGER)
├── unique_countries (INTEGER)
├── total_commands (INTEGER)
├── total_downloads (INTEGER)
└── timestamp (DateTime)
```

## Table Definitions (SQL)

```sql
-- Enums
CREATE TYPE event_type_enum AS ENUM (
    'connection',
    'auth_attempt',
    'login',
    'command',
    'download'
);

CREATE TYPE severity_enum AS ENUM (
    'INFO',
    'LOW',
    'MEDIUM',
    'HIGH',
    'CRITICAL'
);

CREATE TYPE session_status_enum AS ENUM (
    'active',
    'complete',
    'failed'
);

CREATE TYPE command_classification_enum AS ENUM (
    'reconnaissance',
    'file_download',
    'execution',
    'persistence',
    'networking',
    'privilege_escalation'
);

CREATE TYPE threat_level_enum AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

-- Attackers Table
CREATE TABLE attackers (
    ip_address VARCHAR(45) PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL,
    asn INTEGER,
    isp VARCHAR(255),
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    total_commands INTEGER DEFAULT 0,
    total_downloads INTEGER DEFAULT 0,
    max_severity severity_enum DEFAULT 'INFO',
    threat_level threat_level_enum DEFAULT 'low',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Sessions Table
CREATE TABLE sessions (
    id VARCHAR(255) PRIMARY KEY,
    attacker_ip VARCHAR(45) NOT NULL REFERENCES attackers(ip_address),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    status session_status_enum DEFAULT 'active',
    total_commands INTEGER DEFAULT 0,
    protocol VARCHAR(10) DEFAULT 'ssh',
    honeypot_version VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attacks Table (Main event log)
CREATE TABLE attacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    session_id VARCHAR(255) REFERENCES sessions(id),
    attacker_ip VARCHAR(45) NOT NULL REFERENCES attackers(ip_address),
    event_type event_type_enum NOT NULL,
    severity severity_enum DEFAULT 'INFO',
    country_code VARCHAR(2),
    asn INTEGER,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Commands Table
CREATE TABLE commands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    command TEXT NOT NULL,
    classification command_classification_enum,
    success BOOLEAN DEFAULT true,
    output TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Downloads Table
CREATE TABLE downloads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) NOT NULL REFERENCES sessions(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(512),
    file_hash VARCHAR(64),
    file_size INTEGER,
    url VARCHAR(1024),
    file_type VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Credentials Table
CREATE TABLE credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id VARCHAR(255) REFERENCES sessions(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    success BOOLEAN DEFAULT false,
    attempt_count INTEGER DEFAULT 1,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ASN Lookups Cache
CREATE TABLE asn_lookups (
    asn INTEGER PRIMARY KEY,
    isp VARCHAR(255),
    country_code VARCHAR(2),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    lookup_count INTEGER DEFAULT 0
);

-- Activity Statistics (Pre-calculated)
CREATE TABLE activity_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE NOT NULL,
    hour INTEGER,
    attack_count INTEGER DEFAULT 0,
    unique_attackers INTEGER DEFAULT 0,
    unique_countries INTEGER DEFAULT 0,
    total_commands INTEGER DEFAULT 0,
    total_downloads INTEGER DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, hour)
);

-- Indexes for Performance
CREATE INDEX idx_attacks_timestamp ON attacks(timestamp DESC);
CREATE INDEX idx_attacks_session_id ON attacks(session_id);
CREATE INDEX idx_attacks_attacker_ip ON attacks(attacker_ip);
CREATE INDEX idx_attacks_severity ON attacks(severity);
CREATE INDEX idx_attacks_country_code ON attacks(country_code);

CREATE INDEX idx_sessions_attacker_ip ON sessions(attacker_ip);
CREATE INDEX idx_sessions_start_time ON sessions(start_time DESC);
CREATE INDEX idx_sessions_status ON sessions(status);

CREATE INDEX idx_commands_session_id ON commands(session_id);
CREATE INDEX idx_commands_timestamp ON commands(timestamp DESC);
CREATE INDEX idx_commands_classification ON commands(classification);

CREATE INDEX idx_downloads_session_id ON downloads(session_id);
CREATE INDEX idx_downloads_timestamp ON downloads(timestamp DESC);

CREATE INDEX idx_credentials_username ON credentials(username);
CREATE INDEX idx_credentials_timestamp ON credentials(timestamp DESC);

CREATE INDEX idx_attackers_last_seen ON attackers(last_seen DESC);
CREATE INDEX idx_attackers_country_code ON attackers(country_code);
CREATE INDEX idx_attackers_threat_level ON attackers(threat_level);

CREATE INDEX idx_activity_stats_date ON activity_stats(date DESC);
CREATE INDEX idx_activity_stats_hour ON activity_stats(date, hour);

-- Trigger to update attacker stats
CREATE OR REPLACE FUNCTION update_attacker_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE attackers
    SET last_seen = NEW.timestamp,
        total_sessions = (SELECT COUNT(*) FROM sessions WHERE attacker_ip = NEW.attacker_ip),
        total_commands = (SELECT COUNT(*) FROM commands WHERE session_id IN (SELECT id FROM sessions WHERE attacker_ip = NEW.attacker_ip)),
        total_downloads = (SELECT COUNT(*) FROM downloads WHERE session_id IN (SELECT id FROM sessions WHERE attacker_ip = NEW.attacker_ip))
    WHERE ip_address = NEW.attacker_ip;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_attacker_stats_on_attack
AFTER INSERT ON attacks
FOR EACH ROW
EXECUTE FUNCTION update_attacker_stats();
```

## Data Relationships

- **attackers** (1) ← (N) **sessions**: One attacker can have multiple sessions
- **sessions** (1) ← (N) **commands**: One session can have multiple commands
- **sessions** (1) ← (N) **downloads**: One session can have multiple downloads
- **sessions** (1) ← (N) **credentials**: One session can have multiple credential attempts
- **attackers** (1) ← (N) **attacks**: One attacker can generate multiple events
- **asn_lookups** (1) ← (N) **attackers**: Multiple attackers can share the same ASN

