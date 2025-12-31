# Security Guide - TextAI Studio

Comprehensive security guidelines for TextAI Studio deployment and operation.

## Table of Contents

1. [Security Checklist](#security-checklist)
2. [Authentication & Authorization](#authentication--authorization)
3. [Data Security](#data-security)
4. [Network Security](#network-security)
5. [API Security](#api-security)
6. [Operational Security](#operational-security)
7. [Incident Response](#incident-response)
8. [Security Updates](#security-updates)

---

## Security Checklist

### Pre-Deployment

#### Configuration
- [ ] Strong SECRET_KEY generated (32+ characters)
- [ ] Strong ADMIN_PASSWORD set (12+ chars, mixed case, numbers, symbols)
- [ ] DEBUG=false in production
- [ ] No secrets in code or git history
- [ ] .env file in .gitignore
- [ ] All environment variables reviewed
- [ ] Default credentials changed

#### Dependencies
- [ ] All dependencies from requirements.txt
- [ ] No deprecated packages
- [ ] Security vulnerabilities checked (pip-audit)
- [ ] Latest stable versions used

#### Infrastructure
- [ ] HTTPS enabled (SSL/TLS certificate)
- [ ] Firewall configured
- [ ] Only necessary ports open (443, 80, 22)
- [ ] SSH key-based authentication
- [ ] Root login disabled

### Post-Deployment

#### Monitoring
- [ ] Logging enabled
- [ ] Error tracking configured
- [ ] Health checks working
- [ ] Alerts configured
- [ ] Regular log reviews scheduled

#### Maintenance
- [ ] Backup system configured
- [ ] Update schedule defined
- [ ] Incident response plan ready
- [ ] Security audit scheduled

---

## Authentication & Authorization

### Password Security

#### Requirements

Enforce strong passwords:
- Minimum 8 characters (recommend 12+)
- Mix of uppercase, lowercase, numbers, symbols
- No common passwords
- No personal information

#### Implementation

Example password hashing with bcrypt:
```python
import bcrypt

def hash_password(password):
    # Hash password with bcrypt
    # Cost factor: 12 (2^12 iterations)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    # Verify password against hash
    return bcrypt.checkpw(
        password.encode('utf-8'),
        hashed.encode('utf-8')
    )
```

#### Best Practices

✅ Use bcrypt (not MD5, SHA1)
✅ Salt every password
✅ Cost factor >= 12
✅ Never store plaintext passwords
✅ Hash on server-side only
❌ Don't limit password length
❌ Don't truncate passwords

### Session Management

#### Session Security
```python
# Streamlit session state
if 'user' not in st.session_state:
    st.session_state.user = None
    st.session_state.session_id = secrets.token_hex(32)

# Session timeout (30 minutes)
SESSION_TIMEOUT = 1800

if 'last_activity' in st.session_state:
    if time.time() - st.session_state.last_activity > SESSION_TIMEOUT:
        # Logout user
        st.session_state.user = None
```

#### Best Practices

✅ Generate random session IDs
✅ Implement session timeout
✅ Regenerate session on login
✅ Clear session on logout
✅ Use secure cookies (httpOnly, secure, sameSite)

### API Authentication

#### API Key Format
```
sk_[32 random bytes in base64]
Total: 40+ characters
```

#### Generation
```python
import secrets
import base64

def generate_api_key():
    # Generate secure API key
    # 32 random bytes
    random_bytes = secrets.token_bytes(32)
    # Base64 encode
    encoded = base64.b64encode(random_bytes).decode('utf-8')
    # Add prefix
    return f"sk_{encoded}"
```

#### Storage
```python
# Store hash, not plaintext
import hashlib

def hash_api_key(key):
    # Hash API key for storage
    return hashlib.sha256(key.encode()).hexdigest()

# Store only hash in database
api_keys_db[hash_api_key(key)] = user_id
```

#### Best Practices

✅ Use cryptographically secure random
✅ Store hashed version
✅ Allow key rotation
✅ Implement key expiration
✅ Log key usage
❌ Don't log full keys
❌ Don't expose keys in URLs

---

## Data Security

### Encryption at Rest

#### File Permissions
```bash
# User data directory
chmod 700 user_data/
chmod 600 user_data/*.json

# Only owner can read/write
chown appuser:appuser user_data/
```

#### Sensitive Data

Encrypt sensitive fields:
```python
from cryptography.fernet import Fernet

# Generate key (store in .env)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted = cipher.encrypt(data.encode())

# Decrypt
decrypted = cipher.decrypt(encrypted).decode()
```

### Encryption in Transit

#### HTTPS Setup

Required in production. See DEPLOYMENT.md for complete Nginx configuration with SSL.

#### SSL Certificate
```bash
# Let's Encrypt (free)
sudo certbot certonly --standalone -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Data Backup

#### Backup Strategy
```bash
#!/bin/bash
# secure_backup.sh

BACKUP_DIR="/secure/backups"
DATE=$(date +%Y%m%d_%H%M%S)
ENCRYPTION_KEY="/secure/keys/backup.key"

# Backup user data with encryption
tar -czf - user_data/ |     openssl enc -aes-256-cbc -salt -pass file:$ENCRYPTION_KEY     -out $BACKUP_DIR/user_data_$DATE.tar.gz.enc

# Set permissions
chmod 600 $BACKUP_DIR/user_data_$DATE.tar.gz.enc

# Keep last 30 days
find $BACKUP_DIR -name "*.enc" -mtime +30 -delete
```

---

## Network Security

### Firewall Configuration

#### UFW (Ubuntu)
```bash
# Enable firewall
sudo ufw enable

# Allow SSH (change default port recommended)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Check status
sudo ufw status verbose
```

### DDoS Protection

#### Rate Limiting (Application Level)

Implemented in RateLimiter class. See API Security section.

### CORS Configuration
```python
# Streamlit config.toml
[server]
enableCORS = false
enableXsrfProtection = true
```

---

## API Security

### Rate Limiting

#### Implementation
```python
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self):
        self.requests = {}
        self.limits = {
            'guest': 10,
            'user': 100,
            'pro': 1000
        }

    def check_limit(self, user_id, tier):
        # Check if user is within rate limit
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)

        # Clean old requests
        if user_id in self.requests:
            self.requests[user_id] = [
                req for req in self.requests[user_id]
                if req > hour_ago
            ]
        else:
            self.requests[user_id] = []

        # Check limit
        count = len(self.requests[user_id])
        limit = self.limits.get(tier, 10)

        if count >= limit:
            return False

        # Record request
        self.requests[user_id].append(now)
        return True
```

### Input Validation

#### Sanitize Inputs
```python
import html
import re

def sanitize_text(text, max_length=10000):
    # Sanitize user input
    # Remove null bytes
    text = text.replace('\x00', '')

    # Truncate
    text = text[:max_length]

    # Escape HTML
    text = html.escape(text)

    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    return text.strip()
```

---

## Operational Security

### Logging

#### What to Log

✅ Authentication attempts (success/failure)
✅ Authorization failures
✅ API key usage
✅ Rate limit violations
✅ Input validation failures
✅ System errors
❌ Passwords (never!)
❌ Full API keys
❌ Personal data (unless necessary)

#### Log Format
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring

#### Health Checks
```python
def health_check():
    # Comprehensive health check
    status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }

    # Check models loaded
    try:
        sentiment_model = load_sentiment_model()
        status['checks']['models'] = 'ok'
    except Exception:
        status['checks']['models'] = 'error'
        status['status'] = 'unhealthy'

    return status
```

---

## Incident Response

### Incident Response Plan

#### 1. Detection
- Monitor alerts
- Check logs
- User reports

#### 2. Containment
```bash
# Take affected service offline
docker-compose down

# Preserve evidence
cp -r logs/ incident_logs_$(date +%Y%m%d)/
```

#### 3. Investigation
- Analyze logs
- Identify attack vector
- Assess damage

#### 4. Remediation
- Fix vulnerability
- Update security
- Restore from backup if needed

#### 5. Recovery
```bash
# Restore service
git pull origin main
docker-compose build
docker-compose up -d
```

#### 6. Post-Incident
- Document incident
- Update procedures
- Implement preventive measures

---

## Security Updates

### Update Process

1. Subscribe to Security Advisories
2. Regular Vulnerability Scans
```bash
   pip install pip-audit
   pip-audit
```
3. Test Updates in staging
4. Apply Updates to production
5. Verify deployment

### Security Audit Schedule

- **Daily**: Review security logs
- **Weekly**: Check for updates
- **Monthly**: Vulnerability scan
- **Quarterly**: Security audit
- **Annually**: Penetration test

---

## Contact

For security issues:
- **Email**: security@textai.app
- **Response Time**: 24 hours for critical issues

---

**Last Updated**: December 2024  
**Version**: 1.0.0
