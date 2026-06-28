# 🚀 RestoCost - Complete Deployment Guide

Complete guide for deploying RestoCost from scratch using Docker or on a Linux Debian server.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start with Docker](#quick-start-with-docker)
- [Linux Debian Server Setup](#linux-debian-server-setup)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Creating the Super Admin](#creating-the-super-admin)
- [Production Deployment](#production-deployment)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### For Docker Deployment
- **Docker** 24.0+ ([Install](https://docs.docker.com/get-docker/))
- **Docker Compose** 2.20+ (included with Docker Desktop)
- **Git** ([Install](https://git-scm.com/downloads))

### For Linux Debian Server
- **Debian** 11 (Bullseye) or 12 (Bookworm)
- **Root or sudo access**
- **Git**, **curl**, **wget**
- Minimum **2GB RAM**, **10GB disk space**

---

## 🐳 Quick Start with Docker

### Step 1: Clone the Repository

```bash
git clone https://github.com/andrewarnaud1/restocost.git
cd restocost
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your favorite editor
nano .env  # or vim, code, etc.
```

**Important variables to change:**
```bash
# Security - MUST CHANGE IN PRODUCTION
SECRET_KEY=your-super-secret-key-here-minimum-32-characters

# Database credentials
POSTGRES_USER=restocost
POSTGRES_PASSWORD=change-this-password

# Environment
ENVIRONMENT=production
DEBUG=False
```

Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 3: Start All Services

```bash
# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

You should see:
```
NAME                   STATUS    PORTS
restocost-postgres     Up        5432
restocost-backend      Up        0.0.0.0:8000->8000
```

### Step 4: Create Super Admin

```bash
# Enter the backend container
docker-compose exec backend bash

# Create admin user
restocost create-admin

# Follow prompts
📧 Admin email: admin@example.com
🔑 Admin password: ********
🔑 Confirm password: ********

✅ Super admin user created successfully!
```

### Step 5: Verify Installation

```bash
# Test health endpoint
curl http://localhost:8000/api/health

# Test database health
curl http://localhost:8000/api/health/db

# View API documentation
open http://localhost:8000/docs
```

### Step 6: Login and Create Users

```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your-password"
  }'

# Use the access_token to create other users
# See docs/USER_MANAGEMENT.md for details
```

---

## 🐧 Linux Debian Server Setup

### Complete Setup from Scratch

#### 1. Update System

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    libpq-dev \
    postgresql \
    postgresql-contrib \
    nginx \
    supervisor
```

#### 2. Install Python 3.13

Debian 12 comes with Python 3.11. We need to install Python 3.13:

```bash
# Add deadsnakes PPA (for newer Python versions)
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Install Python 3.13
sudo apt install -y \
    python3.13 \
    python3.13-venv \
    python3.13-dev \
    python3-pip

# Verify installation
python3.13 --version
# Output: Python 3.13.x
```

#### 3. Setup PostgreSQL Database

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE restocost;
CREATE USER restocost WITH PASSWORD 'your-secure-password';
GRANT ALL PRIVILEGES ON DATABASE restocost TO restocost;

# Exit psql
\q
```

#### 4. Clone and Setup Application

```bash
# Create application directory
sudo mkdir -p /var/www/restocost
sudo chown $USER:$USER /var/www/restocost

# Clone repository
cd /var/www
git clone https://github.com/andrewarnaud1/restocost.git
cd restocost

# Create Python virtual environment
cd backend
python3.13 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"
```

#### 5. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

Update these values:
```bash
# Database (local PostgreSQL)
DATABASE_URL=postgresql+asyncpg://restocost:your-secure-password@localhost:5432/restocost

# Security
SECRET_KEY=your-generated-secret-key

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS - Add your domain
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

#### 6. Initialize Database

```bash
# Apply migrations
restocost db upgrade

# Or using alembic directly
alembic upgrade head
```

#### 7. Create Super Admin

```bash
# Interactive mode
restocost create-admin

# Follow prompts
📧 Admin email: admin@yourdomain.com
🔑 Admin password: ********
🔑 Confirm password: ********
```

#### 8. Setup Supervisor (Process Manager)

```bash
# Create supervisor configuration
sudo nano /etc/supervisor/conf.d/restocost.conf
```

Add this configuration:
```ini
[program:restocost]
command=/var/www/restocost/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/var/www/restocost/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/restocost/restocost.log
stderr_logfile=/var/log/restocost/restocost-error.log
environment=PATH="/var/www/restocost/backend/.venv/bin"
```

Create log directory:
```bash
sudo mkdir -p /var/log/restocost
sudo chown www-data:www-data /var/log/restocost
```

Start the service:
```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Start RestoCost
sudo supervisorctl start restocost

# Check status
sudo supervisorctl status restocost
```

#### 9. Setup Nginx (Reverse Proxy)

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/restocost
```

Add this configuration:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to FastAPI backend
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Health check endpoint
    location /api/health {
        proxy_pass http://127.0.0.1:8000/api/health;
        access_log off;
    }
}
```

Enable the site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/restocost /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

#### 10. Setup SSL with Let's Encrypt (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

---

## ⚙️ Environment Configuration

### Environment Variables Explained

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DATABASE_URL` | PostgreSQL connection string | - | ✅ |
| `SECRET_KEY` | JWT signing key (32+ chars) | - | ✅ |
| `ALGORITHM` | JWT algorithm | `HS256` | ❌ |
| `API_V1_PREFIX` | API route prefix | `/api` | ❌ |
| `PROJECT_NAME` | Application name | `RestoCost` | ❌ |
| `VERSION` | Application version | `0.1.0` | ❌ |
| `ENVIRONMENT` | Environment type | `development` | ❌ |
| `DEBUG` | Enable debug mode | `True` | ❌ |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` | ✅ (prod) |

### Production Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Use strong PostgreSQL password
- [ ] Enable HTTPS/SSL
- [ ] Setup firewall (UFW)
- [ ] Regular backups
- [ ] Monitor logs

---

## 🗄️ Database Setup

### Using Alembic Migrations

```bash
# Initialize database (first time)
restocost db init

# Apply migrations
restocost db upgrade

# Create new migration (after model changes)
cd backend
alembic revision --autogenerate -m "Description of changes"

# Apply new migration
restocost db upgrade
```

### Database Backup

```bash
# Backup PostgreSQL database
pg_dump -U restocost -d restocost > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql -U restocost -d restocost < backup_20250101_120000.sql
```

### Docker Database Backup

```bash
# Backup
docker-compose exec postgres pg_dump -U restocost restocost > backup.sql

# Restore
docker-compose exec -T postgres psql -U restocost restocost < backup.sql
```

---

## 👤 Creating the Super Admin

The super admin is the first user and has full system access.

### Using CLI (Recommended)

```bash
# Interactive mode
restocost create-admin

# With email
restocost create-admin --email admin@example.com

# With both (not recommended - password in history)
restocost create-admin --email admin@example.com --password SecurePass123
```

### Inside Docker Container

```bash
# Enter container
docker-compose exec backend bash

# Create admin
restocost create-admin

# Exit
exit
```

### What Happens Next?

1. Admin logs in via `/api/auth/login`
2. Admin creates owners via `/api/admin/users`
3. Owners create staff via `/api/admin/users`

See [docs/USER_MANAGEMENT.md](./USER_MANAGEMENT.md) for complete user management guide.

---

## 🏭 Production Deployment

### System Service (systemd)

Alternative to Supervisor, using systemd:

```bash
# Create service file
sudo nano /etc/systemd/system/restocost.service
```

Add:
```ini
[Unit]
Description=RestoCost FastAPI Application
After=network.target postgresql.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/var/www/restocost/backend
Environment="PATH=/var/www/restocost/backend/.venv/bin"
ExecStart=/var/www/restocost/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable restocost
sudo systemctl start restocost
sudo systemctl status restocost
```

### Performance Tuning

```bash
# Increase worker count based on CPU cores
# Formula: (2 x CPU_CORES) + 1
uvicorn app.main:app --workers 5  # For 2 CPU cores

# Enable production optimizations
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1
```

### Monitoring

```bash
# View logs
sudo tail -f /var/log/restocost/restocost.log

# With Docker
docker-compose logs -f backend

# Check resource usage
htop
docker stats
```

---

## 🔍 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Database Connection Errors

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-16-main.log
```

### Docker Issues

```bash
# Restart all services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d

# View container logs
docker-compose logs backend
docker-compose logs postgres
```

### Permission Errors

```bash
# Fix ownership
sudo chown -R www-data:www-data /var/www/restocost

# Fix permissions
sudo chmod -R 755 /var/www/restocost
```

### Migration Errors

```bash
# Reset database (⚠️ DELETES ALL DATA)
restocost db reset --force

# Reapply migrations
restocost db upgrade
```

---

## 📚 Additional Resources

- [User Management Guide](./USER_MANAGEMENT.md)
- [API Documentation](http://localhost:8000/docs)
- [GitHub Repository](https://github.com/andrewarnaud1/restocost)
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Last Updated:** 2026-06-19
**Version:** 0.1.0
**Maintainer:** Andrew Arnaud
