# Deployment Guide

## Prerequisites

### Local Development
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Docker & Docker Compose
- Git

### VPS Requirements
- Ubuntu 22.04 LTS
- 2GB+ RAM
- 20GB+ SSD
- Static IP address
- Ports 22, 80, 443 open for SSH, HTTP, HTTPS
- Port 2222 open for Cowrie SSH (alternative)

---

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository>
cd Honeypot_LiveAttack
```

### 2. Backend Setup

```bash
# Create Python virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Start development server
npm run dev
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb honeypot_dashboard

# Run schema creation (from docs/DATABASE_SCHEMA.md)
psql honeypot_dashboard < schema.sql
```

### 5. Docker Compose (All-in-One)

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## VPS Deployment (Ubuntu 22.04)

### 1. Initial Server Setup

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install dependencies
sudo apt install -y \
  python3.10 \
  python3.10-venv \
  postgresql \
  postgresql-contrib \
  nginx \
  nodejs \
  npm \
  docker.io \
  docker-compose \
  certbot \
  python3-certbot-nginx \
  git

# Add current user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Enable required services
sudo systemctl enable postgresql nginx docker
sudo systemctl start postgresql nginx docker
```

### 2. PostgreSQL Setup

```bash
# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE honeypot_dashboard;
CREATE USER honeypot_user WITH PASSWORD 'strong_password_here';
ALTER ROLE honeypot_user SET client_encoding TO 'utf8';
ALTER ROLE honeypot_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE honeypot_user SET default_transaction_deferrable TO on;
ALTER ROLE honeypot_user SET default_transaction_read_committed TO off;
GRANT ALL PRIVILEGES ON DATABASE honeypot_dashboard TO honeypot_user;
EOF

# Load schema
sudo -u postgres psql honeypot_dashboard < schema.sql
```

### 3. Application Deployment

```bash
# Clone repository
git clone <repository> /opt/honeypot-dashboard
cd /opt/honeypot-dashboard

# Create application user
sudo useradd -m -d /opt/honeypot-dashboard honeypot
sudo chown -R honeypot:honeypot /opt/honeypot-dashboard

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with production values

# Frontend build
cd ../frontend
npm install
npm run build

# Create systemd service for backend
sudo tee /etc/systemd/system/honeypot-backend.service > /dev/null << EOF
[Unit]
Description=Honeypot Dashboard Backend
After=network.target postgresql.service

[Service]
Type=notify
User=honeypot
WorkingDirectory=/opt/honeypot-dashboard/backend
Environment="PATH=/opt/honeypot-dashboard/backend/venv/bin"
ExecStart=/opt/honeypot-dashboard/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable honeypot-backend
sudo systemctl start honeypot-backend
```

### 4. Nginx Configuration

```bash
# Create Nginx config
sudo tee /etc/nginx/sites-available/honeypot-dashboard > /dev/null << 'EOF'
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 10M;

    location / {
        root /opt/honeypot-dashboard/frontend/out;
        try_files $uri $uri/ =404;
    }

    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }

    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/honeypot-dashboard /etc/nginx/sites-enabled/

# Test and reload Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 5. SSL Certificate (Let's Encrypt)

```bash
# Generate SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### 6. Cowrie Integration

```bash
# Install Cowrie
sudo apt install -y cowrie

# Configure Cowrie to output JSON logs
# Edit: /etc/cowrie/cowrie.cfg
# Ensure JSON output is enabled

# Setup log watching for database ingestion
# Use backend/app/parsers/cowrie_parser.py

# Create log watcher service
sudo tee /etc/systemd/system/honeypot-log-parser.service > /dev/null << EOF
[Unit]
Description=Honeypot Log Parser
After=postgresql.service

[Service]
Type=simple
User=honeypot
WorkingDirectory=/opt/honeypot-dashboard/backend
Environment="PATH=/opt/honeypot-dashboard/backend/venv/bin"
ExecStart=/opt/honeypot-dashboard/backend/venv/bin/python -m app.parsers.cowrie_watcher
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable honeypot-log-parser
sudo systemctl start honeypot-log-parser
```

---

## Docker Deployment (Production)

### Build and Push Images

```bash
# Backend image
cd backend
docker build -t your-registry/honeypot-backend:latest .
docker push your-registry/honeypot-backend:latest

# Frontend image
cd ../frontend
docker build -t your-registry/honeypot-frontend:latest .
docker push your-registry/honeypot-frontend:latest
```

### Docker Compose Production File

```bash
# Use docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose -f docker-compose.prod.yml down
```

---

## Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Database connection
psql -U honeypot_user -d honeypot_dashboard -c "SELECT NOW();"

# Nginx status
sudo systemctl status nginx
```

### Log Rotation

```bash
# Configure logrotate for application logs
sudo tee /etc/logrotate.d/honeypot-dashboard > /dev/null << EOF
/var/log/honeypot-dashboard/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 honeypot honeypot
    sharedscripts
    postrotate
        systemctl reload honeypot-backend > /dev/null 2>&1 || true
    endscript
}
EOF
```

### Database Backups

```bash
# Create backup script
sudo tee /usr/local/bin/backup-honeypot-db.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/honeypot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

pg_dump -U honeypot_user honeypot_dashboard | gzip > $BACKUP_DIR/honeypot_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "honeypot_*.sql.gz" -mtime +30 -delete

echo "Backup completed: honeypot_$DATE.sql.gz"
EOF

sudo chmod +x /usr/local/bin/backup-honeypot-db.sh

# Schedule with cron (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-honeypot-db.sh") | crontab -
```

### Monitoring & Alerts

```bash
# Install and configure monitoring
sudo apt install -y prometheus-node-exporter
sudo systemctl enable prometheus-node-exporter
sudo systemctl start prometheus-node-exporter
```

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
journalctl -u honeypot-backend -n 100

# Check database connection
python -c "import psycopg2; psycopg2.connect('dbname=honeypot_dashboard')"
```

### WebSocket Connection Issues
```bash
# Check Nginx proxy settings for WebSocket headers
# Ensure "Connection: upgrade" header is set
```

### High Database Load
```bash
# Monitor queries
sudo -u postgres psql honeypot_dashboard -c "SELECT query, calls FROM pg_stat_statements ORDER BY calls DESC LIMIT 10;"
```

---

## Security Hardening

See [SECURITY.md](./SECURITY.md) for detailed security configuration.

