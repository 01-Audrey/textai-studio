# API Documentation - TextAI Studio

Complete API reference for TextAI Studio.

## Overview

TextAI Studio provides a RESTful API for programmatic access to all NLP tools.

**Base URL**: `http://your-domain.com/api`

## Authentication

### API Key

All API requests require an API key in the header.
```http
X-API-Key: sk_your_api_key_here
```

### Get API Key

1. Sign up / log in to TextAI Studio
2. Navigate to Settings → API Keys
3. Click "Generate API Key"
4. Copy and save your key (shown only once)

### Example
```python
import requests

headers = {
    "X-API-Key": "sk_abc123...",
    "Content-Type": "application/json"
}

response = requests.post(
    "http://localhost:8501/api/sentiment",
    headers=headers,
    json={"text": "I love this!"}
)

print(response.json())
```

## Rate Limits

Rate limits based on user tier:

| Tier | Limit | Period |
|------|-------|--------|
| Guest | 10 | hour |
| User | 100 | hour |
| Pro | 1000 | hour |

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1672531200
```

## Endpoints

### 1. Sentiment Analysis

Analyze the emotional tone of text.

**Endpoint**: `POST /api/sentiment`

**Request**:
```json
{
  "text": "I absolutely love this product!"
}
```

**Response**:
```json
{
  "label": "POSITIVE",
  "score": 0.9998,
  "processing_time_ms": 145
}
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8501/api/sentiment",
    headers={"X-API-Key": "sk_..."},
    json={"text": "I love this!"}
)

data = response.json()
print(f"Sentiment: {data['label']} ({data['score']:.2%})")
```

**Example (cURL)**:
```bash
curl -X POST http://localhost:8501/api/sentiment \
  -H "X-API-Key: sk_..." \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this!"}'
```

---

### 2. Text Summarization

Generate concise summaries of text.

**Endpoint**: `POST /api/summarize`

**Request**:
```json
{
  "text": "Long article text here...",
  "max_length": 150,
  "min_length": 50
}
```

**Response**:
```json
{
  "summary": "Concise summary of the article...",
  "original_length": 1245,
  "summary_length": 98,
  "compression_ratio": 0.079,
  "processing_time_ms": 1234
}
```

**Parameters**:
- `text` (required): Text to summarize
- `max_length` (optional): Maximum summary length (default: 130)
- `min_length` (optional): Minimum summary length (default: 30)

**Example**:
```python
response = requests.post(
    "http://localhost:8501/api/summarize",
    headers={"X-API-Key": "sk_..."},
    json={
        "text": "Your long article...",
        "max_length": 100
    }
)

print(response.json()['summary'])
```

---

### 3. Fake News Detection

Detect potentially misleading content.

**Endpoint**: `POST /api/fake-news`

**Request**:
```json
{
  "text": "Article or claim to verify..."
}
```

**Response**:
```json
{
  "prediction": "FAKE",
  "confidence": 0.87,
  "analysis": {
    "fake_probability": 0.87,
    "real_probability": 0.13
  },
  "processing_time_ms": 234
}
```

**Example**:
```python
response = requests.post(
    "http://localhost:8501/api/fake-news",
    headers={"X-API-Key": "sk_..."},
    json={"text": "Breaking news claim..."}
)

data = response.json()
if data['prediction'] == 'FAKE':
    print(f"⚠️ Potentially fake ({data['confidence']:.1%})")
```

---

### 4. Job Matching

Match resumes to job descriptions.

**Endpoint**: `POST /api/job-match`

**Request**:
```json
{
  "resume": "Resume text...",
  "job_description": "Job description text..."
}
```

**Response**:
```json
{
  "match_score": 0.85,
  "match_percentage": 85.2,
  "recommendation": "Strong Match",
  "processing_time_ms": 123
}
```

**Match Score Scale**:
- 0.9 - 1.0: Excellent Match
- 0.8 - 0.9: Strong Match
- 0.7 - 0.8: Good Match
- 0.6 - 0.7: Fair Match
- < 0.6: Weak Match

**Example**:
```python
response = requests.post(
    "http://localhost:8501/api/job-match",
    headers={"X-API-Key": "sk_..."},
    json={
        "resume": "5 years Python developer...",
        "job_description": "Senior Python Engineer..."
    }
)

match = response.json()
print(f"Match: {match['recommendation']} ({match['match_percentage']:.1f}%)")
```

---

### 5. Batch Processing

Process multiple texts in a single request.

**Endpoint**: `POST /api/batch/{tool}`

**Tools**: `sentiment`, `summarize`, `fake-news`, `job-match`

**Request**:
```json
{
  "texts": [
    "First text to analyze",
    "Second text to analyze",
    "Third text to analyze"
  ]
}
```

**Response**:
```json
{
  "results": [
    {"text": "First text...", "label": "POSITIVE", "score": 0.99},
    {"text": "Second text...", "label": "NEGATIVE", "score": 0.87},
    {"text": "Third text...", "label": "POSITIVE", "score": 0.92}
  ],
  "total": 3,
  "successful": 3,
  "failed": 0,
  "processing_time_ms": 456
}
```

**Example**:
```python
response = requests.post(
    "http://localhost:8501/api/batch/sentiment",
    headers={"X-API-Key": "sk_..."},
    json={
        "texts": [
            "Great product!",
            "Terrible experience.",
            "It's okay, nothing special."
        ]
    }
)

for result in response.json()['results']:
    print(f"{result['text']}: {result['label']}")
```

---

## Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": "Additional information"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid API key |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Example Error Responses

**Missing API Key**:
```json
{
  "error": "API key required",
  "code": "MISSING_API_KEY"
}
```

**Invalid API Key**:
```json
{
  "error": "Invalid API key",
  "code": "INVALID_API_KEY"
}
```

**Rate Limit Exceeded**:
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": "Limit: 100/hour, Reset in: 2345 seconds"
}
```

**Invalid Input**:
```json
{
  "error": "Text is required",
  "code": "MISSING_PARAMETER",
  "details": "Parameter 'text' is required"
}
```

---

## Code Examples

### Python
```python
import requests

class TextAIClient:
    def __init__(self, api_key, base_url="http://localhost:8501/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def sentiment(self, text):
        response = requests.post(
            f"{self.base_url}/sentiment",
            headers=self.headers,
            json={"text": text}
        )
        return response.json()

    def summarize(self, text, max_length=130):
        response = requests.post(
            f"{self.base_url}/summarize",
            headers=self.headers,
            json={"text": text, "max_length": max_length}
        )
        return response.json()

    def fake_news(self, text):
        response = requests.post(
            f"{self.base_url}/fake-news",
            headers=self.headers,
            json={"text": text}
        )
        return response.json()

    def job_match(self, resume, job_description):
        response = requests.post(
            f"{self.base_url}/job-match",
            headers=self.headers,
            json={
                "resume": resume,
                "job_description": job_description
            }
        )
        return response.json()

# Usage
client = TextAIClient("sk_your_api_key")
result = client.sentiment("I love this!")
print(result)
```

### JavaScript
```javascript
const API_KEY = 'sk_your_api_key';
const BASE_URL = 'http://localhost:8501/api';

async function analyzeSentiment(text) {
    const response = await fetch(`${BASE_URL}/sentiment`, {
        method: 'POST',
        headers: {
            'X-API-Key': API_KEY,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text })
    });

    return await response.json();
}

// Usage
analyzeSentiment('I love this!')
    .then(result => console.log(result))
    .catch(error => console.error(error));
```

### cURL
```bash
# Sentiment Analysis
curl -X POST http://localhost:8501/api/sentiment \
  -H "X-API-Key: sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"text": "I love this!"}'

# Text Summarization
curl -X POST http://localhost:8501/api/summarize \
  -H "X-API-Key: sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"text": "Long text...", "max_length": 100}'

# Fake News Detection
curl -X POST http://localhost:8501/api/fake-news \
  -H "X-API-Key: sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"text": "News claim..."}'

# Job Matching
curl -X POST http://localhost:8501/api/job-match \
  -H "X-API-Key: sk_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"resume": "Resume...", "job_description": "Job..."}'
```

---

## Best Practices

### 1. Error Handling

Always handle errors gracefully:
```python
try:
    response = client.sentiment("Text")
    if response.get('error'):
        print(f"Error: {response['error']}")
    else:
        print(f"Result: {response['label']}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 2. Rate Limiting

Check rate limit headers:
```python
response = requests.post(url, headers=headers, json=data)
remaining = int(response.headers.get('X-RateLimit-Remaining', 0))

if remaining < 10:
    print(f"Warning: Only {remaining} requests remaining")
```

### 3. Batch Processing

Use batch endpoints for multiple texts:
```python
# Instead of multiple requests
for text in texts:
    result = client.sentiment(text)  # Slow!

# Use batch endpoint
results = client.batch_sentiment(texts)  # Fast!
```

### 4. Timeout Handling

Set appropriate timeouts:
```python
response = requests.post(
    url,
    headers=headers,
    json=data,
    timeout=30  # 30 seconds
)
```

---

## Changelog

### Version 1.0.0 (December 2024)
- Initial API release
- 4 NLP tools available
- Batch processing support
- Rate limiting implemented

---

**Last Updated**: December 2024  
**Version**: 1.0.0
