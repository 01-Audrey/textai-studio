# Deployment Guide - TextAI Studio

Complete guide for deploying TextAI Studio to production.

## Table of Contents

1. [Pre-Deployment](#pre-deployment)
2. [Platform-Specific Guides](#platform-specific-guides)
3. [Configuration](#configuration)
4. [Security](#security)
5. [Monitoring](#monitoring)
6. [Backup & Recovery](#backup--recovery)
7. [Scaling](#scaling)

## Pre-Deployment

### Requirements Checklist

#### System Requirements
- [ ] Python 3.10+ installed
- [ ] Docker & Docker Compose (if using containers)
- [ ] 4GB+ RAM available
- [ ] 5GB+ disk space
- [ ] Network access for model downloads

#### Configuration Requirements
- [ ] .env file configured
- [ ] SECRET_KEY generated (32+ chars)
- [ ] ADMIN_PASSWORD set (strong password)
- [ ] All required environment variables set
- [ ] Feature flags configured

#### Security Requirements
- [ ] HTTPS enabled (production)
- [ ] Secrets not in code
- [ ] DEBUG=false in production
- [ ] Rate limiting enabled
- [ ] Firewall configured

### Pre-Deployment Testing
```bash
# 1. Run application locally
streamlit run textai_studio_app.py

# 2. Test all features
# - User signup/login
# - All 4 tools (sentiment, summary, fake news, job matcher)
# - Batch processing
# - Analytics dashboard
# - Admin dashboard

# 3. Check logs for errors
tail -f logs/app.log

# 4. Performance test
# - Model loading time
# - Query response time
# - Batch processing speed
```

---

## Platform-Specific Guides

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+

#### Deployment Steps
```bash
# 1. Prepare server
ssh user@your-server.com

# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 3. Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. Clone repository
git clone https://github.com/yourusername/textai-studio.git
cd textai-studio/deployment

# 5. Configure environment
cp .env.example .env
nano .env  # Fill in production values

# 6. Generate secrets
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env

# 7. Build and start
docker-compose up -d

# 8. Verify deployment
docker-compose ps
docker-compose logs -f

# 9. Test application
curl http://localhost:8501/_stcore/health

# 10. Access application
# http://your-server.com:8501
```

#### Post-Deployment
```bash
# Enable auto-restart
docker-compose down
nano docker-compose.yml  # Ensure restart: unless-stopped

docker-compose up -d

# Set up log rotation
sudo nano /etc/logrotate.d/textai-studio
```

---

### Option 2: Streamlit Cloud

#### Prerequisites
- GitHub account
- Streamlit Cloud account (streamlit.io/cloud)

#### Deployment Steps

1. **Push to GitHub**
```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/textai-studio.git
   git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to share.streamlit.io
   - Click "New app"
   - Select repository: yourusername/textai-studio
   - Main file: textai_studio_app.py
   - Click "Deploy"

3. **Configure Secrets**
   - Go to app settings
   - Add secrets from .env file
   - Format (TOML):
```toml
   SECRET_KEY = "your-secret-key"
   ADMIN_PASSWORD = "your-admin-password"
```

4. **Custom Domain (Optional)**
   - Settings → General → Custom subdomain
   - Or use CNAME for custom domain

---

### Option 3: AWS ECS (Container Service)

#### Prerequisites
- AWS account
- AWS CLI configured
- ECR repository created

#### Deployment Steps
```bash
# 1. Build and tag image
docker build -t textai-studio .
docker tag textai-studio:latest YOUR_ECR_REPO/textai-studio:latest

# 2. Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_REPO
docker push YOUR_ECR_REPO/textai-studio:latest

# 3. Create task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# 4. Create ECS service
aws ecs create-service \
  --cluster textai-cluster \
  --service-name textai-service \
  --task-definition textai-studio \
  --desired-count 1 \
  --launch-type FARGATE

# 5. Configure load balancer (optional)
# Set up ALB for HTTPS and custom domain
```

---

### Option 4: Heroku

#### Prerequisites
- Heroku account
- Heroku CLI installed

#### Deployment Steps
```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create textai-studio

# 3. Add buildpack
heroku buildpacks:set heroku/python

# 4. Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_PASSWORD=your-admin-password

# 5. Create Procfile
echo "web: streamlit run textai_studio_app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# 6. Deploy
git add .
git commit -m "Heroku deployment"
git push heroku main

# 7. Open app
heroku open
```

---

### Option 5: DigitalOcean App Platform

#### Prerequisites
- DigitalOcean account
- GitHub repository

#### Deployment Steps

1. **Connect Repository**
   - Go to DigitalOcean App Platform
   - Create New App
   - Connect GitHub repository

2. **Configure Build**
   - Detected: Docker or Python
   - Build Command: `pip install -r requirements.txt`
   - Run Command: `streamlit run textai_studio_app.py --server.port=8080 --server.address=0.0.0.0`

3. **Add Environment Variables**
   - SECRET_KEY
   - ADMIN_PASSWORD
   - Other variables from .env

4. **Configure Resources**
   - Basic: 512MB RAM, 1 CPU
   - Recommended: 2GB RAM, 1 CPU
   - Professional: 4GB RAM, 2 CPU

5. **Deploy**
   - Click "Deploy"
   - Wait for build completion
   - Access provided URL

---

## Configuration

### Production .env
```bash
# Application
APP_NAME=TextAI Studio
APP_ENV=production
DEBUG=false

# Security (CHANGE THESE!)
SECRET_KEY=generate-with-python-secrets-module
ADMIN_PASSWORD=strong-secure-password-here

# Server
HOST=0.0.0.0
PORT=8501

# Performance
ENABLE_MODEL_CACHE=true
CACHE_TTL=300
MAX_BATCH_SIZE=100

# Rate Limiting
GUEST_RATE_LIMIT=10
USER_RATE_LIMIT=100
PRO_RATE_LIMIT=1000

# Features
ENABLE_USER_SIGNUP=true
ENABLE_API_ACCESS=true
ENABLE_ANALYTICS=true
ENABLE_ADMIN_DASHBOARD=true
```

### Secrets Management

#### Option 1: Environment Variables
```bash
# Set in hosting platform
# AWS: Parameter Store, Secrets Manager
# Heroku: Config Vars
# DigitalOcean: App-Level Environment Variables
```

#### Option 2: Secrets File (Docker)
```bash
# Create secrets file
echo "SECRET_KEY=..." > secrets.txt
echo "ADMIN_PASSWORD=..." >> secrets.txt

# Mount as volume
docker run -v $(pwd)/secrets.txt:/run/secrets/secrets.txt textai-studio
```

---

## Security

### Security Checklist

#### Before Deployment
- [ ] Strong SECRET_KEY (32+ random characters)
- [ ] Strong ADMIN_PASSWORD (12+ chars, mixed case, numbers, symbols)
- [ ] DEBUG=false in production
- [ ] No secrets in code or git history
- [ ] .env file in .gitignore
- [ ] Dependencies up to date
- [ ] Rate limiting enabled
- [ ] CORS configured properly

#### After Deployment
- [ ] HTTPS enabled (SSL/TLS certificate)
- [ ] Firewall configured (allow only 443, 80, 22)
- [ ] Admin password changed from default
- [ ] Regular security updates scheduled
- [ ] Monitoring and alerting enabled
- [ ] Backup system configured
- [ ] Incident response plan ready

### HTTPS Setup

#### Let's Encrypt (Free SSL)
```bash
# Install Certbot
sudo apt-get install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Configure Nginx
sudo nano /etc/nginx/sites-available/textai-studio
```

Nginx config:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/textai-studio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Auto-renew
sudo certbot renew --dry-run
```

---

## Monitoring

### Health Checks
```bash
# Application health
curl http://your-domain.com/_stcore/health

# Container health (Docker)
docker inspect --format='{{.State.Health.Status}}' textai-studio
```

### Logging
```bash
# Application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f

# System logs
journalctl -u docker -f
```

### Metrics to Monitor

- **Application**: Response time, error rate, active users
- **System**: CPU usage, memory usage, disk space
- **Models**: Inference time, cache hit rate
- **Database**: Query time, connection pool

### Alerting

Set up alerts for:
- Application down (health check fails)
- High error rate (>5%)
- Slow response time (>5s)
- Low disk space (<10%)
- High memory usage (>90%)

---

## Backup & Recovery

### Backup Strategy

#### Daily Backups
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup user data
tar -czf $BACKUP_DIR/user_data_$DATE.tar.gz user_data/

# Backup database (if using)
# pg_dump -U user dbname > $BACKUP_DIR/db_$DATE.sql

# Keep last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

#### Automated Backups
```bash
# Add to crontab
crontab -e

# Daily at 2 AM
0 2 * * * /path/to/backup.sh
```

### Recovery
```bash
# Restore from backup
tar -xzf backup_20241229_020000.tar.gz -C /app/

# Restart application
docker-compose restart
```

---

## Scaling

### Horizontal Scaling

#### Multiple Instances (Load Balancer)
```yaml
# docker-compose.scale.yml
version: '3.8'

services:
  app:
    deploy:
      replicas: 3
    # ... rest of config

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - app
```

#### Kubernetes (Advanced)
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: textai-studio
spec:
  replicas: 3
  selector:
    matchLabels:
      app: textai-studio
  template:
    metadata:
      labels:
        app: textai-studio
    spec:
      containers:
      - name: textai-studio
        image: textai-studio:latest
        ports:
        - containerPort: 8501
```

### Vertical Scaling
```yaml
# docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Support

- Documentation: See `/docs` directory
- Issues: GitHub Issues
- Email: support@textai.app

---

**Last Updated**: December 2024  
**Version**: 1.0.0
