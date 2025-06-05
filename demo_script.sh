#!/bin/bash
# MirrorCore Relationship Therapist System - Comprehensive Feature Demo Script
# Updated: June 4, 2025

echo "🧠 MirrorCore Relationship Therapist System - Feature Demo"
echo "=========================================================="

BASE_URL="http://127.0.0.1:8000"

# Function to print section headers
section() {
    echo ""
    echo "$(tput setaf 6)$1$(tput sgr0)"
    echo "$(tput setaf 6)${2:-$(printf '%*s' ${#1} | tr ' ' '-')}$(tput sgr0)"
}

# Function to make API calls and format output
call_api() {
    echo "$(tput setaf 3)➡ $1$(tput sgr0)"
    if [ "$3" == "POST" ]; then
        curl -s -X POST "$BASE_URL$2" -H "Content-Type: application/json" -d "$4" | python -m json.tool
    else
        curl -s "$BASE_URL$2" | python -m json.tool
    fi
    echo ""
}

# SECTION 1: SYSTEM STATUS
section "🛠️ SYSTEM STATUS CHECKS"

call_api "Health Check" "/api/health"
call_api "System Status" "/api/status"

# SECTION 2: ANALYTICS & INSIGHTS
section "📊 ANALYTICS & INSIGHTS"

call_api "Dashboard Analytics Data" "/api/analytics"
call_api "User Statistics" "/api/v1/user/stats"
call_api "Recent User Sessions (Last 3)" "/api/v1/user/sessions?limit=3"
call_api "AI Recommendations" "/api/recommendations"

# SECTION 3: CHAT INTERFACE
section "💬 CHAT INTERFACE"

# Test a simple chat message
echo "$(tput setaf 3)➡ Sending a test message to the Therapeutic AI$(tput sgr0)"
curl -s -X POST "$BASE_URL/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, I need help with communication in my relationship"
      }
    ]
  }' | python -m json.tool
echo ""

# Test conversation analysis
echo "$(tput setaf 3)➡ Analyzing a sample conversation$(tput sgr0)"
curl -s -X POST "$BASE_URL/api/v1/chat/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "My partner never listens to me"},
      {"role": "assistant", "content": "That sounds frustrating. Could you share a specific example?"},
      {"role": "user", "content": "Yesterday I was talking about my day and they were just on their phone"},
      {"role": "assistant", "content": "I understand why that would feel dismissive. Have you shared how that made you feel?"}
    ]
  }' | python -m json.tool
echo ""

# SECTION 4: KNOWLEDGE BASE
section "📚 KNOWLEDGE BASE"

call_api "Knowledge Base Search (Communication)" "/api/v1/knowledge-base/search?q=communication"
call_api "Knowledge Base Search (Trust)" "/api/v1/knowledge-base/search?q=trust"
call_api "Knowledge Base Search (Conflict)" "/api/v1/knowledge-base/search?q=conflict"

# SECTION 5: SETTINGS MANAGEMENT
section "⚙️ SETTINGS MANAGEMENT"

call_api "Get Current User Settings" "/api/v1/settings"

# Update settings
echo "$(tput setaf 3)➡ Updating user settings$(tput sgr0)"
curl -s -X POST "$BASE_URL/api/v1/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_provider": {
      "provider": "anthropic",
      "model": "claude-2",
      "api_key": "sk-ant-xxxxxxxxxxxx"
    },
    "knowledge_base_format": "enhanced",
    "subscription_tier": "professional",
    "extension_installed": true
  }' | python -m json.tool
echo ""

# Test AI provider connection
echo "$(tput setaf 3)➡ Testing AI provider connection$(tput sgr0)"
curl -s -X POST "$BASE_URL/api/v1/test-connection" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "anthropic",
    "api_key": "sk-ant-xxxxxxxxxxxx",
    "model": "claude-2"
  }' | python -m json.tool
echo ""

# SECTION 6: FILE PROCESSING
section "📤 FILE UPLOAD & PROCESSING"

echo "$(tput setaf 3)➡ Uploading and analyzing conversation data$(tput sgr0)"
curl -s -X POST "$BASE_URL/api/v1/upload/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "whatsapp",
    "content": {
      "messages": [
        {"sender": "User1", "text": "We need to talk about our plans", "timestamp": "2025-06-01T10:15:00Z"},
        {"sender": "User2", "text": "I thought we already decided", "timestamp": "2025-06-01T10:16:30Z"},
        {"sender": "User1", "text": "You never actually listen to my input", "timestamp": "2025-06-01T10:17:45Z"},
        {"sender": "User2", "text": "Thats not fair, I do listen", "timestamp": "2025-06-01T10:18:20Z"}
      ]
    }
  }' | python -m json.tool
echo ""

# SECTION 7: REPORTS
section "📝 REPORTS & DOCUMENTATION"

call_api "Available Analysis Reports" "/api/v1/reports"

# Submit feedback
echo "$(tput setaf 3)➡ Submitting user feedback$(tput sgr0)"
curl -s -X POST "$BASE_URL/api/v1/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 4.5,
    "comment": "The relationship insights have been very helpful. Would like to see more conflict resolution strategies.",
    "category": "feature_request"
  }' | python -m json.tool
echo ""

echo ""
echo "$(tput setaf 2)✨ Demo Complete!$(tput sgr0)"
echo "$(tput setaf 2)==================$(tput sgr0)"
echo "$(tput setaf 3)🌐 Dashboard:$(tput sgr0) $BASE_URL/dashboard"
echo "$(tput setaf 3)💬 Chat Interface:$(tput sgr0) $BASE_URL/chat"
echo "$(tput setaf 3)📚 Knowledge Base:$(tput sgr0) $BASE_URL/knowledge"
echo "$(tput setaf 3)🔄 WebSocket Analytics:$(tput sgr0) Connect to $BASE_URL/ws/analytics for real-time updates"
echo ""
echo "$(tput setaf 5)This demo showcases the Relationship Therapist system with:$(tput sgr0)"
echo "• Modern cosmic-themed glass morphism UI"
echo "• Sentiment analysis and communication pattern detection"
echo "• Real-time analytics and recommendations"
echo "• AI-powered therapeutic conversation"
echo "• Comprehensive knowledge base integration"
echo "• Multiple AI provider support"
echo ""
