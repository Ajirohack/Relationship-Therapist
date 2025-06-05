# Relationship Therapist AI System

A comprehensive AI-powered relationship therapy system that analyzes conversation history, provides real-time recommendations, and offers therapeutic insights to help users improve their relationships.

## 🌟 Features

### Core Capabilities

- **Multi-format Input Processing**: Supports screenshots, text files, PDFs, audio files, zipped archives, and folders
- **Real-time Social Media Monitoring**: Live conversation analysis and recommendations
- **Comprehensive Analysis**: Communication patterns, emotional intelligence, compatibility assessment
- **Therapeutic Interventions**: AI-powered coaching and guidance
- **Progress Tracking**: Detailed reports and visualizations
- **Knowledge Base Integration**: Custom therapeutic guidance and metrics

### Analysis Types

- **Communication Analysis**: Style assessment, effectiveness metrics, pattern recognition
- **Emotional Intelligence**: Sentiment analysis, emotion classification, empathy scoring
- **Relationship Health**: Compatibility assessment, conflict resolution patterns
- **Progress Monitoring**: Goal tracking, improvement metrics, milestone analysis

### Report Generation

- **Multiple Formats**: PDF, HTML, JSON, Interactive dashboards
- **Comprehensive Visualizations**: Charts, graphs, timelines, matrices
- **Actionable Insights**: Personalized recommendations and intervention strategies
- **Progress Tracking**: Historical analysis and trend identification

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI       │    │  AI Therapist   │    │ Report Generator│
│   Main App      │◄──►│     Core         │◄──►│    Module       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Data Processor  │    │ Conversation     │    │ Knowledge Base  │
│    Module       │    │   Analyzer       │    │    Manager      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Real-time       │    │   MCP Server     │    │   Database      │
│   Monitor       │    │  Integration     │    │   Storage       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Minimal Fallback System

The system includes a robust minimal fallback implementation that operates without external AI dependencies:

```
┌─────────────────┐    ┌────────────────────────┐    ┌─────────────────┐
│   AI Service    │    │  MinimalAITherapist    │    │ Pure Python     │
│   Fallback      │◄──►│       Core             │◄──►│ Implementations │
└─────────────────┘    └────────────────────────┘    └─────────────────┘
         │                        │                           │
         ▼                        ▼                           ▼
┌─────────────────┐    ┌────────────────────────┐    ┌─────────────────┐
│ VADER Sentiment │    │ MinimalConversation    │    │ Rule-based      │
│    Analysis     │    │      Analyzer          │    │ Pattern Matching│
└─────────────────┘    └────────────────────────┘    └─────────────────┘
```

**Key Fallback Features:**

- Pure Python implementations of NumPy functions
- VADER-based sentiment analysis
- Rule-based pattern matching for conflict detection
- Emotional intensity analysis
- Topic detection and categorization
- Specialized recommendation generation based on detected patterns
- No external ML dependencies required

### Key Modules

1. **main.py**: FastAPI application with REST endpoints
2. **ai_therapist.py**: Core AI intelligence and therapeutic logic
3. **conversation_analyzer.py**: NLP analysis and pattern recognition
4. **data_processor.py**: Multi-format input processing
5. **real_time_monitor.py**: Live social media monitoring
6. **knowledge_base.py**: Document management and retrieval
7. **mcp_server.py**: Model Context Protocol integration
8. **report_generator.py**: Comprehensive report creation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Optional: GPU for faster AI processing
- Optional: Redis for caching
- Optional: PostgreSQL for production database

### Installation

1. **Clone the repository**:

   ```bash
   cd /Users/macbook/Downloads/space-bot/relationship_therapist_system
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Download required models**:

   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('vader_lexicon'); nltk.download('punkt')"
   ```

5. **Set up environment variables**:

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Initialize the database** (optional):

   ```bash
   python -c "from main import init_db; init_db()"
   ```

### Running the Application

1. **Start the server**:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the API**:
   - API Documentation: <http://localhost:8000/docs>
   - Interactive API: <http://localhost:8000/redoc>
   - Health Check: <http://localhost:8000/health>

## 📚 API Documentation

### Core Endpoints

#### Upload and Analysis

```http
POST /api/v1/upload/conversation
Content-Type: multipart/form-data

# Upload conversation files for analysis
```

#### Real-time Recommendations

```http
GET /api/v1/recommendations/realtime/{user_id}

# Get real-time conversation recommendations
```

#### User Profile Management

```http
GET /api/v1/users/{user_id}/profile
PUT /api/v1/users/{user_id}/profile

# Manage user therapy profiles
```

#### Report Generation

```http
POST /api/v1/reports/generate
Content-Type: application/json

{
  "user_id": "string",
  "report_type": "relationship_health",
  "format": "pdf",
  "time_period": "last_month"
}
```

#### Knowledge Base

```http
POST /api/v1/knowledge/upload
GET /api/v1/knowledge/search

# Upload and search therapeutic documents
```

### WebSocket Endpoints

#### Real-time Monitoring

```javascript
// Connect to real-time monitoring
const ws = new WebSocket('ws://localhost:8000/ws/monitor/{user_id}');

// Send live conversation data
ws.send(JSON.stringify({
  "type": "conversation_update",
  "content": "conversation text",
  "platform": "whatsapp",
  "timestamp": "2024-01-01T12:00:00Z"
}));
```

#### MCP Integration

```javascript
// Connect to MCP server
const mcp = new WebSocket('ws://localhost:8000/mcp');

// Send MCP messages
mcp.send(JSON.stringify({
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "analyze_conversation",
    "arguments": {
      "text": "conversation content",
      "user_id": "user123"
    }
  },
  "id": 1
}));
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Application Settings
APP_NAME=Relationship Therapist AI
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# Server Configuration
HOST=0.0.0.0
PORT=8000
WORKERS=4

# Database Configuration
DATABASE_URL=sqlite:///./relationship_therapist.db
# DATABASE_URL=postgresql://user:password@localhost/relationship_therapist

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379/0

# AI Model Configuration
HUGGINGFACE_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here  # Optional

# Social Media API Keys (optional)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_token_secret

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
UPLOAD_DIR=./uploads
REPORT_DIR=./reports
MAX_FILE_SIZE=100MB

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
```

### Model Configuration

The system uses several AI models that can be configured:

```python
# In ai_therapist.py
MODEL_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "emotion_model": "j-hartmann/emotion-english-distilroberta-base",
    "sentiment_model": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "personality_model": "Minej/bert-base-personality"
}
```

## 📊 Usage Examples

### 1. Analyzing Conversation History

```python
import requests
import json

# Upload conversation file
with open('conversation.txt', 'rb') as f:
    files = {'file': f}
    data = {'user_id': 'user123', 'analysis_type': 'comprehensive'}
    response = requests.post(
        'http://localhost:8000/api/v1/upload/conversation',
        files=files,
        data=data
    )

analysis_result = response.json()
print(json.dumps(analysis_result, indent=2))
```

### 2. Getting Real-time Recommendations

```python
import asyncio
import websockets
import json

async def get_realtime_recommendations():
    uri = "ws://localhost:8000/ws/monitor/user123"
    async with websockets.connect(uri) as websocket:
        # Send conversation update
        message = {
            "type": "conversation_update",
            "content": "I'm feeling frustrated with our communication",
            "platform": "whatsapp",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        await websocket.send(json.dumps(message))
        
        # Receive recommendation
        recommendation = await websocket.recv()
        print(json.dumps(json.loads(recommendation), indent=2))

asyncio.run(get_realtime_recommendations())
```

### 3. Generating Reports

```python
import requests

# Generate relationship health report
report_request = {
    "user_id": "user123",
    "report_type": "relationship_health",
    "format": "pdf",
    "time_period": "last_month"
}

response = requests.post(
    'http://localhost:8000/api/v1/reports/generate',
    json=report_request
)

report_info = response.json()
print(f"Report generated: {report_info['report_path']}")
```

### 4. Managing Knowledge Base

```python
import requests

# Upload therapeutic guidance document
with open('therapy_guidelines.pdf', 'rb') as f:
    files = {'file': f}
    data = {
        'document_type': 'guidance',
        'title': 'Communication Therapy Guidelines',
        'description': 'Best practices for communication therapy'
    }
    response = requests.post(
        'http://localhost:8000/api/v1/knowledge/upload',
        files=files,
        data=data
    )

# Search knowledge base
search_response = requests.get(
    'http://localhost:8000/api/v1/knowledge/search',
    params={'query': 'conflict resolution techniques', 'limit': 5}
)

search_results = search_response.json()
for result in search_results['results']:
    print(f"- {result['title']}: {result['relevance_score']:.2f}")
```

## 🔍 Monitoring and Debugging

### Health Checks

```bash
# Check application health
curl http://localhost:8000/health

# Check detailed system status
curl http://localhost:8000/api/v1/system/status
```

### Metrics

The system exposes Prometheus metrics on port 9090:

```bash
# View metrics
curl http://localhost:9090/metrics
```

### Logging

Logs are structured and can be configured via environment variables:

```python
# View logs in real-time
tail -f logs/relationship_therapist.log

# Filter by log level
grep "ERROR" logs/relationship_therapist.log
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_conversation_analyzer.py

# Run integration tests
pytest tests/integration/
```

### Test Data

Sample test data is provided in the `tests/data/` directory:

- `sample_conversations.json`: Example conversation data
- `test_audio.wav`: Sample audio file
- `test_image.png`: Sample screenshot
- `test_document.pdf`: Sample PDF document

## 🚀 Deployment

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t relationship-therapist .
docker run -p 8000:8000 relationship-therapist
```

### Production Deployment

```bash
# Using gunicorn for production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With nginx reverse proxy
# Configure nginx to proxy to localhost:8000
```

## 🔒 Security Considerations

### Data Privacy

- All conversation data is encrypted at rest
- Personal information is anonymized in logs
- GDPR compliance features included
- User data retention policies configurable

### API Security

- JWT token authentication
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS configuration for web clients

### File Upload Security

- File type validation
- Size limits enforced
- Virus scanning integration points
- Secure file storage with access controls

## 🤝 Contributing

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Run code formatting
black .
flake8 .
mypy .
```

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 80%

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation

- API Documentation: <http://localhost:8000/docs>
- Technical Documentation: [docs/](docs/)
- FAQ: [docs/FAQ.md](docs/FAQ.md)

### Getting Help

- GitHub Issues: Report bugs and request features
- Discussions: Community support and questions
- Email: <support@relationship-therapist-ai.com>

### Troubleshooting

Common issues and solutions:

1. **Model Download Errors**:

   ```bash
   # Manually download models
   python -c "from transformers import AutoModel; AutoModel.from_pretrained('all-MiniLM-L6-v2')"
   ```

2. **Memory Issues**:
   - Reduce batch sizes in configuration
   - Use CPU-only mode for development
   - Increase system memory allocation

3. **Database Connection Issues**:
   - Check database URL in environment variables
   - Ensure database server is running
   - Verify connection permissions

## 🔮 Roadmap

### Upcoming Features

- [ ] Multi-language support
- [ ] Voice conversation analysis
- [ ] Mobile app integration
- [ ] Advanced ML models
- [ ] Couples therapy mode
- [ ] Integration with therapy platforms

### Version History

- **v1.0.0**: Initial release with core features
- **v1.1.0**: Real-time monitoring and MCP integration
- **v1.2.0**: Advanced report generation
- **v2.0.0**: Multi-language and voice support (planned)

---

**Built with ❤️ for better relationships**
