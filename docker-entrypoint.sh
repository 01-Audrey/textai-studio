#!/bin/bash
# ==================================================
# Docker Entrypoint - TextAI Studio
# ==================================================

set -e

echo "🚀 Starting TextAI Studio..."

# Create directories if they don't exist
mkdir -p /app/user_data/history
mkdir -p /app/user_data/uploads
mkdir -p /app/models
mkdir -p /app/logs

echo "✅ Directories ready"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Using default configuration"
fi

# Validate configuration
echo "🔍 Validating configuration..."
python -c "from config import Config; Config.validate()" || {
    echo "❌ Configuration validation failed"
    exit 1
}

echo "✅ Configuration valid"

# Download models if needed (optional)
# echo "📥 Checking models..."
# python -c "from transformers import pipeline; pipeline('sentiment-analysis')"

echo "✅ Ready to start application"

# Execute the main command
exec "$@"
