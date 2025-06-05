# MirrorCore: Dynamic Stage Orchestration System

# MirrorCore UI Integration Files

This directory contains the UI components and utilities for integrating with the MirrorCore Dynamic Stage Orchestration system. The UI is built with React and provides a modern, responsive interface for interacting with the MirrorCore backend.

## Directory Structure

```
MirrorCore_UI_Integration_Files/
├── README.md
├── requirements.txt
├── backend/
│   └── ...
├── config/
│   └── ...
├── docs/
│   └── ...
├── frontend/
│   ├── assets/
│   │   └── styles/
│   │       └── mirrorcore.css
│   ├── components/
│   │   ├── index.js
│   │   ├── MirrorCoreApp.jsx
│   │   ├── MirrorCoreChatBot.jsx
│   │   └── SessionDashboard.jsx
│   └── utils/
│       └── api.js
```

## Components

### MirrorCoreApp

The main application component that integrates the SessionDashboard and MirrorCoreChatBot components. It manages the current view (dashboard or chat) and handles session selection.

```jsx
import { MirrorCoreApp } from './frontend/components';

function App() {
  return <MirrorCoreApp />;
}
```

### MirrorCoreChatBot

A chat interface component for interacting with Diego. It displays messages, handles user input, and shows the current session's stage and scores.

```jsx
import { MirrorCoreChatBot } from './frontend/components';

function ChatView() {
  return (
    <MirrorCoreChatBot 
      userId="user123" 
      sessionId="session456" 
      onSessionChange={(newSessionId) => console.log(newSessionId)} 
    />
  );
}
```

### SessionDashboard

A dashboard component that displays all sessions for a user and allows creating new sessions or selecting existing ones.

```jsx
import { SessionDashboard } from './frontend/components';

function DashboardView() {
  return (
    <SessionDashboard 
      userId="user123" 
      onSelectSession={(sessionId) => console.log(sessionId)} 
    />
  );
}
```

## API Utilities

The `api.js` file provides utility functions for interacting with the MirrorCore backend API:

- `sendMessage(message, userId, sessionId)`: Sends a message to the backend
- `getSession(sessionId)`: Gets session information
- `getUserSessions(userId)`: Gets all sessions for a user
- `setSessionFlag(sessionId, flagName, value)`: Sets a flag for a session

```jsx
import { sendMessage, getSession } from './frontend/utils/api';

// Example usage
async function handleSendMessage() {
  try {
    const message = {
      text: 'Hello Diego!',
      sender: 'client',
      timestamp: new Date().toISOString()
    };
    
    const response = await sendMessage(message, 'user123', 'session456');
    console.log(response);
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Styling

The UI components use CSS variables for theming and styling. The styles are defined in `frontend/assets/styles/mirrorcore.css`. The CSS uses a BEM-like naming convention with the prefix `mirrorcore-`.

## Integration with Backend

The UI components are designed to work with the MirrorCore backend API. The API endpoints are defined in `mirrorcore_router.py` and include:

- `/mirrorcore/message`: Processes client messages
- `/mirrorcore/session/{session_id}`: Retrieves session information
- `/mirrorcore/flag/{session_id}`: Sets a flag for a session
- `/mirrorcore/user/{user_id}/sessions`: Retrieves all sessions for a user

## Getting Started

1. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Start the backend server:

   ```
   python mirrorcore_main.py
   ```

3. Integrate the UI components into your React application

## Stage Visualization

The UI visually represents the different stages (APP, FPP, RPP) with different colors:

- APP (Acquaintance Phase): Blue
- FPP (Friend Phase): Green
- RPP (Romantic Phase): Orange

The current stage is displayed in the chat header and in the session cards on the dashboard.

## Overview

MirrorCore is a logic-driven controller designed to monitor interactions, analyze trust and emotional openness, and trigger movement between relationship stages (APP → FPP → RPP). It serves as the intelligence layer for the Character Archivist System, enabling dynamic conversation flow based on user engagement metrics.

## Key Components

### 1. Stage Controller

The Stage Controller (`stage_controller.py`) is the core component that manages stage transitions based on interaction scores and defined rules. It:

- Tracks the current stage (APP, FPP, RPP)
- Evaluates exit conditions for each stage
- Manages custom flags for special transition conditions
- Provides a clean API for recording messages and getting session state

### 2. Score Interpreter

The Score Interpreter (`score_interpreter.py`) calculates trust and emotional openness scores based on message content and interaction patterns. It analyzes:

- Sentiment analysis
- Message length
- Response latency
- Question ratio
- Personal pronouns
- Intimacy keywords
- Reciprocation
- Attachment cues
- Politeness

### 3. Format Message Templates (FMTs)

The FMT Loader (`fmt_loader.py`) manages message templates for each stage, providing appropriate responses based on the current stage and context. Each template includes:

- Stage association
- Trigger conditions
- Goals
- Tone
- Core message and variations
- AI behaviors

### 4. Session Model

The Session Model (`session_model.py`) handles persistence of session data, including:

- Messages
- Stage history
- Trust and openness scores
- Custom flags

### 5. API Router

The API Router (`mirrorcore_router.py`) provides FastAPI endpoints for interacting with the MirrorCore system:

- Processing messages
- Getting session information
- Setting flags
- Managing user sessions

## Setup and Installation

### Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Other dependencies in requirements.txt

### Installation

1. Clone the repository
2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

3. Ensure the directory structure is set up correctly:

   ```
   MirrorCore_UI_Integration_Files/
   ├── backend/
   │   ├── __init__.py
   │   ├── fmt_loader.py
   │   ├── mirrorcore_main.py
   │   ├── mirrorcore_router.py
   │   ├── score_interpreter.py
   │   ├── session_model.py
   │   └── stage_controller.py
   ├── config/
   │   ├── mirrorcore_config.json
   │   └── stage_definitions.json
   ├── data/
   │   └── (session data will be stored here)
   ├── formats/
   │   ├── APP/
   │   ├── FPP/
   │   └── RPP/
   └── README.md
   ```

### Running the API

```bash
python -m relationship_therapist_system.MirrorCore_UI_Integration_Files.backend.mirrorcore_main
```

The API will be available at <http://localhost:8000>

## API Documentation

Once the server is running, API documentation is available at:

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## Configuration

### Stage Definitions

Stage definitions are stored in `config/stage_definitions.json` and define the entry, maintenance, and exit conditions for each stage.

### MirrorCore Config

General configuration is stored in `config/mirrorcore_config.json` and includes settings for:

- Scoring thresholds and weights
- UI display options
- FMT loading behavior
- Stage transition rules

## Usage Example

```python
from relationship_therapist_system.MirrorCore_UI_Integration_Files.backend.stage_controller import StageController
from relationship_therapist_system.MirrorCore_UI_Integration_Files.backend.fmt_loader import FmtLoader
import datetime as dt

# Create a controller for a user
controller = StageController(user_id="user123")

# Record a message from Diego
controller.record_diego("How are you feeling today?", dt.datetime.now())

# Record a client message and get the result
result = controller.record_cl("I'm feeling great! Thanks for asking.", dt.datetime.now())

# Get the current stage and scores
print(f"Stage: {result['stage']}")
print(f"Trust: {result['scores']['trust']}")
print(f"Openness: {result['scores']['open']}")

# Get an appropriate FMT for the current stage
fmt_loader = FmtLoader()
fmt = fmt_loader.get_fmt(result['stage'])
response = fmt_loader.get_fmt_variation(fmt)

print(f"Response: {response}")
```

## Next Steps

1. **Frontend Integration**: Develop a UI that displays the current stage, trust/openness scores, and stage history.
2. **LLM Integration**: Connect the MirrorCore system to an LLM for more dynamic response generation.
3. **Analytics Dashboard**: Create a dashboard for analyzing stage transitions and user engagement.
4. **Expanded FMTs**: Develop more Format Message Templates for each stage.
5. **Fine-tuned Scoring**: Calibrate the scoring weights based on real-world usage data.

## License

This project is proprietary and confidential.
