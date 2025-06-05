# Relationship Therapist Assistant - Browser Extension

A Chrome browser extension that provides real-time relationship guidance and conversation analysis while you chat on various messaging platforms.

## Features

### 🤖 Real-time Assistance

- **Smart Suggestions**: Get contextual advice while chatting
- **Conversation Analysis**: Analyze communication patterns and emotional tone
- **Relationship Insights**: Receive personalized recommendations based on your conversations

### 💬 Platform Support

- WhatsApp Web
- Facebook Messenger
- Telegram Web
- Discord
- Slack
- Instagram Direct Messages
- Twitter/X Direct Messages

### 🔐 Secure & Private

- End-to-end encryption for sensitive data
- Local processing when possible
- Secure authentication with JWT tokens
- No conversation data stored without consent

### 📊 Analytics & Insights

- Communication pattern analysis
- Emotional tone tracking
- Relationship health metrics
- Progress tracking over time

## Installation

### Prerequisites

- Google Chrome browser (version 88 or higher)
- Relationship Therapist Assistant backend server running

### Install from Source

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd relationship_therapist_system/browser_extension
   ```

2. **Open Chrome Extensions page**:
   - Navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right)

3. **Load the extension**:
   - Click "Load unpacked"
   - Select the `browser_extension` folder
   - The extension should now appear in your extensions list

4. **Pin the extension**:
   - Click the puzzle piece icon in Chrome toolbar
   - Find "Relationship Therapist Assistant"
   - Click the pin icon to keep it visible

## Setup

### 1. Backend Server

Ensure the backend server is running:

```bash
cd relationship_therapist_system
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Create Account

1. Click the extension icon in your browser
2. Click "Don't have an account? Sign up"
3. Fill in your details:
   - Email address
   - Password
   - Role (User or Therapist)
4. Click "Sign Up"

### 3. Login

1. Enter your email and password
2. Click "Sign In"
3. You should see the main dashboard

## Usage

### Getting Started

1. **Navigate to a supported messaging platform**
2. **Look for the floating assistant button** (💝) in the top-right corner
3. **Click the button** to open the assistant panel

### Using the Assistant Panel

The assistant panel has three main tabs:

#### 📝 Suggestions Tab

- **Auto-suggestions**: Automatically generated based on conversation context
- **Manual suggestions**: Click "Get Suggestion" for on-demand advice
- **Confidence scores**: Each suggestion includes a confidence rating
- **Reasoning**: Understand why each suggestion was made

#### 📊 Analysis Tab

- **Conversation analysis**: Deep analysis of communication patterns
- **Emotional metrics**: Tone, sentiment, and emotional intelligence scores
- **Recommendations**: Actionable advice for improving communication
- **Export options**: Save analysis results for later review

#### 💡 Insights Tab

- **Relationship insights**: Long-term patterns and trends
- **Progress tracking**: See how your communication improves over time
- **Personalized tips**: Customized advice based on your communication style

### Keyboard Shortcuts

- **Ctrl+Shift+A** (Cmd+Shift+A on Mac): Toggle assistant panel
- **Ctrl+Shift+S** (Cmd+Shift+S on Mac): Get quick suggestion
- **Ctrl+Shift+D** (Cmd+Shift+D on Mac): Analyze current conversation

### Settings

Access settings through the popup:

- **Auto Suggestions**: Enable/disable automatic suggestions
- **Real-time Analysis**: Toggle live conversation analysis
- **Notifications**: Control notification preferences

## Supported Platforms

### WhatsApp Web

- URL: `web.whatsapp.com`
- Features: Full support for suggestions and analysis
- Message detection: Automatic

### Facebook Messenger

- URL: `messenger.com`
- Features: Full support
- Message detection: Automatic

### Telegram Web

- URL: `web.telegram.org`
- Features: Full support
- Message detection: Automatic

### Discord

- URL: `discord.com`
- Features: Full support
- Message detection: Automatic

### Other Platforms

- Instagram, Twitter, Slack: Basic support
- Custom platforms: May require manual configuration

## Troubleshooting

### Extension Not Loading

1. Check that Developer mode is enabled
2. Refresh the extensions page
3. Try reloading the extension
4. Check browser console for errors

### Assistant Panel Not Appearing

1. Refresh the messaging platform page
2. Check if the platform is supported
3. Ensure you're logged into the extension
4. Try toggling the assistant with keyboard shortcut

### Authentication Issues

1. Check that the backend server is running
2. Verify server URL in extension settings
3. Clear extension storage and re-login
4. Check network connectivity

### Suggestions Not Working

1. Ensure you're logged in
2. Check internet connection
3. Verify API endpoints are accessible
4. Try refreshing the page

### Performance Issues

1. Close unnecessary tabs
2. Disable other extensions temporarily
3. Clear browser cache
4. Restart Chrome

## Privacy & Security

### Data Handling

- **Local Processing**: Basic analysis done locally when possible
- **Encrypted Transmission**: All data sent to server is encrypted
- **No Permanent Storage**: Conversations not stored without explicit consent
- **User Control**: Full control over what data is shared

### Permissions

The extension requires these permissions:

- **Active Tab**: To interact with messaging platforms
- **Storage**: To save user preferences and cache
- **Host Permissions**: To access supported messaging platforms
- **Background**: For real-time features and notifications

### Security Features

- JWT token authentication
- Automatic token refresh
- Secure API communication
- Content Security Policy enforcement

## Development

### File Structure

```
browser_extension/
├── manifest.json          # Extension configuration
├── background.js          # Service worker for API communication
├── content.js            # Content script for page interaction
├── content.css           # Styles for injected UI
├── popup.html            # Extension popup interface
├── popup.css             # Popup styles
├── popup.js              # Popup functionality
└── README.md             # This file
```

### Building

No build process required - the extension runs directly from source files.

### Testing

1. Load extension in developer mode
2. Open browser console for debugging
3. Test on supported platforms
4. Check background script logs

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## API Integration

The extension communicates with the backend API:

### Authentication Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `POST /api/v1/auth/logout` - User logout

### Analysis Endpoints

- `POST /api/v1/realtime/recommendation` - Get suggestions
- `POST /api/v1/analyze/conversation` - Analyze conversations
- `GET /api/v1/user/stats` - Get user statistics

### WebSocket Connection

- `ws://localhost:8000/ws` - Real-time updates

## Support

### Getting Help

- Check this README for common issues
- Review browser console for error messages
- Check backend server logs
- Contact support through the extension popup

### Reporting Issues

When reporting issues, please include:

- Browser version
- Extension version
- Steps to reproduce
- Error messages
- Platform being used

### Feature Requests

Submit feature requests through:

- GitHub issues
- Extension feedback form
- Direct contact

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Changelog

### Version 1.0.0

- Initial release
- Support for major messaging platforms
- Real-time suggestions and analysis
- User authentication
- Settings management
- WebSocket integration

---

**Note**: This extension is designed to help improve communication in relationships. It should not replace professional therapy or counseling when needed.
