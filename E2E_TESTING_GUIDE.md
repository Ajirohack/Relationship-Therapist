# End-to-End Testing Guide

## System Status ✅

The Relationship Therapist System is now **READY FOR E2E TESTING**!

### Current System State

- ✅ Database initialized with all required tables
- ✅ Environment configuration (.env) created
- ✅ Directory structure established
- ✅ FastAPI server running on <http://localhost:8000>
- ✅ All core components initialized (minimal mode)
- ✅ Basic functionality available without heavy ML dependencies

## Available API Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/
```

### 2. Upload Conversation Data

```bash
curl -X POST "http://localhost:8000/api/v1/upload/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "platform": "whatsapp",
    "conversations": [
      {
        "text": "I love spending time with you",
        "sender": "user1",
        "timestamp": "2024-01-01T10:00:00"
      },
      {
        "text": "You make me so happy!",
        "sender": "user2",
        "timestamp": "2024-01-01T10:01:00"
      }
    ]
  }'
```

### 3. Analyze Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/conversation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "analysis_type": "comprehensive",
    "conversations": [
      {
        "text": "I love spending time with you",
        "sender": "user1",
        "timestamp": "2024-01-01T10:00:00"
      },
      {
        "text": "You make me so happy!",
        "sender": "user2",
        "timestamp": "2024-01-01T10:01:00"
      }
    ]
  }'
```

### 4. Get Real-time Recommendations

```bash
curl -X POST "http://localhost:8000/api/v1/realtime/recommendation" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "current_message": "We had a fight today",
    "context": {
      "recent_mood": "tense",
      "relationship_stage": "committed"
    }
  }'
```

### 5. User Profile Management

```bash
# Create/Update Profile
curl -X POST "http://localhost:8000/api/v1/user/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user_001",
    "profile_data": {
      "age": 28,
      "relationship_status": "in_relationship",
      "goals": ["improve_communication", "resolve_conflicts"]
    }
  }'

# Get Profile
curl "http://localhost:8000/api/v1/user/profile/test_user_001"
```

## Testing Scenarios

### Scenario 1: Positive Relationship Analysis

**Test Data:**

```json
{
  "conversations": [
    {"text": "I love you so much", "sender": "user1"},
    {"text": "You make me feel special", "sender": "user2"},
    {"text": "I appreciate how you listen to me", "sender": "user1"}
  ]
}
```

**Expected Results:**

- High relationship health score (>0.7)
- Positive sentiment analysis
- Positive indicators detected
- Supportive recommendations

### Scenario 2: Conflict Detection

**Test Data:**

```json
{
  "conversations": [
    {"text": "You never listen to me", "sender": "user1"},
    {"text": "That's not true, you're being dramatic", "sender": "user2"},
    {"text": "I feel like we're always fighting", "sender": "user1"}
  ]
}
```

**Expected Results:**

- Lower relationship health score
- Negative sentiment detected
- Conflict resolution recommendations
- Communication improvement suggestions

### Scenario 3: Red Flag Detection

**Test Data:**

```json
{
  "conversations": [
    {"text": "You're not allowed to see your friends", "sender": "user1"},
    {"text": "I need to check your phone", "sender": "user1"},
    {"text": "It's your fault we're having problems", "sender": "user1"}
  ]
}
```

**Expected Results:**

- Red flags detected
- Professional counseling recommendations
- Warning about concerning patterns

## Web Interface Testing

1. **Open Browser:** Navigate to <http://localhost:8000>
2. **API Documentation:** Visit <http://localhost:8000/docs> for interactive API testing
3. **Health Check:** Verify the welcome message appears

## Database Verification

```bash
# Check database contents
sqlite3 relationship_therapist.db

# View tables
.tables

# Check users
SELECT * FROM users;

# Check conversations
SELECT * FROM conversations;

# Check analysis sessions
SELECT * FROM analysis_sessions;
```

## File Upload Testing

### Test Text File Upload

```bash
# Create test file
echo "I love spending time with my partner. We communicate well." > test_conversation.txt

# Upload file (implement file upload endpoint if needed)
curl -X POST "http://localhost:8000/api/v1/upload/file" \
  -F "file=@test_conversation.txt" \
  -F "user_id=test_user_001"
```

## Performance Testing

### Load Testing with Multiple Requests

```bash
# Test multiple concurrent requests
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/v1/analyze/conversation" \
    -H "Content-Type: application/json" \
    -d '{"user_id":"user_'$i'","conversations":[{"text":"Test message","sender":"user1"}]}' &
done
wait
```

## Expected System Behavior

### ✅ Working Features (Minimal Mode)

- Basic sentiment analysis using VADER
- Communication style detection
- Red flag pattern matching
- Positive indicator detection
- Basic recommendation generation
- Database operations
- API endpoints
- File structure management

### ⚠️ Limited Features (Heavy Dependencies Disabled)

- Advanced NLP processing (spaCy, transformers)
- Semantic similarity search
- Advanced ML-based analysis
- Complex report generation
- Audio/video processing

## Troubleshooting

### Common Issues

1. **Server Won't Start**

   ```bash
   # Check if port is in use
   lsof -i :8000
   
   # Kill existing process
   kill -9 <PID>
   ```

2. **Database Errors**

   ```bash
   # Reinitialize database
   python3 init_db.py
   ```

3. **Import Errors**

   ```bash
   # Check Python environment
   which python3
   pip3 list
   ```

## Next Steps for Production

### For Official Trials

1. **Install Heavy Dependencies:**

   ```bash
   pip3 install torch transformers sentence-transformers
   pip3 install spacy textblob scikit-learn
   python3 -m spacy download en_core_web_sm
   ```

2. **Configure API Keys:**
   - Update `.env` with real API keys
   - OpenAI API key for advanced AI features
   - Hugging Face token for model access

3. **Database Migration:**
   - Consider PostgreSQL for production
   - Set up proper backup strategies

4. **Security Enhancements:**
   - Implement authentication
   - Add rate limiting
   - Enable HTTPS

5. **Monitoring:**
   - Add logging aggregation
   - Set up health monitoring
   - Implement error tracking

## Success Criteria

✅ **E2E Testing Complete When:**

- All API endpoints respond correctly
- Database operations work as expected
- Analysis produces reasonable results
- Recommendations are generated
- No critical errors in logs
- System handles various input types

---

**System Status: READY FOR E2E TESTING** 🚀

The relationship therapist system is now functional with basic AI capabilities and ready for comprehensive testing!
