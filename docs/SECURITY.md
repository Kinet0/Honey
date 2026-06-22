# Security Hardening Guide

## Overview

This guide provides security best practices for deploying and operating the Honeypot Dashboard in production.

---

## Application Security

### 1. Environment Variables

**Never commit sensitive data to version control:**

```bash
# .env.example (safe to commit)
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:3000

# .env (DO NOT commit)
# Contains actual secrets
```

### 2. CORS Configuration

```python
# backend/app/core/config.py
CORS_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com"
]

# Development only
if DEBUG:
    CORS_ORIGINS.append("http://localhost:3000")
```

### 3. CSRF Protection

```python
# Use FastAPI middleware for CSRF protection
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Rate Limiting

```python
# Use slowapi for rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/attacks/feed")
@limiter.limit("100/minute")
async def get_attacks_feed(request: Request):
    # Implementation
    pass
```

### 5. Input Validation

```python
# Use Pydantic for strict input validation
from pydantic import BaseModel, Field

class AttackFilter(BaseModel):
    country: Optional[str] = Field(None, max_length=2)
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)
```

### 6. SQL Injection Prevention

```python
# Use SQLAlchemy ORM - never raw SQL
# ✓ Good
session.query(Attack).filter(Attack.ip == user_input).all()

# ✗ Bad
session.execute(f"SELECT * FROM attacks WHERE ip = '{user_input}'")
```

### 7. XSS Prevention

```python
# In Next.js, always use dangerouslySetInnerHTML carefully
# Sanitize HTML output
import DOMPurify from 'dompurify';

const sanitized = DOMPurify.sanitize(html);
```

---

## Infrastructure Security

### 1. Firewall Configuration

```bash
# UFW (Ubuntu Firewall)
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp     # SSH
sudo ufw allow 80/tcp     # HTTP
sudo ufw allow 443/tcp    # HTTPS
sudo ufw enable
```

### 2. SSH Hardening

```bash
# Edit /etc/ssh/sshd_config
Port 2222                          # Change default port
PermitRootLogin no                 # Disable root login
PasswordAuthentication no           # Use key-based auth
PubkeyAuthentication yes
MaxAuthTries 3
MaxSessions 5
ClientAliveInterval 300
ClientAliveCountMax 2

# Reload SSH
sudo systemctl reload ssh
```

### 3. Fail2Ban Installation

```bash
sudo apt install -y fail2ban

# Create jail config
sudo tee /etc/fail2ban/jail.local > /dev/null << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[recidive]
enabled = true
EOF

sudo systemctl restart fail2ban
```

### 4. Nginx Security Headers

```nginx
# /etc/nginx/sites-available/honeypot-dashboard

# Security headers
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;

# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'" always;

# HSTS
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Disable server info
server_tokens off;
```

### 5. PostgreSQL Security

```bash
# Create restricted user for application
sudo -u postgres psql << EOF
CREATE USER honeypot_app WITH PASSWORD 'strong_password';
CREATE DATABASE honeypot_dashboard OWNER honeypot_app;

-- Restrict privileges
REVOKE CONNECT ON DATABASE honeypot_dashboard FROM PUBLIC;
GRANT CONNECT ON DATABASE honeypot_dashboard TO honeypot_app;

-- Connection limits
ALTER ROLE honeypot_app CONNECTION LIMIT 50;
EOF

# Configure pg_hba.conf
sudo tee -a /etc/postgresql/14/main/pg_hba.conf << EOF
local   honeypot_dashboard   honeypot_app   md5
host    honeypot_dashboard   honeypot_app   127.0.0.1/32   md5
EOF

# Enable SSL connections
sudo systemctl restart postgresql
```

### 6. Database Backups & Encryption

```bash
# Create encrypted backup
gpg --symmetric --cipher-algo AES256 backup.sql.gz

# Verify backups
gpg --decrypt backup.sql.gz.gpg | gunzip | psql -U honeypot_app -d honeypot_dashboard

# Store backups securely
# Consider: AWS S3, Backblaze, or encrypted external drive
```

---

## Monitoring & Auditing

### 1. Application Logging

```python
# backend/app/core/logging.py
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger(__name__)

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=10
)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### 2. Audit Logging

```python
# Log important actions
async def create_audit_log(
    action: str,
    user_ip: str,
    details: dict,
    session: Session
):
    log = AuditLog(
        action=action,
        user_ip=user_ip,
        details=details,
        timestamp=datetime.utcnow()
    )
    session.add(log)
    await session.commit()
```

### 3. Error Monitoring (Sentry)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://your-sentry-dsn@sentry.io/project-id",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

### 4. Intrusion Detection

```bash
# Install AIDE (Advanced Intrusion Detection Environment)
sudo apt install -y aide aide-common

# Initialize AIDE database
sudo aideinit

# Schedule daily checks
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/bin/aide --check") | crontab -
```

---

## DDoS Mitigation

### 1. Nginx Rate Limiting

```nginx
limit_req_zone $binary_remote_addr zone=attack_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;

server {
    location /api {
        limit_req zone=api_limit burst=20 nodelay;
        ...
    }
    
    location / {
        limit_req zone=attack_limit burst=50 nodelay;
        ...
    }
}
```

### 2. Cloudflare DDoS Protection

- Use Cloudflare for additional DDoS protection
- Enable WAF (Web Application Firewall)
- Set rate limiting rules in Cloudflare

### 3. Connection Limits

```bash
# Edit /etc/security/limits.conf
honeypot soft nofile 65536
honeypot hard nofile 65536
honeypot soft nproc 32768
honeypot hard nproc 32768
```

---

## Data Protection

### 1. Data Anonymization

```python
# Don't store raw passwords in logs
def sanitize_log_data(data: dict) -> dict:
    if 'password' in data:
        data['password'] = '****'
    if 'auth_token' in data:
        data['auth_token'] = 'REDACTED'
    return data
```

### 2. HTTPS/TLS

```bash
# Use modern TLS configuration
sudo tee /etc/nginx/snippets/ssl-params.conf > /dev/null << EOF
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
EOF

# Include in server block
include /etc/nginx/snippets/ssl-params.conf;
```

### 3. Database Encryption

```bash
# Enable PostgreSQL SSL connections
# In postgresql.conf
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file = '/etc/postgresql/server.key'
```

### 4. Secrets Management

```python
# Use python-dotenv and never log secrets
from dotenv import load_dotenv
import os

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD')

# Never print or log these values
```

---

## API Security

### 1. API Key Authentication (Optional)

```python
from fastapi import Depends, HTTPException

async def verify_api_key(request: Request):
    api_key = request.headers.get("X-API-Key")
    if api_key != os.getenv("ADMIN_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key

@app.get("/api/v1/admin/stats")
async def get_admin_stats(api_key: str = Depends(verify_api_key)):
    # Implementation
    pass
```

### 2. JWT Tokens

```python
from datetime import datetime, timedelta
import jwt

def create_access_token(data: dict, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    
    expire = datetime.utcnow() + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm="HS256"
    )
    return encoded_jwt
```

### 3. Dependency Validation

```python
# Always validate request data
@app.post("/api/v1/search")
async def search(filters: SearchFilters):
    # filters is automatically validated by Pydantic
    results = await search_attacks(filters)
    return results
```

---

## Incident Response

### 1. Breach Detection

```bash
# Monitor for unauthorized access
sudo grep "FAILED PASSWORD" /var/log/auth.log | wc -l

# Check for privilege escalation attempts
sudo grep "sudo:" /var/log/auth.log
```

### 2. Log Analysis

```bash
# Use tools to analyze suspicious activity
sudo apt install -y auditd
sudo systemctl enable auditd
sudo systemctl start auditd

# View audit logs
sudo ausearch -m execve
```

### 3. Emergency Procedures

- **Data Breach**: Immediately disable affected credentials
- **System Compromise**: Isolate server, preserve logs, initiate forensics
- **DDoS Attack**: Enable stricter rate limiting, notify Cloudflare

---

## Compliance Checklist

- [ ] HTTPS/TLS enabled and valid
- [ ] Firewall configured
- [ ] SSH hardened (key-based auth only)
- [ ] Fail2Ban active
- [ ] Regular backups with encryption
- [ ] Database user with restricted privileges
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Security headers in place
- [ ] Monitoring and alerting configured
- [ ] Regular security updates applied
- [ ] Access logs retained for audit
- [ ] Sensitive data not logged

