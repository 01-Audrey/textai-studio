# TextAI Studio

NLP text analysis platform with 4 AI-powered tools using HuggingFace Transformers. Features sentiment analysis, text summarization, fake news detection, and resume-job matching with user authentication, API system, and Docker deployment.

![Python](https://img.shields.io/badge/python-3.13-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.52.2-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-live-success.svg)

## 🚀 Live Demo

**Try it now:** https://textai-studio-app.streamlit.app/

Experience all 4 NLP tools without installation. Sign up for free to access analytics and API features.

## Features

### NLP Tools
- **Sentiment Analysis** - Emotional tone detection using DistilBERT achieving 95%+ accuracy
- **Text Summarization** - Concise summary generation with BART (up to 85% compression)
- **Fake News Detection** - Misinformation identification using RoBERTa-based classifier
- **Job Matching** - Resume-job similarity scoring with Sentence-BERT embeddings

### Platform Capabilities
- User authentication with bcrypt password hashing (cost factor 12)
- RESTful API with 3-tier rate limiting (guest: 10/h, user: 100/h, pro: 1000/h)
- Batch CSV processing supporting 50+ items/second
- Real-time analytics dashboard with usage insights
- Admin monitoring dashboard for system health
- Complete query history tracking

### Performance
- Model caching achieving <10ms warm start (500x improvement over cold start)
- Batch processing: 50+ items/second throughput
- Memory optimized: ~850MB with all 4 models loaded
- Response time: <2s average for single queries

## Tech Stack

**Framework & UI:**
- Streamlit 1.52.2 - Web application framework
- Plotly 6.5.0 - Interactive visualizations

**ML/NLP:**
- HuggingFace Transformers 4.57.3 - Pre-trained model integration
- PyTorch 2.9.1 - Deep learning backend
- Sentence-Transformers 5.2.0 - Semantic similarity

**Data Processing:**
- Pandas 2.3.3 - Data manipulation
- NumPy 2.4.0 - Numerical computing

**Security:**
- Bcrypt 5.0.0 - Password hashing
- Python-dotenv 1.2.1 - Environment management

**Deployment:**
- Docker & Docker Compose - Containerization
- Streamlit Cloud - Production hosting

## Installation

### Prerequisites
- Python 3.10+ (tested with 3.13)
- 4GB+ RAM recommended
- 5GB+ disk space for models

### Quick Start with Docker
```bash
# Clone repository
git clone https://github.com/01-Audrey/textai-studio.git
cd textai-studio

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start with Docker Compose
docker-compose up -d

# Access at http://localhost:8501
```

### Manual Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Generate SECRET_KEY:
python -c "import secrets; print(secrets.token_hex(32))"

# Run application
streamlit run textai_studio_app.py
```

## Configuration

Create `.env` file from `.env.example`:
```bash
# Security (Required)
SECRET_KEY=your-secret-key-here          # Generate with secrets.token_hex(32)
ADMIN_PASSWORD=your-secure-password      # Strong password (12+ chars)

# Application Settings
APP_ENV=production                       # production or development
DEBUG=false                              # Set to true for debugging
PORT=8501                                # Application port

# Feature Flags
ENABLE_USER_SIGNUP=true                  # Allow new user registration
ENABLE_API_ACCESS=true                   # Enable API endpoints
ENABLE_ANALYTICS=true                    # Track usage analytics
```

## Usage

### Web Interface

1. Navigate to https://textai-studio-app.streamlit.app/ or your local instance
2. Sign up for a free account or log in
3. Select a tool from the sidebar navigation
4. Enter text or upload CSV for batch processing
5. View results with interactive visualizations

### API Access

Generate an API key from the Settings page after login:
```python
import requests

headers = {"X-API-Key": "your-api-key"}

# Sentiment Analysis
response = requests.post(
    "http://localhost:8501/api/sentiment",
    headers=headers,
    json={"text": "I love this product!"}
)
print(response.json())
# Output: {"label": "POSITIVE", "score": 0.9998}

# Text Summarization
response = requests.post(
    "http://localhost:8501/api/summarize",
    headers=headers,
    json={
        "text": "Your long article text here...",
        "max_length": 130,
        "min_length": 30
    }
)
print(response.json()["summary"])

# Batch Processing
import pandas as pd

df = pd.read_csv("texts.csv")
results = []

for text in df["text_column"]:
    response = requests.post(
        "http://localhost:8501/api/sentiment",
        headers=headers,
        json={"text": text}
    )
    results.append(response.json())

pd.DataFrame(results).to_csv("results.csv", index=False)
```

See [API.md](API.md) for complete API documentation with all endpoints and parameters.

## Deployment

Multiple deployment options supported:

**Cloud Platforms:**
- ✅ **Streamlit Cloud** (recommended) - Currently deployed at production URL
- **AWS ECS** - Container orchestration with auto-scaling
- **Heroku** - Simple PaaS deployment
- **DigitalOcean App Platform** - Container-based hosting

**Self-Hosted:**
- **Docker** (recommended) - Consistent environment across platforms
- **Manual VPS** - Traditional server deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed platform-specific deployment guides.

## Documentation

- [Setup Guide](SETUP.md) - Initial configuration and installation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment for 6 platforms
- [Docker Guide](DOCKER_GUIDE.md) - Container deployment workflow
- [Architecture](ARCHITECTURE.md) - System design and technical architecture
- [API Reference](API.md) - Complete API documentation with examples
- [Security Guide](SECURITY.md) - Security best practices and hardening
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Project Structure
```
textai-studio/
├── textai_studio_app.py          # Main application
├── config.py                     # Configuration loader
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── Dockerfile                    # Docker configuration
├── docker-compose.yml            # Docker orchestration
├── .streamlit/
│   └── config.toml              # Streamlit settings
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── ...
└── .github/
    ├── ISSUE_TEMPLATE/          # Issue templates
    └── PULL_REQUEST_TEMPLATE.md
```

## Security

**Authentication:**
- Bcrypt password hashing with cost factor 12
- Session management with 30-minute timeout
- API key authentication with SHA-256 hashing

**Rate Limiting:**
- Guest tier: 10 requests/hour
- User tier: 100 requests/hour
- Pro tier: 1000 requests/hour

**Data Protection:**
- Input validation and sanitization
- Environment variable configuration
- HTTPS/TLS encryption in production
- Secure file permissions (700/600)

See [SECURITY.md](SECURITY.md) for comprehensive security documentation.

## Performance Benchmarks

| Metric | Value | Target |
|--------|-------|--------|
| Model Loading (warm) | <10ms | <50ms ✅ |
| Single Query | <2s | <3s ✅ |
| Batch Processing | 50+ items/sec | 40+ items/sec ✅ |
| Memory Usage | ~850MB | <1GB ✅ |
| Cache Hit Rate | 90%+ | 80%+ ✅ |

## Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Audrey** - [GitHub](https://github.com/01-Audrey)

CS Student | ML/Computer Vision 

## Acknowledgments

- [HuggingFace](https://huggingface.co/) - Transformers library and pre-trained models
- [Streamlit](https://streamlit.io/) - Web application framework
- [PyTorch](https://pytorch.org/) - Deep learning backend
- [Sentence-Transformers](https://www.sbert.net/) - Semantic similarity models

---

**Built with ❤️ for production NLP applications**
