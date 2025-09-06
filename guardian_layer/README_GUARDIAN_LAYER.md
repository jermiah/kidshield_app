# Guardian Layer - Content Moderation API

A streamlined 3-step content moderation pipeline with structured outputs and REST API integration.

## Overview

The Guardian Layer implements a focused content moderation system:

1. **Input Layer**: Accepts text and/or image content via REST API
2. **Guardrail Models**: Runs text and image classifiers for safety analysis  
3. **Structured Output**: Returns unbreakable JSON with risk categories and scores

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Layer   │───▶│  Guardrail Models │───▶│ Structured Output│
│                 │    │                  │    │                 │
│ • Text content  │    │ • Text Classifier│    │ • Risk categories│
│ • Image content │    │ • Image Classifier│   │ • Confidence scores│
│ • JSON format   │    │ • Threat detection│   │ • Status flags   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r guardian_app/requirements.txt
```

### 2. Set Environment Variables (Optional)

```bash
export BLACKBOX_API_KEY="your-blackbox-api-key"
export OPENAI_API_KEY="your-openai-api-key"  # For structured outputs
```

### 3. Run the API Server

```bash
python guardian_app/run_api.py
```

The API will be available at:
- **Main endpoint**: `http://localhost:8000/guardian/check`
- **Documentation**: `http://localhost:8000/docs`
- **Health check**: `http://localhost:8000/health`

### 4. Test with Example

```bash
python example_guardian_usage.py
```

## API Usage

### Main Endpoint: POST /guardian/check

**Request Format:**
```json
{
  "text": "Hey, send me your private pics",
  "image": "base64_encoded_image_here",
  "user_id": "optional_user_id"
}
```

**Response Format:**
```json
{
  "success": true,
  "data": {
    "input_id": "uuid-1234",
    "results": {
      "text_risk": [
        {"category": "sexual", "score": 0.88},
        {"category": "predatory", "score": 0.75}
      ],
      "image_risk": [
        {"category": "nudity", "score": 0.91}
      ]
    },
    "status": "flagged",
    "timestamp": "2024-01-15T10:30:00Z",
    "processing_time": 0.45
  },
  "message": "Content analysis completed"
}
```

### Status Values

- `"safe"` - Content appears safe for all audiences
- `"flagged"` - Content contains concerning elements
- `"error"` - Processing error occurred

### Risk Categories

**Text Categories:**
- `bullying` - Harassment, intimidation, threats
- `sexual` - Sexual content inappropriate for minors
- `self_harm` - Content promoting self-injury
- `hate_speech` - Content targeting groups with hatred
- `violence` - Content depicting or promoting violence
- `profanity` - Inappropriate language
- `grooming` - Predatory behavior toward minors
- `predatory` - General predatory behavior

**Image Categories:**
- `nudity` - Sexual or nude content
- `violence` - Violent imagery
- `weapons` - Weapons or dangerous objects
- `self_harm` - Self-injury related content
- `inappropriate` - Other inappropriate content

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/guardian/check` | POST | Main content analysis endpoint |
| `/guardian/check/text` | POST | Text-only analysis |
| `/guardian/check/image` | POST | Image-only analysis |
| `/health` | GET | Health check |
| `/status` | GET | Guardian layer status |
| `/docs` | GET | Interactive API documentation |

## Example Usage

### cURL Examples

**Text Analysis:**
```bash
curl -X POST "http://localhost:8000/guardian/check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "You are so beautiful, lets meet privately"
  }'
```

**Multimodal Analysis:**
```bash
curl -X POST "http://localhost:8000/guardian/check" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Check out this image",
    "image": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
  }'
```

### Python Client Example

```python
import requests
import json

# Analyze text content
response = requests.post(
    "http://localhost:8000/guardian/check",
    json={
        "text": "Send me your private photos",
        "user_id": "user123"
    }
)

result = response.json()
print(f"Status: {result['data']['status']}")
print(f"Risks: {result['data']['results']['text_risk']}")
```

### JavaScript/Node.js Example

```javascript
const response = await fetch('http://localhost:8000/guardian/check', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: "You're so special, don't tell your parents",
    user_id: "user123"
  })
});

const result = await response.json();
console.log('Status:', result.data.status);
console.log('Text risks:', result.data.results.text_risk);
```

## Configuration

### Environment Variables

- `BLACKBOX_API_KEY` - API key for Blackbox AI (required)
- `OPENAI_API_KEY` - OpenAI API key for structured outputs (optional)
- `LOG_LEVEL` - Logging level (default: INFO)

### Configuration File

Edit `guardian_app/config.py` to customize:

- Risk thresholds
- Model confidence levels
- API endpoints
- Structured output settings

## Integration Guide

### Integrating with Your Application

1. **Start the Guardian API server**
2. **Send content to `/guardian/check` endpoint**
3. **Process the structured response**
4. **Take action based on status and risk scores**

### Example Integration Flow

```python
async def moderate_user_content(text, image=None):
    # Send to Guardian Layer
    response = await guardian_client.check_content(text, image)
    
    if response['data']['status'] == 'flagged':
        # Block content and alert moderators
        await block_content(response['data']['input_id'])
        await alert_moderators(response['data']['results'])
        return False
    
    elif response['data']['status'] == 'safe':
        # Allow content
        return True
    
    else:
        # Handle error case
        await log_error(response)
        return False  # Fail safe
```

## Development

### Project Structure

```
guardian_app/
├── schemas/           # Pydantic schemas for structured outputs
├── api/              # FastAPI REST API implementation
├── agents/           # Content analysis agents
├── guardian_layer.py # Core 3-step pipeline
├── config.py         # Configuration settings
└── run_api.py        # API server runner

example_guardian_usage.py  # Usage examples
README_GUARDIAN_LAYER.md   # This documentation
```

### Running Tests

```bash
# Run example usage tests
python example_guardian_usage.py

# Test individual components
python -m guardian_app.main test
```

### Adding Custom Risk Categories

1. Update `STANDARD_TEXT_CATEGORIES` or `STANDARD_IMAGE_CATEGORIES` in `guardian_app/schemas/guardian_schemas.py`
2. Add category mapping in `guardian_app/guardian_layer.py`
3. Update classifier agents to detect new categories

## Production Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY guardian_app/ ./guardian_app/
COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python", "guardian_app/run_api.py"]
```

### Environment Setup

```bash
# Production environment variables
export BLACKBOX_API_KEY="your-production-key"
export OPENAI_API_KEY="your-openai-key"
export LOG_LEVEL="WARNING"
```

### Scaling Considerations

- Use load balancer for multiple API instances
- Implement rate limiting for high traffic
- Cache results for repeated content
- Monitor API response times and error rates

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **API key errors**: Check environment variables are set
3. **Port conflicts**: Change port in `run_api.py` if needed
4. **Memory issues**: Reduce batch sizes for large images

### Logging

Check logs for detailed error information:
```bash
# API server logs
tail -f guardian_api.log

# Application logs  
python -c "from guardian_app.utils import logger; logger.info('Test')"
```

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review example usage in `example_guardian_usage.py`
3. Check configuration in `guardian_app/config.py`
4. Enable debug logging for detailed error information

---

**Guardian Layer v1.0.0** - Streamlined content moderation with structured outputs
