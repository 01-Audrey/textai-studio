# ==================================================
# Makefile - TextAI Studio Docker Commands
# ==================================================

.PHONY: help build up down logs shell clean

help:
	@echo "TextAI Studio - Docker Commands"
	@echo "================================"
	@echo "make build    - Build Docker image"
	@echo "make up       - Start containers"
	@echo "make down     - Stop containers"
	@echo "make logs     - View logs"
	@echo "make shell    - Open shell in container"
	@echo "make clean    - Remove containers and volumes"
	@echo "make dev      - Start in development mode"

build:
	@echo "🔨 Building Docker image..."
	docker-compose build

up:
	@echo "🚀 Starting containers..."
	docker-compose up -d
	@echo "✅ Application running at http://localhost:8501"

down:
	@echo "🛑 Stopping containers..."
	docker-compose down

logs:
	@echo "📋 Viewing logs (Ctrl+C to exit)..."
	docker-compose logs -f

shell:
	@echo "🐚 Opening shell in app container..."
	docker-compose exec app /bin/bash

clean:
	@echo "🧹 Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "✅ Cleanup complete"

dev:
	@echo "🔧 Starting in development mode..."
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

restart:
	@echo "🔄 Restarting containers..."
	docker-compose restart

status:
	@echo "📊 Container status:"
	docker-compose ps
