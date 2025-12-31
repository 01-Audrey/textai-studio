# Troubleshooting Guide - TextAI Studio

Common issues and solutions for TextAI Studio.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Runtime Errors](#runtime-errors)
3. [Performance Issues](#performance-issues)
4. [Docker Issues](#docker-issues)
5. [API Issues](#api-issues)
6. [Data Issues](#data-issues)
7. [Model Issues](#model-issues)

---

## Installation Issues

### Issue: pip install fails

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement...
```

**Solutions**:

1. **Upgrade pip**:
```bash
   python -m pip install --upgrade pip
```

2. **Use Python 3.10+**:
```bash
   python --version  # Should be 3.10 or higher
```

3. **Install from requirements.txt**:
```bash
   pip install -r requirements.txt
```

4. **Try minimal requirements**:
```bash
   pip install -r requirements-minimal.txt
```

---

### Issue: torch installation fails on Windows

**Symptoms**:
```
ERROR: Could not find a version that satisfies the requirement torch
```

**Solution**:

Install PyTorch separately first:
```bash
# CPU version
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu

# Then install rest
pip install -r requirements.txt
```

---

### Issue: transformers installation fails

**Symptoms**:
```
ERROR: Failed building wheel for tokenizers
```

**Solution**:

Install build tools:

**Windows**:
```bash
# Install Visual C++ Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
```

**Linux**:
```bash
sudo apt-get install build-essential
```

**Mac**:
```bash
xcode-select --install
```

---

## Runtime Errors

### Issue: ModuleNotFoundError

**Symptoms**:
```python
ModuleNotFoundError: No module named 'streamlit'
```

**Solutions**:

1. **Verify installation**:
```bash
   pip list | grep streamlit
```

2. **Reinstall**:
```bash
   pip install streamlit==1.29.0
```

3. **Check Python version**:
```bash
   python --version
   which python  # Ensure correct Python
```

---

### Issue: Port already in use

**Symptoms**:
```
Error: Port 8501 is already in use
```

**Solutions**:

1. **Kill existing process**:

   **Windows**:
```bash
   netstat -ano | findstr :8501
   taskkill /PID <PID> /F
```

   **Linux/Mac**:
```bash
   lsof -ti:8501 | xargs kill -9
```

2. **Use different port**:
```bash
   streamlit run app.py --server.port=8502
```

3. **Update .env**:
```bash
   PORT=8502
```

---

### Issue: Configuration validation failed

**Symptoms**:
```
ValueError: Configuration errors: SECRET_KEY is required
```

**Solutions**:

1. **Create .env file**:
```bash
   cp .env.example .env
```

2. **Generate SECRET_KEY**:
```bash
   python -c "import secrets; print(secrets.token_hex(32))"
```

3. **Add to .env**:
```bash
   SECRET_KEY=your_generated_key_here
   ADMIN_PASSWORD=your_secure_password
```

---

### Issue: File permission error

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: 'user_data/users.json'
```

**Solutions**:

1. **Fix permissions** (Linux/Mac):
```bash
   chmod -R 755 user_data/
   chown -R $USER:$USER user_data/
```

2. **Run with sudo** (not recommended):
```bash
   sudo streamlit run app.py
```

3. **Check directory exists**:
```bash
   mkdir -p user_data/history user_data/api_keys
```

---

## Performance Issues

### Issue: Slow model loading

**Symptoms**:
- First query takes 10+ seconds
- "Loading model..." appears every time

**Solutions**:

1. **Enable model caching** (should be default):
```python
   @st.cache_resource
   def load_model():
       return pipeline('sentiment-analysis')
```

2. **Pre-download models**:
```bash
   python -c "from transformers import pipeline; pipeline('sentiment-analysis')"
```

3. **Check disk space**:
```bash
   df -h  # Ensure enough space for model cache
```

---

### Issue: High memory usage

**Symptoms**:
- Application uses >4GB RAM
- Out of memory errors

**Solutions**:

1. **Close unused models**:
   - Only load models when needed
   - Use lazy loading

2. **Increase system RAM**:
   - Minimum: 4GB
   - Recommended: 8GB

3. **Use lighter models** (future):
   - Distilled versions
   - Quantized models

---

### Issue: Slow queries

**Symptoms**:
- Single queries take >5s
- Batch processing very slow

**Solutions**:

1. **Check model caching**:
```python
   # Verify @st.cache_resource is used
```

2. **Use batch processing**:
```python
   # Process multiple at once
   results = model(texts)  # Not loop
```

3. **Monitor system resources**:
```bash
   # Check CPU/Memory
   top
   htop
```

---

## Docker Issues

### Issue: Docker build fails

**Symptoms**:
```
ERROR: failed to solve: process "/bin/sh -c pip install ..." did not complete
```

**Solutions**:

1. **Clear cache and rebuild**:
```bash
   docker build --no-cache -t textai-studio .
```

2. **Check Dockerfile syntax**:
```bash
   docker build --progress=plain -t textai-studio .
```

3. **Check disk space**:
```bash
   docker system df
   docker system prune  # Clean up
```

---

### Issue: Container won't start

**Symptoms**:
```
Container exits immediately
docker ps shows nothing
```

**Solutions**:

1. **Check logs**:
```bash
   docker logs textai-studio
   docker-compose logs -f
```

2. **Run interactively**:
```bash
   docker run -it --rm textai-studio /bin/bash
```

3. **Check configuration**:
```bash
   docker-compose config
```

---

### Issue: Container can't access internet

**Symptoms**:
- Models won't download
- Updates fail

**Solutions**:

1. **Check DNS**:
```bash
   docker run --rm textai-studio ping google.com
```

2. **Update DNS settings**:
```json
   // /etc/docker/daemon.json
   {
     "dns": ["8.8.8.8", "8.8.4.4"]
   }
```

3. **Restart Docker**:
```bash
   sudo systemctl restart docker
```

---

### Issue: Volume permission errors

**Symptoms**:
```
PermissionError: Permission denied: '/app/user_data'
```

**Solutions**:

1. **Fix host permissions** (Linux):
```bash
   sudo chown -R $(id -u):$(id -g) user_data/
```

2. **Use named volumes**:
```yaml
   volumes:
     - user_data:/app/user_data  # Named volume
```

3. **Check volume mounts**:
```bash
   docker volume ls
   docker volume inspect textai_user_data
```

---

## API Issues

### Issue: API key not working

**Symptoms**:
```json
{"error": "Invalid API key"}
```

**Solutions**:

1. **Verify key format**:
   - Should start with `sk_`
   - 40+ characters long

2. **Regenerate key**:
   - Log in to dashboard
   - Generate new API key
   - Update client code

3. **Check header format**:
```python
   headers = {"X-API-Key": "sk_..."}  # Correct
   # Not: "API-Key" or "api-key"
```

---

### Issue: Rate limit exceeded

**Symptoms**:
```json
{"error": "Rate limit exceeded", "code": "RATE_LIMIT_EXCEEDED"}
```

**Solutions**:

1. **Check current usage**:
   - Dashboard → API section
   - View remaining requests

2. **Wait for reset**:
   - Limits reset every hour
   - Check X-RateLimit-Reset header

3. **Upgrade tier**:
   - Guest: 10/hour
   - User: 100/hour
   - Pro: 1000/hour

---

### Issue: Timeout errors

**Symptoms**:
```python
requests.exceptions.ReadTimeout
```

**Solutions**:

1. **Increase timeout**:
```python
   response = requests.post(url, json=data, timeout=60)
```

2. **Use batch endpoint**:
```python
   # Faster for multiple texts
   results = client.batch_sentiment(texts)
```

3. **Check server load**:
```bash
   docker stats  # Monitor resources
```

---

## Data Issues

### Issue: Users can't log in

**Symptoms**:
- "Invalid username or password"
- But credentials are correct

**Solutions**:

1. **Check users.json**:
```bash
   cat user_data/users.json
   # Verify user exists
```

2. **Reset password**:
```python
   # Admin can reset in admin dashboard
```

3. **Check file permissions**:
```bash
   ls -la user_data/users.json
   chmod 644 user_data/users.json
```

---

### Issue: History not saving

**Symptoms**:
- Queries work but don't appear in history
- History page is empty

**Solutions**:

1. **Check directory exists**:
```bash
   ls -la user_data/history/
```

2. **Check permissions**:
```bash
   chmod -R 755 user_data/history/
```

3. **Verify HistoryManager**:
```python
   # Check add_entry() is called
```

---

### Issue: Data corruption

**Symptoms**:
```python
JSONDecodeError: Expecting value
```

**Solutions**:

1. **Backup and reset**:
```bash
   cp user_data/users.json user_data/users.json.bak
   echo '{}' > user_data/users.json
```

2. **Validate JSON**:
```bash
   python -m json.tool user_data/users.json
```

3. **Restore from backup**:
```bash
   cp backups/user_data_20241229.tar.gz .
   tar -xzf user_data_20241229.tar.gz
```

---

## Model Issues

### Issue: Models won't download

**Symptoms**:
- "Unable to load model"
- Download hangs or fails

**Solutions**:

1. **Check internet connection**:
```bash
   ping huggingface.co
```

2. **Set cache directory**:
```bash
   export HF_HOME=/path/to/cache
```

3. **Manual download**:
```python
   from transformers import pipeline
   model = pipeline('sentiment-analysis')
   # Models download automatically
```

4. **Use proxy** (if behind firewall):
```bash
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
```

---

### Issue: CUDA out of memory

**Symptoms**:
```
RuntimeError: CUDA out of memory
```

**Solutions**:

1. **Use CPU version**:
```python
   model = pipeline('sentiment-analysis', device=-1)
```

2. **Reduce batch size**:
```python
   # From 32 to 16
   results = model(texts[:16])
```

3. **Clear cache**:
```python
   import torch
   torch.cuda.empty_cache()
```

---

### Issue: Model inference error

**Symptoms**:
```python
IndexError: index out of range
ValueError: Input too long
```

**Solutions**:

1. **Truncate input**:
```python
   model(text[:512])  # Limit to 512 tokens
```

2. **Check input format**:
```python
   # Should be string, not list
   model("text")  # Correct
   model(["text"])  # May cause issues
```

3. **Update transformers**:
```bash
   pip install --upgrade transformers
```

---

## Debugging Tips

### 1. Enable Debug Mode
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG

# View detailed logs
tail -f logs/app.log
```

### 2. Check System Resources
```bash
# CPU and Memory
top
htop

# Disk space
df -h

# Docker stats
docker stats
```

### 3. Inspect Container
```bash
# Enter container
docker exec -it textai-studio bash

# Check files
ls -la /app/user_data

# Check processes
ps aux

# Check environment
env | grep APP
```

### 4. Test Components
```python
# Test model loading
from transformers import pipeline
model = pipeline('sentiment-analysis')
result = model("test")
print(result)

# Test authentication
from config import Config
Config.validate()
print("Config valid!")

# Test database
import json
with open('user_data/users.json') as f:
    users = json.load(f)
    print(f"{len(users)} users loaded")
```

---

## Getting Help

### Before Asking for Help

1. ✅ Check this troubleshooting guide
2. ✅ Review error messages
3. ✅ Check logs
4. ✅ Search existing issues
5. ✅ Try basic solutions

### When Asking for Help

Include:
- Error message (full text)
- Steps to reproduce
- Environment details (OS, Python version)
- Relevant logs
- What you've already tried

### Support Channels

- **Documentation**: See `/docs` directory
- **GitHub Issues**: Report bugs
- **Email**: support@textai.app

---

## FAQ

**Q: How do I reset admin password?**

A: Generate new password hash and update users.json:
```python
import bcrypt
password = "new_password"
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
# Update in users.json
```

**Q: Can I use PostgreSQL instead of JSON?**

A: Yes, but requires code changes. PostgreSQL recommended for >1000 users.

**Q: How do I backup my data?**

A:
```bash
tar -czf backup.tar.gz user_data/
```

**Q: Can I use GPU for inference?**

A: Yes, install torch-cuda version:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Q: How do I update the application?**

A:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
streamlit run app.py
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0
