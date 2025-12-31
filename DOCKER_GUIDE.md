# ==================================================
# Docker Build & Testing Guide
# ==================================================

## Prerequisites

1. **Install Docker**
   - Windows/Mac: Docker Desktop
   - Linux: Docker Engine
   - Verify: `docker --version`

2. **Install Docker Compose**
   - Included with Docker Desktop
   - Linux: Install separately
   - Verify: `docker-compose --version`

## Build Process

### Method 1: Docker (Simple)
```bash
# 1. Navigate to deployment directory
cd deployment/

# 2. Build the image
docker build -t textai-studio .

# 3. Run the container
docker run -d \
  -p 8501:8501 \
  --name textai-studio \
  -v $(pwd)/user_data:/app/user_data \
  -v $(pwd)/models:/app/models \
  textai-studio

# 4. Check logs
docker logs -f textai-studio

# 5. Access application
# Open browser: http://localhost:8501

# 6. Stop container
docker stop textai-studio

# 7. Remove container
docker rm textai-studio
```

### Method 2: Docker Compose (Recommended)
```bash
# 1. Navigate to deployment directory
cd deployment/

# 2. Create .env file
cp .env.example .env
# Edit .env with your values

# 3. Build and start
docker-compose up -d

# 4. View logs
docker-compose logs -f

# 5. Access application
# Open browser: http://localhost:8501

# 6. Stop services
docker-compose down

# 7. Clean up (including volumes)
docker-compose down -v
```

### Method 3: Using Makefile (Easiest)
```bash
# Build
make build

# Start
make up

# View logs
make logs

# Stop
make down

# Clean everything
make clean
```

## Testing Checklist

### 1. Build Testing
- [ ] Image builds without errors
- [ ] Build completes in reasonable time
- [ ] Image size is acceptable (<2GB)
```bash
# Check image size
docker images textai-studio
```

### 2. Runtime Testing
- [ ] Container starts successfully
- [ ] Application accessible on port 8501
- [ ] Health check passes
- [ ] No errors in logs
```bash
# Check container health
docker inspect --format='{{.State.Health.Status}}' textai-studio

# View logs
docker logs textai-studio
```

### 3. Functionality Testing
- [ ] Web interface loads
- [ ] User can login/signup
- [ ] All 4 tools work
- [ ] File upload works
- [ ] Batch processing works
- [ ] Analytics displays
- [ ] Admin dashboard accessible

### 4. Persistence Testing
- [ ] Data survives container restart
- [ ] User accounts persist
- [ ] History saved correctly
- [ ] Models cached properly
```bash
# Restart container
docker-compose restart

# Verify data persists
docker-compose exec app ls -la /app/user_data
```

### 5. Performance Testing
- [ ] Models load efficiently
- [ ] Queries processed quickly
- [ ] No memory leaks
- [ ] CPU usage reasonable
```bash
# Monitor resources
docker stats textai-studio
```

## Troubleshooting

### Build Fails
```bash
# Clear cache and rebuild
docker build --no-cache -t textai-studio .

# Check Dockerfile syntax
docker build --progress=plain -t textai-studio .
```

### Port Already in Use
```bash
# Find process using port 8501
# Windows
netstat -ano | findstr :8501

# Linux/Mac
lsof -i :8501

# Use different port
docker run -p 8502:8501 textai-studio
```

### Container Won't Start
```bash
# Check logs
docker logs textai-studio

# Run interactively to see errors
docker run -it --rm textai-studio /bin/bash

# Check configuration
docker-compose config
```

### Volume Permission Issues
```bash
# Fix permissions (Linux)
sudo chown -R $(id -u):$(id -g) user_data/ models/

# Run as root (not recommended)
docker run --user root textai-studio
```

### Models Not Downloading
```bash
# Check network
docker run --rm textai-studio ping google.com

# Pre-download models
docker-compose exec app python -c "from transformers import pipeline; pipeline('sentiment-analysis')"
```

### Memory Issues
```bash
# Check memory usage
docker stats

# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory

# Clean up unused resources
docker system prune -a
```

## Development Workflow

### Live Reload (Development)
```bash
# Start in dev mode
make dev

# Or manually
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Access Container Shell
```bash
# Using docker-compose
docker-compose exec app bash

# Using docker
docker exec -it textai-studio bash

# Using make
make shell
```

### Update Dependencies
```bash
# Update requirements.txt
# Then rebuild
docker-compose build --no-cache
docker-compose up -d
```

## Production Deployment

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Environment variables set
- [ ] Secrets configured
- [ ] Volumes backed up
- [ ] Health checks working
- [ ] Logs configured
- [ ] Monitoring setup

### Deploy to Server
```bash
# 1. Copy files to server
scp -r deployment/ user@server:/opt/textai-studio/

# 2. SSH to server
ssh user@server

# 3. Navigate to directory
cd /opt/textai-studio/deployment/

# 4. Configure environment
cp .env.example .env
nano .env

# 5. Start services
docker-compose up -d

# 6. Verify deployment
docker-compose ps
docker-compose logs -f
```

## Maintenance

### Backup Data
```bash
# Backup volumes
docker run --rm \
  -v textai_user_data:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/user_data_backup.tar.gz /data

# Backup database (if using)
docker-compose exec db pg_dump -U textai_user textai_db > backup.sql
```

### Update Application
```bash
# 1. Pull latest code
git pull origin main

# 2. Rebuild image
docker-compose build

# 3. Restart services
docker-compose up -d

# 4. Verify
docker-compose logs -f
```

### Monitor Logs
```bash
# Real-time logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs -f app

# Save logs to file
docker-compose logs > logs.txt
```

## Performance Optimization

### Image Size Optimization
- Use slim base images
- Multi-stage builds
- Remove unnecessary files
- Minimize layers

### Runtime Optimization
- Limit container resources
- Use volume caching
- Enable buildkit
- Optimize dependencies
```bash
# Build with buildkit
DOCKER_BUILDKIT=1 docker build -t textai-studio .

# Limit resources
docker run \
  --memory="2g" \
  --cpus="2" \
  textai-studio
```

## Next Steps

1. Complete all testing
2. Document any issues
3. Prepare deployment documentation
4. Set up monitoring
5. Plan backup strategy
6. Configure auto-scaling (if needed)
