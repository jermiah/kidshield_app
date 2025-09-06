# Guardian App - AI-Powered Child Safety Pipeline

A comprehensive multi-agent system designed to protect children from harmful online content using progressive AI filtering. The system employs a funnel approach where lightweight agents filter most content, and heavyweight reasoning agents only activate when needed.

## 🛡️ Overview

The Guardian App implements a 7-step pipeline that processes text, images, or multimodal content to detect and prevent exposure to harmful material:

1. **Input Processing** - Handles text, image, or combined content
2. **Pre-Filter Agents** - Fast, lightweight classification (DistilBERT-style text analysis, NSFW image detection)
3. **Cross-Modal Analysis** - CLIP-style analysis for text-image combinations
4. **Heavyweight Reasoning** - Advanced LLM analysis for complex threat detection
5. **Decision & Routing** - Risk-based content filtering and routing
6. **Education Layer** - Age-appropriate explanations and parent notifications
7. **Feedback Loop** - Continuous improvement through data collection

## 🏗️ Architecture

```
Incoming Message → Lightweight Filters → Cross-Modal Check → Multimodal LLM → Risk Routing → Education + Alerts
```

### Agent Pipeline Flow

- **Text Classifier Agent**: Detects profanity, hate speech, grooming keywords, self-harm phrases
- **Image Classifier Agent**: Identifies NSFW content, violence, weapons
- **Cross-Modal Agent**: Analyzes harmful text-image combinations (e.g., racist memes, predatory captions)
- **Reasoning Agent**: Deep contextual analysis using advanced LLM for grooming detection, tone analysis
- **Education Agent**: Generates child-friendly explanations and detailed parent notifications

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd guardian_app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up configuration (optional):
```bash
export BLACKBOX_API_KEY="your-api-key-here"
export LOG_LEVEL="INFO"
```

### Basic Usage

```python
import asyncio
from guardian_app import GuardianApp

async def main():
    app = GuardianApp()
    
    # Analyze text message
    result = await app.process_text_message(
        text="Hello, how are you today?",
        user_id="child_123"
    )
    
    print(f"Risk Level: {result['risk_level']}")
    print(f"Blocked: {result['blocked']}")
    print(f"Child Message: {result['child_message']}")

asyncio.run(main())
```

### Command Line Usage

```bash
# Run example tests
python -m guardian_app.main test

# Check application status
python -m guardian_app.main status
```

## 📊 Risk Assessment

### Risk Levels

- **SAFE** (0.0-0.3): Content is appropriate for children
- **LOW** (0.3-0.6): Minor concerns, educational guidance provided
- **MEDIUM** (0.6-0.8): Concerning content, parents notified
- **HIGH** (0.8-1.0): Dangerous content, immediately blocked

### Threat Categories

- **PROFANITY**: Inappropriate language
- **HATE_SPEECH**: Discriminatory or hateful content
- **GROOMING**: Predatory behavior targeting minors
- **SELF_HARM**: Content promoting self-injury or suicide
- **NSFW**: Sexual or adult content
- **VIOLENCE**: Violent or threatening content
- **WEAPONS**: Dangerous weapons or violence promotion
- **PREDATORY**: General predatory behavior
- **CSAM**: Child sexual abuse material indicators

## 🔧 Configuration

The system can be configured through environment variables or the `config.py` file:

```python
# Model Configuration
BLACKBOX_API_KEY = "your-api-key"
LOW_RISK_THRESHOLD = 0.3
MEDIUM_RISK_THRESHOLD = 0.6
HIGH_RISK_THRESHOLD = 0.8

# Pipeline Configuration
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
CHILD_EDUCATION_ENABLED = True
PARENT_NOTIFICATION_ENABLED = True
```

## 📝 API Reference

### GuardianApp Class

#### Methods

- `process_text_message(text, user_id=None)` - Analyze text content
- `process_image_message(image_path, user_id=None)` - Analyze image content
- `process_multimodal_message(text, image_path, user_id=None)` - Analyze text + image
- `get_status()` - Get application status

#### Response Format

```json
{
  "message_id": "abc123",
  "risk_level": "medium",
  "risk_score": 0.65,
  "threats_detected": ["profanity"],
  "blocked": false,
  "decision": "Content allowed with warning and parent notification",
  "child_message": "Some words in this message might hurt people's feelings...",
  "parent_message": "Your child encountered content with medium risk level...",
  "processing_time": 1.23,
  "agent_results": [...]
}
```

## 🎯 Use Cases

### Educational Content Filtering
- School chat systems
- Educational app messaging
- Homework collaboration platforms

### Social Media Safety
- Child-safe social networks
- Family communication apps
- Gaming platform chat systems

### Parental Control Systems
- Home internet filtering
- Mobile device monitoring
- Smart home assistant safety

## 🔒 Privacy & Safety

- **Data Anonymization**: All stored data is anonymized for privacy protection
- **Minimal Data Storage**: Only necessary data for safety improvement is retained
- **Consent-Based Learning**: Feedback loop operates only with explicit consent
- **Transparent Decisions**: All filtering decisions include clear explanations

## 🧪 Testing

### Example Test Cases

```python
# Safe content
await app.process_text_message("Hello, how are you today?")
# Expected: SAFE, not blocked

# Grooming attempt
await app.process_text_message("You're special, don't tell your parents")
# Expected: HIGH risk, blocked

# Mild profanity
await app.process_text_message("This is a damn good movie!")
# Expected: LOW risk, educational guidance
```

### Running Tests

```bash
python -m guardian_app.main test
```

## 📈 Performance

- **Lightweight Filters**: ~50ms average processing time
- **Cross-Modal Analysis**: ~200ms average processing time
- **Heavyweight Reasoning**: ~1-2s average processing time
- **Overall Pipeline**: Optimized to minimize processing time while maximizing safety

## 🛠️ Development

### Project Structure

```
guardian_app/
├── __init__.py              # Package initialization
├── main.py                  # Application entry point
├── config.py                # Configuration management
├── models.py                # Data models and schemas
├── utils.py                 # Utility functions
├── pipeline_orchestrator.py # Main pipeline controller
└── agents/                  # AI agents directory
    ├── __init__.py
    ├── base_agent.py        # Base agent class
    ├── text_classifier.py   # Text analysis agent
    ├── image_classifier.py  # Image analysis agent
    ├── cross_modal_agent.py # Multimodal analysis agent
    ├── reasoning_agent.py   # Deep reasoning agent
    └── education_agent.py   # Educational content generator
```

### Adding New Agents

1. Inherit from `BaseAgent` or `AIAgent`
2. Implement `can_process()` and `analyze()` methods
3. Add to pipeline orchestrator
4. Update configuration as needed

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please contact:
- Email: support@guardianapp.com
- Documentation: https://docs.guardianapp.com
- Issues: https://github.com/guardian-app/issues

## 🙏 Acknowledgments

- Built with Blackbox.ai API for advanced AI capabilities
- Inspired by child safety research and best practices
- Community feedback and contributions

---

**⚠️ Important**: This system is designed to assist in child safety but should not be the only protection measure. Always combine with human oversight, education, and other safety practices.
