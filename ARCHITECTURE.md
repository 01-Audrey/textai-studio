# System Architecture - TextAI Studio

Technical overview of TextAI Studio's architecture, components, and design decisions.

## System Overview

TextAI Studio is a monolithic web application built with Streamlit, featuring:
- Frontend UI (Streamlit components)
- Backend logic (Python)
- ML models (HuggingFace Transformers)
- Data storage (JSON files)

## Architecture Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                         User Browser                         │
│                     (HTTP/WebSocket)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Streamlit Server                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Frontend (UI Components)                 │  │
│  │  • Authentication Pages                               │  │
│  │  • Tool Interfaces (4 tools)                          │  │
│  │  • Batch Processing UI                                │  │
│  │  • Analytics Dashboard                                │  │
│  │  • Admin Dashboard                                    │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │           Backend (Business Logic)                    │  │
│  │  • UserManager (authentication)                       │  │
│  │  • HistoryManager (usage tracking)                    │  │
│  │  • APIKeyManager (API keys)                           │  │
│  │  • RateLimiter (rate limiting)                        │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │             ML Layer (NLP Models)                     │  │
│  │  • Sentiment Analysis (DistilBERT)                    │  │
│  │  • Summarization (BART)                               │  │
│  │  • Fake News Detection (BERT)                         │  │
│  │  • Job Matching (Sentence-BERT)                       │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │          Data Storage (JSON Files)                    │  │
│  │  • users.json (user accounts)                         │  │
│  │  • history/{user}.json (usage history)                │  │
│  │  • api_keys.json (API keys)                           │  │
│  │  • rate_limits.json (rate tracking)                   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend Layer

**Technology**: Streamlit components

**Responsibilities**:
- User interface rendering
- Input validation
- User interaction handling
- Data visualization (Plotly charts)

**Key Components**:
- `login_page()` - Authentication
- `sentiment_analysis_page()` - Sentiment tool
- `text_summarization_page()` - Summary tool
- `fake_news_detection_page()` - Fake news tool
- `job_matching_page()` - Job matcher tool
- `analytics_dashboard()` - User analytics
- `admin_dashboard()` - Admin monitoring

### 2. Backend Layer

**Technology**: Python classes and functions

**Responsibilities**:
- Business logic
- User management
- History tracking
- API authentication
- Rate limiting

**Key Classes**:
```python
class UserManager:
    - register_user()
    - authenticate_user()
    - get_user()
    - update_user()

class HistoryManager:
    - add_entry()
    - get_history()
    - get_analytics()
    - delete_history()

class APIKeyManager:
    - generate_key()
    - validate_key()
    - get_user_by_key()
    - revoke_key()

class RateLimiter:
    - check_limit()
    - increment_usage()
    - get_remaining()
    - reset_limits()
```

### 3. ML Layer

**Technology**: HuggingFace Transformers + PyTorch

**Responsibilities**:
- Model loading and caching
- Inference execution
- Batch processing
- Result formatting

**Models**:

| Tool | Model | Size | Task |
|------|-------|------|------|
| Sentiment | distilbert-base-uncased-finetuned-sst-2-english | 260MB | Classification |
| Summarizer | facebook/bart-large-cnn | 1.6GB | Seq2Seq |
| Fake News | bert-base-uncased | 420MB | Classification |
| Job Matcher | sentence-transformers/all-MiniLM-L6-v2 | 90MB | Embedding |

**Caching Strategy**:
```python
@st.cache_resource
def load_sentiment_model():
    return pipeline('sentiment-analysis')
```

### 4. Data Storage Layer

**Technology**: JSON files

**Structure**:
```
user_data/
├── users.json              # User accounts
├── history/
│   ├── user1.json         # User 1 history
│   └── user2.json         # User 2 history
├── api_keys/
│   └── api_keys.json      # API key mappings
└── rate_limits/
    └── rate_limits.json   # Rate limit tracking
```

**Why JSON?**:
- ✅ Simple, no DB setup needed
- ✅ Human-readable
- ✅ Easy backup
- ✅ Version control friendly
- ❌ Not scalable beyond ~1000 users
- ❌ No concurrent write safety

**Migration Path**: PostgreSQL for production scale

## Data Flow

### 1. User Query Flow
```
User Input → Streamlit UI → Backend Validation → Model Inference → Result Display
                ↓
           History Save → JSON File
                ↓
           Rate Limit Check → Update Counter
```

### 2. Authentication Flow
```
Login Form → UserManager.authenticate() → Bcrypt Verify → Session State
                                               ↓
                                          Load User Data
                                               ↓
                                         Redirect to App
```

### 3. Batch Processing Flow
```
CSV Upload → Parse CSV → Validate → Batch Inference (chunked)
                                           ↓
                                    Progress Updates
                                           ↓
                                    Results DataFrame
                                           ↓
                                    Download CSV
```

## Technology Stack

### Core Technologies
- **Python**: 3.10+
- **Streamlit**: 1.29.0 (web framework)
- **PyTorch**: 2.1.0 (ML backend)
- **Transformers**: 4.36.0 (NLP models)

### Supporting Libraries
- **pandas**: Data manipulation
- **plotly**: Interactive visualizations
- **bcrypt**: Password hashing
- **sentence-transformers**: Embeddings
- **python-dotenv**: Environment variables

### Infrastructure
- **Docker**: Containerization
- **Docker Compose**: Orchestration
- **Nginx**: Reverse proxy (optional)

## Design Decisions

### 1. Streamlit Framework

**Why Streamlit?**
- ✅ Rapid development
- ✅ Built-in components
- ✅ Python-only (no JS needed)
- ✅ Easy deployment
- ❌ Limited customization
- ❌ Single-page app constraints

**Alternative Considered**: FastAPI + React
- More flexible but requires frontend expertise

### 2. JSON Storage

**Why JSON?**
- ✅ Zero setup
- ✅ Perfect for prototype/MVP
- ✅ Easy debugging
- ❌ Not scalable
- ❌ No transactions

**Migration Strategy**: Switch to PostgreSQL when users > 1000

### 3. Monolithic Architecture

**Why Monolith?**
- ✅ Simpler deployment
- ✅ Easier development
- ✅ Lower latency (in-process)
- ❌ Harder to scale
- ❌ All-or-nothing updates

**When to Microservices?**
- When traffic > 10k requests/day
- When team > 5 developers
- When need independent scaling

### 4. Model Caching

**Strategy**: In-memory caching with @st.cache_resource

**Benefits**:
- 99%+ faster (6s → 10ms)
- Automatic cache invalidation
- Simple implementation

**Tradeoff**: High memory usage (~850MB for 4 models)

### 5. Rate Limiting

**Implementation**: In-memory counter with JSON persistence

**Tiers**:
- Guest: 10/hour
- User: 100/hour
- Pro: 1000/hour

**Why Not Redis?**
- Overkill for current scale
- JSON sufficient for <1000 users
- Easy to migrate later

## Scalability Considerations

### Current Limits
- **Users**: ~1000 (JSON storage limit)
- **Requests**: ~100 req/min (single instance)
- **Data**: ~1GB (filesystem storage)

### Scaling Path

#### Stage 1: Vertical Scaling (Current → 5k users)
- Increase server resources (4GB → 8GB RAM)
- Add Redis for rate limiting
- Optimize model loading

#### Stage 2: Horizontal Scaling (5k → 50k users)
- Load balancer + multiple instances
- PostgreSQL database
- Redis cache cluster
- Shared model storage (S3/NFS)

#### Stage 3: Microservices (50k+ users)
- Separate API service
- Dedicated model inference service
- Message queue (RabbitMQ/Kafka)
- Kubernetes orchestration

## Performance Optimizations

### Implemented
- ✅ Model caching (@st.cache_resource)
- ✅ Batch inference (5-10x faster)
- ✅ Lazy loading (history, data)
- ✅ File I/O caching (session state)
- ✅ Pandas vectorization

### Future Optimizations
- [ ] Model quantization (4-bit)
- [ ] GPU acceleration
- [ ] CDN for static assets
- [ ] Database query optimization
- [ ] Async processing (Celery)

## Security Architecture

### Authentication
- Bcrypt password hashing (cost factor: 12)
- Session-based authentication
- Secure session cookies

### API Security
- API key authentication (sk_ prefix)
- Rate limiting per user tier
- Input validation and sanitization

### Data Security
- Environment variables for secrets
- No secrets in code/git
- File permissions (user data)

### Future Enhancements
- [ ] JWT tokens
- [ ] OAuth2 integration
- [ ] 2FA support
- [ ] Audit logging
- [ ] RBAC (Role-Based Access Control)

## Monitoring & Observability

### Current
- Application logs (file-based)
- Health check endpoint
- Admin dashboard metrics

### Recommended
- [ ] Structured logging (JSON)
- [ ] Centralized logging (ELK stack)
- [ ] Metrics collection (Prometheus)
- [ ] Distributed tracing (Jaeger)
- [ ] Error tracking (Sentry)

## Disaster Recovery

### Backup Strategy
- Daily backups (user data, history)
- 30-day retention
- Off-site storage (S3)

### Recovery Time Objective (RTO)
- Target: < 1 hour

### Recovery Point Objective (RPO)
- Target: < 24 hours (daily backups)

## Testing Strategy

### Unit Tests
- Backend classes (UserManager, etc.)
- Utility functions
- Data validation

### Integration Tests
- API endpoints
- Database operations
- Model inference

### E2E Tests
- User workflows
- UI interactions
- Batch processing

### Load Tests
- Concurrent users
- Request throughput
- Memory stability

## Future Architecture

### Planned Improvements

1. **Database Migration**
```
   JSON Files → PostgreSQL
   - User data
   - History
   - API keys
```

2. **Caching Layer**
```
   Redis
   - Rate limiting
   - Session storage
   - Model results cache
```

3. **Message Queue**
```
   RabbitMQ/Celery
   - Async batch processing
   - Background tasks
   - Email notifications
```

4. **Microservices**
```
   API Gateway → Auth Service
               → Inference Service
               → Analytics Service
```

## Diagrams

### Current Architecture (v1.0)
```
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Streamlit  │
                    │   (8501)    │
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
    │  Models │      │  Backend  │    │   Data    │
    │ (Cache) │      │  (Logic)  │    │  (JSON)   │
    └─────────┘      └───────────┘    └───────────┘
```

### Target Architecture (v2.0)
```
                    ┌─────────────┐
                    │   Browser   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Load Balancer│
                    └──────┬──────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
    │ App 1   │      │  App 2    │    │  App 3    │
    └────┬────┘      └─────┬─────┘    └─────┬─────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
    ┌────▼────┐      ┌─────▼─────┐    ┌─────▼─────┐
    │PostgreSQL│      │   Redis   │    │    S3     │
    └─────────┘      └───────────┘    └───────────┘
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0
