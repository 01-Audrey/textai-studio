# TextAI Studio

> Advanced NLP platform with 4 AI-powered tools for text analysis

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.29.0-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

TextAI Studio is a production-ready web application providing AI-powered text analysis tools:

- **Sentiment Analysis** - Analyze emotional tone of text
- **Text Summarization** - Generate concise summaries
- **Fake News Detection** - Identify potentially misleading content
- **Job Matching** - Match resumes to job descriptions

## Features

### Core Features
- 🤖 4 pre-trained NLP models (HuggingFace Transformers)
- 📊 Interactive visualizations (Plotly)
- 📁 Batch processing (CSV upload/download)
- 👤 User management (authentication, history)
- 🔑 API access with rate limiting
- 📈 Analytics dashboard
- 👑 Admin dashboard with monitoring

### Performance
- ⚡ Model caching (<10ms warm start)
- 🚀 Batch processing (50+ items/sec)
- 💾 Optimized data operations
- 📉 Low latency (<2s per query)

### Security
- 🔒 Bcrypt password hashing
- 🔐 Session-based authentication
- 🛡️ API key management
- ⚠️ Rate limiting (guest/user/pro tiers)

## Quick Start

### Using Docker (Recommended)
```bash
# 1. Clone repository
git clone https://github.com/yourusername/textai-studio.git
cd textai-studio/deployment

# 2. Configure environment
cp .env.example .env
nano .env  # Edit with your values

# 3. Start application
docker-compose up -d

# 4. Access application
# Open browser: http://localhost:8501
```

### Manual Installation
```bash
# 1. Install Python 3.10+
python --version  # Verify

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env

# 4. Run application
streamlit run textai_studio_app.py
```

## Documentation

- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Docker Guide](DOCKER_GUIDE.md) - Containerization
- [Setup Instructions](SETUP.md) - Initial configuration
- [API Documentation](API.md) - API reference
- [Architecture](ARCHITECTURE.md) - System design
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues

## Requirements

### System Requirements
- **OS**: Linux, macOS, Windows (with WSL2)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 5GB for models and data
- **Python**: 3.10 or higher

### Dependencies
- streamlit==1.29.0
- transformers==4.36.0
- torch==2.1.0
- sentence-transformers==2.2.2
- pandas==2.1.4
- plotly==5.18.0
- bcrypt==4.1.2

See [requirements.txt](requirements.txt) for complete list.

## Architecture
```
TextAI Studio
│
├── Frontend (Streamlit)
│   ├── Authentication
│   ├── Tool Interfaces
│   ├── Batch Processing
│   ├── Analytics Dashboard
│   └── Admin Dashboard
│
├── Backend (Python)
│   ├── NLP Models (HuggingFace)
│   ├── User Management
│   ├── History Tracking
│   ├── API System
│   └── Rate Limiting
│
└── Data Storage (JSON)
    ├── User Accounts
    ├── Usage History
    ├── API Keys
    └── Rate Limits
```

## API Access
```python
import requests

# Authenticate
response = requests.post(
    "http://localhost:8501/api/sentiment",
    headers={"X-API-Key": "your-api-key"},
    json={"text": "I love this product!"}
)

print(response.json())
# {"label": "POSITIVE", "score": 0.9998}
```

See [API.md](API.md) for complete API documentation.

## Development

### Local Development
```bash
# Install dev dependencies
pip install -r requirements.txt

# Run with hot reload
streamlit run textai_studio_app.py --server.runOnSave=true

# Run tests
pytest tests/
```

### Docker Development
```bash
# Start in dev mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Or using Makefile
make dev
```

## Project Structure
```
textai-studio/
├── deployment/              # Deployment files
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── .env.example
│   └── config.py
├── textai_studio_app.py    # Main application
├── user_data/              # User data (git-ignored)
│   ├── users.json
│   ├── history/
│   └── api_keys/
├── models/                 # Model cache (git-ignored)
└── logs/                   # Application logs
```

## Configuration

### Environment Variables

Key variables in `.env`:
```bash
# Security
SECRET_KEY=your-secret-key-here
ADMIN_PASSWORD=secure-admin-password

# Application
APP_ENV=production
DEBUG=false
PORT=8501

# Features
ENABLE_USER_SIGNUP=true
ENABLE_API_ACCESS=true
ENABLE_ANALYTICS=true
```

See [.env.example](.env.example) for all variables.

## Deployment Options

### Cloud Platforms

- **Streamlit Cloud** - Native deployment
- **Heroku** - Container deployment
- **AWS ECS** - Elastic Container Service
- **Google Cloud Run** - Serverless containers
- **Azure Container Instances** - Managed containers
- **DigitalOcean App Platform** - PaaS deployment

### Self-Hosted

- **Docker** - Containerized deployment
- **Kubernetes** - Orchestration at scale
- **VPS** - Traditional server deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for platform-specific guides.

## Monitoring

### Health Check
```bash
curl http://localhost:8501/_stcore/health
```

### Metrics

Access admin dashboard for:
- System health score
- User statistics
- Query volume
- Performance metrics
- Active alerts

## Security

### Best Practices

✅ Change default admin password  
✅ Use strong SECRET_KEY  
✅ Enable rate limiting  
✅ Keep dependencies updated  
✅ Use HTTPS in production  
✅ Regular backups  
✅ Monitor logs for suspicious activity  

### Security Checklist

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete security checklist.

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Performance

### Benchmarks

- Model loading: <10ms (cached)
- Single query: <2s (includes inference)
- Batch processing: 50-60 items/sec
- Memory usage: ~850MB (4 models loaded)
- Startup time: <5s (with cached models)

### Optimization

- ✅ Model caching (@st.cache_resource)
- ✅ Batch inference (5-10x faster)
- ✅ Lazy loading (history, data)
- ✅ File I/O caching (90% faster)
- ✅ Optimized DataFrames (vectorized ops)

## Troubleshooting

Common issues:

**Port already in use**
```bash
# Change port in .env or docker-compose.yml
PORT=8502
```

**Models not downloading**
```bash
# Pre-download models
python -c "from transformers import pipeline; pipeline('sentiment-analysis')"
```

**Memory issues**
```bash
# Increase Docker memory limit
# Docker Desktop -> Settings -> Resources -> Memory
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **HuggingFace** - Transformers library and models
- **Streamlit** - Web framework
- **PyTorch** - Deep learning backend
- **Plotly** - Interactive visualizations

## Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@textai.app

## Roadmap

### Version 1.1 (Q1 2025)
- [ ] PostgreSQL database integration
- [ ] Redis caching layer
- [ ] User profile customization
- [ ] Export to PDF/Word
- [ ] Multi-language support

### Version 1.2 (Q2 2025)
- [ ] Fine-tuning interface
- [ ] Custom model upload
- [ ] Team collaboration features
- [ ] Advanced analytics
- [ ] API v2 with webhooks

## Authors

**Audrey** - *ML Engineer & Developer*

## Version

Current version: **1.0.0** (December 2024)

---

Made with ❤️ by Audrey
