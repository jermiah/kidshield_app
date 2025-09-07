![honu_logo](https://github.com/user-attachments/assets/248fa6d7-7084-42c6-908c-ab59e5e920b0)

A comprehensive three-layer AI system designed to protect children online through intelligent content analysis, decision-making, and coordinated response actions. KidShield combines advanced LLM capabilities with robust safety mechanisms to provide real-time protection against digital threats.

## 🎯 Overview

This system receives incoming messages that have already been classified as suspicious and focuses on:

- **Detects Threats**: Uses advanced LLM models to analyze text and images for potential dangers
- **Makes Smart Decisions**: AI-enhanced decision engine determines appropriate protective actions
- **Coordinates Responses**: Manages communications with parents, children, and relevant authorities
- **Provides Education**: Delivers age-appropriate safety resources and guidance
- **Ensures Safety**: Maintains comprehensive audit trails and fallback mechanisms

## 🏗️ Three-Layer Architecture

KidShield implements a clean three-layer architecture for maximum modularity and scalability:

```
┌─────────────────────────────────────────────────────────────┐
│                      APP LAYER                              │
│  User Interfaces • APIs • Authentication • Dashboards      │
├─────────────────────────────────────────────────────────────┤
│                    GUARDIAN LAYER                           │
│  LLM Analysis • Threat Detection • Content Classification  │
├─────────────────────────────────────────────────────────────┤
│                     AGENT LAYER                             │
│  Decision Making • Communication • Action Coordination     │
└─────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

**🖥️ App Layer**: User-facing interfaces, authentication, and application logic  
**🛡️ Guardian Layer**: AI-powered content analysis and threat detection  
**🤖 Agent Layer**: Intelligent decision-making and response coordination

## 🤖 LLM Integration

The system integrates with **BlackBox AI** to provide enhanced capabilities:

- **Enhanced Decision Reasoning**: AI-generated explanations for all decisions
- **Personalized Communications**: Context-aware messages for parents, children, and senders
- **Age-Appropriate Content**: Automatically adapted messaging based on child's age and situation
- **Fallback Safety**: Graceful degradation to template-based responses if LLM is unavailable

## 🏗️ System Architecture

### Core Components

1. **Message Processor** - Handles incoming suspicious messages with metadata
2. **Decision Engine** - Analyzes context and selects appropriate actions
3. **Communication Generator** - Creates tailored messages for different stakeholders
4. **Action Manager** - Coordinates and executes chosen actions
5. **Educational Content Library** - Age-appropriate safety resources
6. **Logging & Audit System** - Tracks decisions and actions for transparency

### Key Features

- ✅ Multi-stakeholder communication (parents, children, senders)
- ✅ Age-appropriate content generation
- ✅ Severity assessment algorithms
- ✅ Educational resource matching
- ✅ Action justification and audit trails
- ✅ Configurable response templates
- ✅ Comprehensive logging and monitoring

## 📁 Complete Project Structure

```
kidshield_app/
├── 📱 app_layer/                    # User Interface & Application Logic
│   ├── __init__.py
│   ├── api/                         # REST API endpoints
│   │   ├── __init__.py
│   │   └── main_api.py             # Main application API
│   ├── frontend/                    # Web interface components
│   │   ├── index.html              # Main dashboard
│   │   └── app.js                  # Frontend JavaScript
│   ├── models/                      # Application data models
│   │   ├── __init__.py
│   │   └── user_models.py          # User profiles and settings
│   └── nodejs/                      # Node.js components
│       ├── index.js                # Node.js server
│       ├── package.json            # Node dependencies
│       └── package-lock.json
│
├── 🛡️ guardian_layer/               # LLM-Powered Threat Detection
│   ├── __init__.py
│   ├── config.py                   # Guardian configuration
│   ├── main.py                     # Guardian main entry point
│   ├── models.py                   # Guardian data models
│   ├── utils.py                    # Guardian utilities
│   ├── pipeline_orchestrator.py   # Analysis pipeline coordination
│   ├── structured_outputs.py      # LLM output formatting
│   ├── run_api.py                  # Guardian API server
│   ├── agents/                     # AI Analysis Agents
│   │   ├── __init__.py
│   │   ├── base_agent.py          # Base agent class
│   │   ├── text_classifier.py     # Text threat detection
│   │   ├── image_classifier.py    # Image threat detection
│   │   ├── reasoning_agent.py     # Advanced reasoning
│   │   ├── education_agent.py     # Educational content
│   │   └── cross_modal_agent.py   # Multi-modal analysis
│   ├── api/                        # Guardian API endpoints
│   │   ├── __init__.py
│   │   ├── guardian_api.py        # Main Guardian API
│   │   └── input_normalizer.py    # Input preprocessing
│   └── schemas/                    # Data validation schemas
│       ├── __init__.py
│       ├── api_schemas.py         # API request/response schemas
│       ├── guardian_schemas.py    # Guardian-specific schemas
│       └── simple_schemas.py      # Simplified data structures
│
├── 🤖 agent_layer/                  # Decision Making & Response Coordination
│   ├── __init__.py
│   ├── agents/                     # AI Decision Agents
│   │   ├── __init__.py
│   │   └── ai_agent.py            # Main AI agent coordinator
│   ├── communication/              # Message Generation
│   │   ├── __init__.py
│   │   └── message_generator.py   # LLM-enhanced messaging
│   ├── decision_engine/            # Decision Making Logic
│   │   ├── __init__.py
│   │   └── decision_engine.py     # Risk assessment & action selection
│   ├── integrations/               # Layer Integration
│   │   ├── __init__.py
│   │   └── guardian_integration.py # Guardian Layer integration
│   ├── models/                     # Agent Data Models
│   │   ├── __init__.py
│   │   ├── actions.py             # Action definitions
│   │   └── message.py             # Message structures
│   ├── tools/                      # Action Tools
│   │   ├── __init__.py
│   │   └── notification_service.py # Notification delivery
│   └── utils/                      # Agent Utilities
│       ├── __init__.py
│       ├── blackbox_client.py     # LLM API client
│       └── logger.py              # Logging and audit
│
├── ⚙️ config/                       # System Configuration
│   ├── agent_config.json          # Agent system settings
│   └── educational_content.json   # Safety resources and tips
│
├── 📊 data/                         # Sample Data & Test Cases
│   └── sample_messages.json       # Realistic test scenarios
│
├── 📚 examples/                     # Usage Examples
│   ├── basic_usage.py             # Standard system demonstration
│   ├── guardian_integration_usage.py # Guardian Layer examples
│   └── llm_enhanced_usage.py      # LLM integration examples
│
├── 🧪 tests/                        # Comprehensive Test Suite
│   ├── test_ai_agent.py           # Agent system tests
│   ├── test_blackbox_integration.py # LLM integration tests
│   ├── test_decision_engine.py    # Decision engine tests
│   └── test_guardian_integration.py # Guardian integration tests
│
├── 🌐 html/                         # Static Web Assets
│   └── privacy-policy.html        # Privacy policy page
│
├── 🔧 Integration Tests             # System Integration Testing
│   ├── test_critical_integration.py
│   ├── test_enhanced_agent_actions.py
│   ├── test_integration_simple.py
│   ├── test_simplified_response.py
│   └── test_three_layer_integration.py
│
├── 📋 Documentation                 # Project Documentation
│   ├── README.md                  # This comprehensive guide
│   ├── README_FRONTEND.md         # Frontend-specific documentation
│   ├── SYSTEM_OVERVIEW.md         # Complete system overview
│   ├── ARCHITECTURE_ANALYSIS.md   # Architecture analysis
│   ├── LAYER_REORGANIZATION_SUMMARY.md # Layer organization guide
│   ├── TODO.md                    # Development progress
│   └── TODO_INTEGRATION.md        # Integration tasks
│
├── 🔐 Environment & Dependencies    # System Setup
│   ├── .env                       # Environment variables (API keys)
│   ├── .env.example              # Environment template
│   ├── requirements.txt          # Python dependencies
│   ├── package.json              # Node.js dependencies
│   ├── package-lock.json         # Node.js lock file
│   └── myenv/                    # Python virtual environment
│
└── 🛠️ Development Tools             # Development Support
    ├── .gitignore                # Git ignore rules
    ├── .blackboxrules           # BlackBox AI configuration
    └── nodejs/                   # Additional Node.js tools
        └── index.js
```

## 🔄 Layer Interaction Flow

The three layers work together in a coordinated flow:

```
1. 📱 App Layer receives user input (message, image, etc.)
   ↓
2. 🛡️ Guardian Layer analyzes content using LLM models
   ↓ (threat detected)
3. 🤖 Agent Layer makes decisions and coordinates responses
   ↓
4. 📱 App Layer delivers notifications and educational content
```

### Integration Points

- **App → Guardian**: Content submission for analysis
- **Guardian → Agent**: Threat detection results and risk scores
- **Agent → App**: Action plans and communication content
- **Cross-Layer**: Comprehensive logging and audit trails

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- BlackBox AI API key
- Required packages (see requirements.txt)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jermiah/kidshield_app.git
cd kidshield_app
```

2. Install dependencies:
```bash
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

3. Set up your BlackBox API key:
```bash
# Create .env file with your API key
touch .env
echo "BLACKBOX_API_KEY=your_api_key_here" > .env
```

4. Run fastapi server:
```bash
cd guardian_layer/api
fastapi run guardian_api.py
```

5. Run nodejs server to connect to WhatsApp
```bash
cd app_layer/nodejs
npm i
npm run dev
```

### Basic Usage

```python
from src.agents.ai_agent import AIAgent
from src.models.message import SuspiciousMessage, ChildProfile, MessageMetadata, ThreatType, SeverityLevel

# Initialize the AI agent with LLM enhancement
agent = AIAgent(use_llm=True)

# Create a suspicious message (normally received from detection system)
message = SuspiciousMessage(
    message_id="msg_001",
    content="Suspicious content here",
    threat_type=ThreatType.BULLYING,
    severity=SeverityLevel.HIGH,
    child_profile=child_profile,
    metadata=metadata
)

# Process the message
action_plan = agent.process_suspicious_message(message)

# Review the action plan with AI-enhanced reasoning
print(f"Generated {len(action_plan.decisions)} decisions")
print(f"Created {len(action_plan.communications)} communications")

# View enhanced reasoning
for decision in action_plan.decisions:
    print(f"Action: {decision.action_type.value}")
    print(f"AI Reasoning: {decision.reasoning}")
```

### LLM Configuration

The system can be configured to use or disable LLM features:

```python
# Enable LLM (default)
agent = AIAgent(use_llm=True)

# Disable LLM (use templates only)
agent = AIAgent(use_llm=False)

# Configure via config file
config = {
    "llm": {
        "enabled": True,
        "fallback_to_templates": True,
        "temperature": {
            "decision_reasoning": 0.3,
            "parent_messages": 0.4,
            "child_messages": 0.5
        }
    }
}
agent = AIAgent(config, use_llm=True)
```

### BlackBox API Integration

The system uses BlackBox AI for enhanced capabilities:

```python
from src.utils.blackbox_client import BlackBoxClient

# Direct LLM usage
client = BlackBoxClient()

# Generate enhanced decision reasoning
reasoning = client.generate_decision_reasoning(
    message_content="Inappropriate message",
    threat_type="bullying",
    severity="high",
    child_age=12,
    context={"sender_type": "stranger"}
)

# Generate personalized parent message
parent_msg = client.generate_parent_message(
    child_name="Emma",
    threat_type="bullying",
    severity="high",
    action_taken="Sender blocked",
    tone="urgent"
)
```

## 🎯 Supported Threat Types

The system handles various types of suspicious content:

- **Bullying/Harassment** - Cyberbullying and online harassment
- **Inappropriate Requests** - Requests from strangers or inappropriate contacts
- **Sexual/Violent Content** - Explicit or harmful content
- **Manipulation/Scams** - Attempts to manipulate or defraud
- **Stranger Contact** - Unsolicited contact from unknown individuals

## 🔧 Configuration

### Agent Configuration (`config/agent_config.json`)

```json
{
  "decision_engine": {
    "severity_thresholds": {
      "critical": 0.9,
      "high": 0.7,
      "medium": 0.4,
      "low": 0.0
    },
    "immediate_action_triggers": [
      "sexual_content",
      "violent_content",
      "manipulation"
    ]
  }
}
```

### Educational Content (`config/educational_content.json`)

Contains age-appropriate safety tips, educational modules, and crisis resources.

## 📊 Decision-Making Process

The AI agent follows a structured decision-making process:

1. **Risk Assessment** - Calculates risk score based on multiple factors
2. **Action Selection** - Determines appropriate actions based on threat type and severity
3. **Communication Planning** - Generates targeted messages for stakeholders
4. **Timeline Creation** - Schedules actions based on priority
5. **Follow-up Planning** - Determines if ongoing monitoring is needed

### Risk Factors Considered

- Threat type and severity level
- Child's age and vulnerability
- Sender history and behavior patterns
- Message frequency and context
- Previous incidents involving the child

## 💬 Communication Types

### For Parents
- **Urgent Notifications** - Immediate alerts for high-risk situations
- **Standard Notifications** - Regular updates on incidents
- **Educational Resources** - Guidance on digital safety and communication

### For Children
- **Age-Appropriate Alerts** - Gentle notifications tailored to age group
- **Educational Content** - Safety tips and awareness information
- **Supportive Messages** - Reassurance and guidance

### For Senders
- **Warning Messages** - Firm warnings about inappropriate behavior
- **Educational Information** - Guidelines on acceptable online conduct

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_decision_engine.py

# Run with coverage
python -m pytest tests/ --cov=src
```

## 📈 Monitoring and Auditing

The system includes comprehensive logging and auditing:

- **Decision Tracking** - All decisions are logged with reasoning
- **Communication Logs** - Record of all messages sent
- **Action Execution** - Tracking of action implementation
- **Performance Metrics** - System performance and effectiveness

## 🔒 Privacy and Safety

- **Child Privacy** - Age-appropriate communication that respects privacy
- **Data Protection** - Secure handling of sensitive information
- **Transparency** - Clear reasoning for all decisions and actions
- **Non-Stigmatizing** - Supportive approach that doesn't blame victims

## 📋 Sample Use Cases

### Case 1: Cyberbullying
- **Input**: Bullying message to 14-year-old
- **Actions**: Notify parent, educate child, warn sender, provide resources
- **Communications**: Supportive message to teen, informative alert to parent

### Case 2: Inappropriate Request
- **Input**: Stranger requesting personal meeting with 12-year-old
- **Actions**: Block sender, immediate parent notification, educate child
- **Communications**: Age-appropriate safety reminder, urgent parent alert

### Case 3: Manipulation Attempt
- **Input**: Adult attempting to manipulate vulnerable child
- **Actions**: Block sender, escalate to authorities, comprehensive support
- **Communications**: Crisis resources, immediate intervention

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or support:
- Check the examples in the `examples/` directory
- Review the test cases in `tests/`
- Consult the configuration files in `config/`

## 🔮 Future Enhancements

- Machine learning integration for improved decision-making
- Real-time threat intelligence integration
- Advanced natural language processing for content analysis
- Integration with external safety platforms
- Mobile app for parent notifications
- Dashboard for monitoring and analytics

---

**Note**: This system is designed to work with pre-classified suspicious messages. It focuses on response coordination rather than initial threat detection.
