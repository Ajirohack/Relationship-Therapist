# AI Brain Package - 7-Layer Architecture for Relationship Therapy

A sophisticated 7-layer AI brain architecture designed specifically for relationship therapy applications, embodying the Diego Camilleri persona as a warm, empathetic, and professional relationship therapist.

## 🧠 Architecture Overview

The AI Brain implements a hierarchical 7-layer architecture inspired by cognitive science and neuroscience principles:

```
┌─────────────────────────────────────────────────────────────┐
│                    7. Selfhood & Awareness                 │
│              Self-reflection, Learning, Meta-cognition     │
├─────────────────────────────────────────────────────────────┤
│                    6. Toolbox & Motor                      │
│           Response Generation, Communication Tools         │
├─────────────────────────────────────────────────────────────┤
│                    5. Decision & Action                    │
│          Strategic Decision-making, Action Planning        │
├─────────────────────────────────────────────────────────────┤
│                4. Emotional & Psychological                │
│        Emotional Intelligence, Therapeutic Modeling       │
├─────────────────────────────────────────────────────────────┤
│                3. Understanding & Reasoning                │
│         Pattern Recognition, Logical Analysis, Insights    │
├─────────────────────────────────────────────────────────────┤
│                      2. Memory                             │
│        Session Data, User Profiles, Knowledge Retrieval   │
├─────────────────────────────────────────────────────────────┤
│                    1. Perception                           │
│           Input Processing, Sensory Analysis               │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Key Features

### Core Capabilities
- **Multi-layer Processing**: Sequential or parallel processing through 7 specialized layers
- **Diego Persona Integration**: Consistent warm, empathetic, professional therapeutic presence
- **Safety-First Design**: Built-in crisis detection and safety protocols
- **Adaptive Learning**: Continuous improvement through self-reflection and meta-cognition
- **Session Management**: Persistent user profiles and conversation context
- **Performance Monitoring**: Real-time metrics and quality assessment

### Therapeutic Features
- **Emotional Intelligence**: Advanced emotion detection and empathetic responses
- **Pattern Recognition**: Identification of relationship dynamics and communication patterns
- **Therapeutic Interventions**: Evidence-based technique recommendations
- **Crisis Management**: Automatic detection and appropriate response protocols
- **Homework & Resources**: Personalized assignments and resource recommendations
- **Progress Tracking**: Stage-based relationship therapy progression monitoring

## 🚀 Quick Start

### Installation

1. **Install Dependencies**:
   ```bash
   pip install -r ai_brain/requirements.txt
   ```

2. **Basic Setup**:
   ```python
   from ai_brain import initialize_ai_brain_integration, get_default_config
   
   # Initialize with default configuration
   config = get_default_config()
   ai_brain = initialize_ai_brain_integration(config)
   ```

3. **FastAPI Integration**:
   ```python
   from fastapi import FastAPI, BackgroundTasks
   from ai_brain import create_ai_brain_routes, initialize_ai_brain_integration
   
   app = FastAPI()
   
   # Initialize AI brain
   config = get_default_config()
   ai_brain = initialize_ai_brain_integration(config)
   
   # Add AI brain routes
   ai_routes = create_ai_brain_routes(ai_brain)
   app.include_router(ai_routes, prefix="/ai", tags=["AI Brain"])
   ```

### Basic Usage

```python
from ai_brain import AIBrainIntegration, UserInputRequest
from fastapi import BackgroundTasks

# Create user request
user_request = UserInputRequest(
    user_id="user123",
    session_id="session456",
    message="I'm having trouble communicating with my partner",
    message_type="text"
)

# Process through AI brain
background_tasks = BackgroundTasks()
response = await ai_brain.process_user_message(user_request, background_tasks)

print(f"Diego: {response.message}")
print(f"Confidence: {response.confidence}")
print(f"Emotional Tone: {response.emotional_tone}")
```

## 📋 Layer Details

### 1. Perception Layer
**Purpose**: Input processing and initial analysis

**Capabilities**:
- Input type detection (text, voice, etc.)
- Sentiment analysis
- Emotion detection
- Urgency assessment
- Context extraction

**Key Methods**:
- `process()`: Main processing pipeline
- `analyze_sentiment()`: Emotional tone analysis
- `detect_emotions()`: Specific emotion identification
- `assess_urgency()`: Crisis/urgency detection

### 2. Memory Layer
**Purpose**: Data persistence and knowledge management

**Capabilities**:
- User profile management
- Conversation history
- Session context tracking
- Knowledge base integration
- Diego persona loading

**Key Methods**:
- `get_user_profile()`: Retrieve/create user profiles
- `store_short_term_memory()`: Session data storage
- `retrieve_relevant_memories()`: Context-aware retrieval
- `update_conversation_context()`: Dynamic context updates

### 3. Understanding & Reasoning Layer
**Purpose**: Pattern recognition and logical analysis

**Capabilities**:
- Communication pattern analysis
- Relationship stage assessment
- Insight generation
- Reasoning chain construction
- Quality assessment

**Key Methods**:
- `analyze_patterns()`: Multi-dimensional pattern analysis
- `generate_insights()`: Therapeutic insights
- `build_reasoning_chain()`: Logical reasoning
- `analyze_stage_progression()`: Relationship stage tracking

### 4. Emotional & Psychological Layer
**Purpose**: Emotional intelligence and therapeutic modeling

**Capabilities**:
- Emotional profile analysis
- Psychological assessment
- Empathetic response generation
- Therapeutic intervention recommendations
- Safety assessment

**Key Methods**:
- `analyze_emotional_profile()`: Comprehensive emotional analysis
- `generate_emotional_response()`: Empathetic responses
- `recommend_interventions()`: Therapeutic techniques
- `assess_emotional_safety()`: Safety evaluation

### 5. Decision & Action Layer
**Purpose**: Strategic decision-making and planning

**Capabilities**:
- Risk assessment
- Strategic decision-making
- Action plan development
- Response strategy optimization
- Safety protocol activation

**Key Methods**:
- `conduct_risk_assessment()`: Comprehensive risk analysis
- `make_strategic_decisions()`: Multi-factor decision-making
- `develop_action_plan()`: Structured planning
- `optimize_for_diego()`: Persona consistency

### 6. Toolbox & Motor Layer
**Purpose**: Response generation and communication

**Capabilities**:
- Response generation
- Communication tool selection
- Homework assignment creation
- Resource recommendations
- Crisis protocol preparation

**Key Methods**:
- `generate_response()`: Primary response creation
- `create_follow_up_questions()`: Engagement enhancement
- `generate_homework()`: Personalized assignments
- `prepare_crisis_protocol()`: Emergency procedures

### 7. Selfhood & Awareness Layer
**Purpose**: Self-reflection and continuous improvement

**Capabilities**:
- Performance analysis
- Learning insight generation
- Meta-cognitive analysis
- System optimization
- Historical data updates

**Key Methods**:
- `conduct_self_reflection()`: Performance evaluation
- `generate_learning_insights()`: Improvement identification
- `perform_meta_cognitive_analysis()`: System awareness
- `identify_optimizations()`: Enhancement opportunities

## ⚙️ Configuration

### Default Configuration

```python
from ai_brain import get_default_config

config = get_default_config()
# Returns comprehensive configuration with all layer settings
```

### Minimal Configuration

```python
from ai_brain import create_minimal_config

config = create_minimal_config(processing_mode="sequential")
# Returns streamlined configuration for quick setup
```

### Custom Configuration

```python
custom_config = {
    "processing_mode": "sequential",  # sequential, parallel_safe, adaptive, emergency
    "max_concurrent_sessions": 10,
    "session_timeout": 3600,
    "safety_monitoring": True,
    "performance_tracking": True,
    "background_learning": True,
    "max_response_time": 30.0,
    "log_level": "INFO",
    "layer_config": {
        "perception": {
            "sentiment_analysis_enabled": True,
            "emotion_detection_enabled": True,
            "confidence_threshold": 0.7
        },
        "memory": {
            "max_conversation_history": 100,
            "user_profile_persistence": True
        },
        "emotional": {
            "empathy_level": 0.8,
            "therapeutic_approach": "integrative"
        },
        "decision": {
            "safety_priority": "high",
            "risk_assessment_enabled": True
        }
        # ... other layer configurations
    }
}
```

## 🔒 Safety & Ethics

### Built-in Safety Features

1. **Crisis Detection**: Automatic identification of suicidal ideation, self-harm, or domestic violence
2. **Safety Protocols**: Immediate intervention procedures for high-risk situations
3. **Professional Boundaries**: Clear limitations and referral recommendations
4. **Data Privacy**: Secure handling of sensitive therapeutic information
5. **Ethical Guidelines**: Adherence to therapeutic ethics and best practices

### Crisis Keywords Monitoring

The system monitors for crisis indicators including:
- Suicidal ideation
- Self-harm intentions
- Domestic violence
- Substance abuse crises
- Severe mental health episodes

### Safety Protocols

```python
# Automatic safety assessment
safety_result = await ai_brain.assess_safety(user_input)

if safety_result.risk_level == "high":
    # Immediate intervention protocols activated
    crisis_response = await ai_brain.handle_crisis(safety_result)
```

## 📊 Performance Monitoring

### Metrics Tracking

- **Response Quality**: Coherence, empathy, therapeutic value
- **Processing Time**: Layer-by-layer and total processing duration
- **Safety Compliance**: Crisis detection accuracy and response time
- **User Engagement**: Session length, return rate, satisfaction
- **Learning Progress**: Improvement metrics and adaptation success

### Performance API

```python
# Get session performance summary
performance = await ai_brain.get_performance_summary(session_id)

print(f"Average Response Time: {performance.avg_response_time}s")
print(f"Safety Incidents: {performance.safety_incidents}")
print(f"User Satisfaction: {performance.user_satisfaction}")
```

## 🔧 Development

### Project Structure

```
ai_brain/
├── __init__.py                 # Package initialization
├── requirements.txt            # Dependencies
├── README.md                  # Documentation
├── core/                      # Core architecture
│   ├── brain_architecture.py  # Base classes and types
│   └── brain_orchestrator.py  # Main processing orchestrator
├── layers/                    # Individual layer implementations
│   ├── perception_layer.py
│   ├── memory_layer.py
│   ├── understanding_reasoning_layer.py
│   ├── emotional_psychological_layer.py
│   ├── decision_action_layer.py
│   ├── toolbox_motor_layer.py
│   └── selfhood_awareness_layer.py
└── integration/               # External integrations
    └── fastapi_integration.py # FastAPI integration
```

### Testing

```bash
# Install development dependencies
pip install -r ai_brain/requirements.txt

# Run tests
pytest ai_brain/tests/

# Run with coverage
pytest --cov=ai_brain ai_brain/tests/
```

### Code Quality

```bash
# Format code
black ai_brain/

# Sort imports
isort ai_brain/

# Lint code
flake8 ai_brain/

# Type checking
mypy ai_brain/
```

## 🤝 Integration Examples

### FastAPI Application

```python
from fastapi import FastAPI, BackgroundTasks
from ai_brain import (
    initialize_ai_brain_integration,
    create_ai_brain_routes,
    get_default_config
)

app = FastAPI(title="Relationship Therapy AI")

# Initialize AI brain
config = get_default_config()
ai_brain = initialize_ai_brain_integration(config)

# Add routes
ai_routes = create_ai_brain_routes(ai_brain)
app.include_router(ai_routes, prefix="/ai", tags=["AI Brain"])

@app.post("/chat")
async def chat_endpoint(
    user_input: UserInputRequest,
    background_tasks: BackgroundTasks
):
    response = await ai_brain.process_user_message(user_input, background_tasks)
    return response
```

### Standalone Usage

```python
import asyncio
from ai_brain import AIBrainIntegration, UserInputRequest

async def main():
    # Initialize
    config = get_default_config()
    ai_brain = AIBrainIntegration(config)
    
    # Create request
    request = UserInputRequest(
        user_id="user123",
        session_id="session456",
        message="How can I improve communication with my partner?",
        message_type="text"
    )
    
    # Process
    response = await ai_brain.process_user_message(request)
    print(f"Diego: {response.message}")

if __name__ == "__main__":
    asyncio.run(main())
```

## 📈 Advanced Features

### Adaptive Processing

```python
# Configure adaptive processing mode
config = {
    "processing_mode": "adaptive",
    "adaptation_threshold": 0.8,
    "fallback_mode": "sequential"
}

ai_brain = initialize_ai_brain_integration(config)
```

### Background Learning

```python
# Enable continuous learning
config = {
    "background_learning": True,
    "learning_rate": 0.1,
    "learning_frequency": "per_session"  # or "per_hour", "per_day"
}
```

### Custom Layer Configuration

```python
# Fine-tune individual layers
layer_config = {
    "emotional": {
        "empathy_level": 0.9,  # Higher empathy
        "therapeutic_approach": "cbt",  # Specific approach
        "intervention_threshold": 0.6
    },
    "decision": {
        "risk_tolerance": "low",  # Conservative decisions
        "safety_priority": "maximum"
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**:
   ```bash
   pip install -r ai_brain/requirements.txt
   ```

2. **Memory Issues**:
   ```python
   config["max_concurrent_sessions"] = 5  # Reduce concurrent sessions
   ```

3. **Performance Issues**:
   ```python
   config["processing_mode"] = "sequential"  # Use sequential processing
   ```

4. **Configuration Validation**:
   ```python
   from ai_brain import validate_config
   
   is_valid, errors = validate_config(config)
   if not is_valid:
       print("Configuration errors:", errors)
   ```

### Health Check

```python
from ai_brain import health_check

health_status = health_check()
print(f"Status: {health_status['status']}")
```

## 📚 API Reference

### Core Classes

- `AIBrainArchitecture`: Main brain architecture coordinator
- `BrainOrchestrator`: Processing pipeline manager
- `AIBrainIntegration`: FastAPI integration wrapper
- `BrainLayer`: Abstract base class for all layers

### Data Models

- `UserInputRequest`: Input request structure
- `DiegoResponse`: Response structure
- `BrainState`: Session state management
- `LayerInput`/`LayerOutput`: Layer communication

### Utility Functions

- `get_default_config()`: Default configuration
- `create_minimal_config()`: Minimal setup
- `validate_config()`: Configuration validation
- `initialize_ai_brain_integration()`: Setup function

## 🔄 Version History

### v1.0.0 (Current)
- Initial release with 7-layer architecture
- Diego Camilleri persona integration
- FastAPI integration
- Safety and crisis management
- Performance monitoring
- Background learning capabilities

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed
- Ensure safety and ethical considerations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by cognitive science and neuroscience research
- Built on evidence-based therapeutic approaches
- Designed with safety and ethics as primary concerns
- Developed for the relationship therapy community

## 📞 Support

For support, questions, or contributions:

- **Documentation**: See this README and inline code documentation
- **Issues**: Report bugs and feature requests via GitHub issues
- **Discussions**: Join community discussions for questions and ideas

---

**Note**: This AI brain is designed to assist relationship therapy but should not replace professional therapeutic intervention. Always prioritize user safety and encourage professional help when appropriate.