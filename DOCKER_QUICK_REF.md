# Docker Quick Reference

## Essential Commands

### Build & Start
```bash
docker-compose up -d           # Start in background
docker-compose up              # Start with logs
make up                        # Using Makefile
```

### Stop & Remove
```bash
docker-compose down            # Stop containers
docker-compose down -v         # Stop and remove volumes
make down                      # Using Makefile
```

### View Logs
```bash
docker-compose logs -f         # Follow logs
docker-compose logs --tail=50  # Last 50 lines
make logs                      # Using Makefile
```

### Access Shell
```bash
docker-compose exec app bash   # Open shell
make shell                     # Using Makefile
```

### Rebuild
```bash
docker-compose build           # Rebuild image
docker-compose build --no-cache # Force rebuild
make build                     # Using Makefile
```

### Status
```bash
docker-compose ps              # Container status
docker stats                   # Resource usage
make status                    # Using Makefile
```

## Troubleshooting

### View Errors
```bash
docker-compose logs app        # App logs
docker inspect textai-studio   # Container details
```

### Restart Services
```bash
docker-compose restart         # Restart all
docker-compose restart app     # Restart app only
make restart                   # Using Makefile
```

### Clean Up
```bash
docker system prune           # Remove unused
docker volume prune           # Remove unused volumes
make clean                    # Clean everything
```

## URLs

- Application: http://localhost:8501
- Health Check: http://localhost:8501/_stcore/health
