# MirrorCore UI React Application

This React application integrates the MirrorCore UI components with a complete frontend application structure, including authentication, routing, and API integration.

## Features

- User authentication (demo implementation)
- Session management
- Dynamic stage visualization
- Chat interface with Diego Camilleri
- Session dashboard
- Responsive design

## Project Structure

```
├── public/                 # Static files
├── src/
│   ├── assets/             # Styles and other assets
│   │   └── styles/         # CSS files
│   ├── components/         # React components
│   │   ├── mirrorcore/     # MirrorCore UI components
│   │   └── ProtectedRoute.js
│   ├── contexts/           # React contexts
│   │   └── AuthContext.js  # Authentication context
│   ├── pages/              # Page components
│   │   ├── Login.js        # Login page
│   │   ├── MirrorCorePage.js # MirrorCore wrapper page
│   │   └── NotFound.js     # 404 page
│   ├── utils/              # Utility functions
│   │   └── api.js          # API utilities
│   ├── App.js              # Main App component
│   ├── index.js            # Entry point
│   ├── index.css           # Global styles
│   ├── reportWebVitals.js  # Performance monitoring
│   └── setupProxy.js       # API proxy configuration
└── package.json            # Dependencies and scripts
```

## Setup and Installation

1. Install dependencies:

```bash
npm install
```

2. Start the development server:

```bash
npm start
```

3. Build for production:

```bash
npm run build
```

## Backend Integration

This React app is configured to work with the MirrorCore backend API. The API endpoints are proxied through `/api` to the backend server running on `http://localhost:8000`.

The proxy configuration is defined in `src/setupProxy.js`.

## Authentication

For demonstration purposes, this app uses a simple authentication system that stores the user ID in localStorage. In a production environment, you would replace this with a more secure authentication system.

## MirrorCore Components

The MirrorCore UI components are integrated into this React app:

- `MirrorCoreApp`: The main component that manages the view state between dashboard and chat.
- `MirrorCoreChatBot`: The chat interface component for interacting with Diego.
- `SessionDashboard`: The dashboard component for displaying and selecting sessions.

## API Utilities

The `src/utils/api.js` file provides utility functions for interacting with the MirrorCore backend API:

- `sendMessage`: Send a message to the MirrorCore backend.
- `getSession`: Get session information.
- `getUserSessions`: Get all sessions for a user.
- `setSessionFlag`: Set a flag for a session.

## Customization

You can customize the appearance of the MirrorCore UI by modifying the CSS variables defined in `src/assets/styles/mirrorcore.css`.
