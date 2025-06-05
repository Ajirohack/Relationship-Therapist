# MirrorCore Relationship Therapist System - Demo Scripts

This directory contains scripts to demonstrate the functionality of the MirrorCore Relationship Therapist System with its modern UI and comprehensive features.

## Quick Start

To quickly install all required dependencies and prepare the demo scripts:

```bash
# Run the installer script
./install_demo_deps.sh

# Start the server
python main_simple.py

# In a new terminal, run the demo script
./demo_script.sh
```

## Available Demo Scripts

### 1. API Feature Demo Script (`demo_script.sh`)

This script demonstrates the main API endpoints of the system by making HTTP requests and displaying the responses.

**Features demonstrated:**

- System status and health checks
- Analytics and insights retrieval
- Chat interface and therapeutic AI responses
- Knowledge base search functionality
- Settings management
- File upload and processing
- Report generation and feedback submission

**Usage:**

```bash
# Make sure the server is running first
./demo_script.sh
```

### 2. WebSocket Test Client (`test_websocket.py`)

This script connects to the WebSocket endpoint to demonstrate real-time analytics updates.

**Requirements:**

- Python 3.7+
- websockets package
- colorama package

**Installation:**

```bash
pip install websockets colorama
```

**Usage:**

```bash
# Make sure the server is running first
./test_websocket.py

# With custom parameters
./test_websocket.py --url ws://127.0.0.1:8000/ws/analytics --duration 120
```

### 3. Interactive API Tester (`test_api_interactive.py`)

This interactive tool provides a user-friendly menu-based interface for testing all API endpoints without having to remember curl commands.

**Requirements:**

- Python 3.7+
- requests package
- colorama package

**Installation:**

```bash
pip install requests colorama
```

**Usage:**

```bash
# Make sure the server is running first
./test_api_interactive.py

# With custom server URL
./test_api_interactive.py --url http://your-server:8000
```

## Running the Demo

1. Start the MirrorCore Relationship Therapist System server:

   ```bash
   python main_simple.py
   ```

2. Choose one of the following demo methods:

   **For API endpoint testing:**

   ```bash
   # Automated script
   ./demo_script.sh
   
   # Interactive menu-based testing
   ./test_api_interactive.py
   ```

   **For real-time analytics:**

   ```bash
   ./test_websocket.py
   ```

3. Access the web interfaces:
   - Dashboard: <http://127.0.0.1:8000/dashboard>
   - Chat: <http://127.0.0.1:8000/chat>
   - Knowledge Base: <http://127.0.0.1:8000/knowledge>
   - API Documentation: <http://127.0.0.1:8000/docs>

## Features Showcased

- 🎨 Modern cosmic-themed glass morphism UI
- 🧠 AI-powered therapeutic conversation
- 📊 Real-time analytics and visualizations
- 📈 Sentiment analysis and communication pattern detection
- 💡 Personalized recommendations
- 📚 Comprehensive knowledge base
- ⚙️ Multiple AI provider support
- 🔄 WebSocket for real-time updates

## Notes

- This is a demonstration system with mock data
- In a production environment, real AI models would be integrated
- The server supports various AI providers through settings configuration

## Moving to Production

For guidance on integrating the system with real AI model providers and preparing for production deployment, refer to:

- [AI Provider Integration Guide](AI_PROVIDER_INTEGRATION.md) - Details on connecting to OpenAI, Anthropic, HuggingFace, and local models
- [E2E Testing Guide](E2E_TESTING_GUIDE.md) - Comprehensive testing procedures for validating the system

When moving to production, consider:

1. Setting up proper authentication
2. Configuring a production-grade database
3. Implementing logging and monitoring
4. Setting up HTTPS for secure communication
5. Deploying in a containerized environment for scalability

### Docker Deployment

For containerized deployment, use the provided Docker files:

```bash
# Build and start the containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the containers
docker-compose down
```

The `docker-compose.yml` file includes:

- The main application container
- PostgreSQL database
- Redis for caching (optional)
- Nginx for SSL termination and static file serving (optional)
