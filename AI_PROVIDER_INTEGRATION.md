# AI Provider Integration Guide for MirrorCore Relationship Therapist

This guide explains how to integrate the Relationship Therapist system with various AI model providers for production use. The system is designed to be modular, allowing you to use different AI providers based on your requirements.

## Supported AI Providers

The system currently supports integration with the following AI providers:

1. **OpenAI API** (GPT-3.5, GPT-4)
2. **Anthropic** (Claude, Claude Instant)
3. **HuggingFace Models** (via API or local deployment)
4. **Local Models** (with compatible interface)

## Prerequisites

Before integrating with AI providers, ensure you have:

1. An active account with your chosen AI provider
2. API keys or access tokens
3. Sufficient API credits or subscription
4. Network access from your deployment environment to the API endpoints

## Configuration Process

### 1. Environment Variables Setup

Create or update the `.env` file in your project root with your API keys:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_ORG_ID=org-your-org-id-here  # Optional

# Anthropic Configuration
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# HuggingFace Configuration
HF_API_TOKEN=hf_your-huggingface-token-here
HF_MODEL_ENDPOINT=https://api-inference.huggingface.co/models/your-model-name

# Local Model Configuration
LOCAL_MODEL_PATH=/path/to/your/model
LOCAL_MODEL_TYPE=llama  # or other supported model types
```

### 2. Configure Provider Settings

Update the AI provider settings in the system:

#### Method A: Through the UI

1. Log in to the system
2. Navigate to Settings
3. Select the "AI Providers" tab
4. Choose your preferred provider
5. Enter your API key
6. Test the connection
7. Save settings

#### Method B: API Configuration

Use the settings API endpoint to configure the provider:

```bash
curl -X POST "http://your-server:8000/api/v1/settings" \
  -H "Content-Type: application/json" \
  -d '{
    "ai_provider": {
      "provider": "openai",
      "model": "gpt-4",
      "api_key": "sk-your-openai-key-here"
    },
    "knowledge_base_format": "enhanced",
    "subscription_tier": "professional",
    "extension_installed": true
  }'
```

#### Method C: Direct Configuration File

Edit the `config.py` file to set default provider settings:

```python
AI_PROVIDERS = {
    "default": {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": os.getenv("OPENAI_API_KEY")
    },
    "fallback": {
        "provider": "anthropic",
        "model": "claude-2",
        "api_key": os.getenv("ANTHROPIC_API_KEY")
    }
}
```

## Provider-Specific Setup

### OpenAI

1. Create an account at [OpenAI Platform](https://platform.openai.com/)
2. Generate an API key in your account settings
3. Set up billing to ensure continuous API access
4. Recommended models:
   - `gpt-4` for highest quality responses
   - `gpt-3.5-turbo` for cost-effective operation

```python
# Example implementation
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a relationship therapist..."},
        {"role": "user", "content": user_message}
    ],
    temperature=0.7
)
```

### Anthropic

1. Sign up at [Anthropic](https://www.anthropic.com/)
2. Request API access if not already available
3. Generate API key in your account dashboard
4. Recommended models:
   - `claude-2` for comprehensive analysis
   - `claude-instant` for faster, more economical responses

```python
# Example implementation
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-2",
    system="You are a relationship therapist...",
    messages=[
        {"role": "user", "content": user_message}
    ],
    max_tokens=1000
)
```

### HuggingFace Models

1. Create an account on [HuggingFace](https://huggingface.co/)
2. Generate an access token in your account settings
3. Choose a suitable model from the model hub
4. Configure the endpoint URL for your chosen model

```python
# Example implementation
import requests

API_URL = f"https://api-inference.huggingface.co/models/your-chosen-model"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

output = query({
    "inputs": "You are a relationship therapist. " + user_message,
})
```

### Local Models

1. Download a compatible model (e.g., LLaMA, Falcon, Mistral)
2. Set up the necessary environment for running the model
3. Configure the model path and parameters

```python
# Example implementation (using LLaMA.cpp Python bindings)
from llama_cpp import Llama

llm = Llama(
    model_path=os.getenv("LOCAL_MODEL_PATH"),
    n_ctx=2048,
    n_threads=8
)

prompt = "You are a relationship therapist. " + user_message
output = llm(prompt, max_tokens=512, temperature=0.7)
```

## Testing the Integration

After configuring your chosen provider, test the integration:

1. Run the connection test:
   ```bash
   ./test_api_interactive.py
   ```
   Select option 11 (Test AI Provider Connection)

2. Send a test chat message:
   ```bash
   curl -X POST "http://your-server:8000/api/v1/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "messages": [
         {
           "role": "user",
           "content": "Hello, I need help with my relationship"
         }
       ],
       "settings": {
         "provider": "openai"  # or your chosen provider
       }
     }'
   ```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your API key is correct and not expired
   - Check that billing is active on your account
   - Ensure the API key has the necessary permissions

2. **Rate Limiting**
   - Implement exponential backoff for retries
   - Monitor your usage and adjust accordingly
   - Consider upgrading your subscription tier

3. **Model Availability**
   - Some models may have waitlists or restricted access
   - Check the provider's status page for service disruptions
   - Configure fallback models for reliability

4. **Response Quality**
   - Adjust the temperature parameter for more consistent responses
   - Refine your system prompts for better therapeutic guidance
   - Test with different models to find the best fit for your use case

### Logging and Monitoring

Enable detailed logging for debugging:

```python
# In config.py
LOGGING_LEVEL = "DEBUG"  # Set to INFO, WARNING, or ERROR in production
AI_PROVIDER_LOGGING = True
```

## Best Practices

1. **Security**
   - Never hardcode API keys in your code
   - Rotate API keys periodically
   - Use environment variables or a secure key management service

2. **Cost Management**
   - Set usage limits on your API accounts
   - Monitor token usage and implement controls
   - Cache common responses when appropriate

3. **Performance**
   - Implement asynchronous processing for better user experience
   - Use streaming responses for long-form therapeutic content
   - Set appropriate timeouts for API calls

4. **Fallback Strategy**
   - Configure multiple providers for redundancy
   - Implement automatic failover when a provider is unavailable
   - Have a basic rule-based system as a last resort

## Production Readiness Checklist

Before going live with your integration:

- [ ] API keys and secrets are securely stored
- [ ] Rate limiting and retry logic is implemented
- [ ] Error handling is comprehensive
- [ ] Logging and monitoring are configured
- [ ] Cost controls are in place
- [ ] Fallback providers are configured
- [ ] Performance is optimized for your expected load
- [ ] Response quality has been evaluated with test cases

## Further Resources

- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
- [Anthropic API Documentation](https://docs.anthropic.com/claude/reference)
- [HuggingFace API Documentation](https://huggingface.co/docs/api-inference/index)
- [LLaMA.cpp Documentation](https://github.com/ggerganov/llama.cpp)

---

For technical support with integrations, please contact the MirrorCore development team.
