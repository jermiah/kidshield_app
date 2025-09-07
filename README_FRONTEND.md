# KidShield - Complete Messaging Safety System

A Beeper-like messaging interface with AI-powered safety monitoring that automatically detects threats and takes protective actions.

## 🚀 System Overview

The system consists of three integrated layers:

1. **Guardian Layer** (Python) - AI content analysis and threat detection
2. **Agent Layer** (Python) - Decision making and action planning  
3. **App Layer** (Node.js + Frontend) - Messaging interface and action execution

## 🛡️ Enhanced Features

### Agent Layer Enhancements
- **Guaranteed 3 Actions**: For any detected risk, the system now ensures these actions:
  - 🚨 **Alert Parents** - Immediate notification to parents
  - 📚 **Educate Child** - Age-appropriate safety education
  - ⚠️ **Warn Sender** - Warning with specific threat classification

### Simplified API Response
The `/guardian/auto-analyze` endpoint now returns only essential information:
```json
{
  "success": true,
  "data": {
    "action_types": ["notify_parent", "educate_child", "warn_sender"],
    "messages": [
      {
        "recipient": "parent",
        "subject": "HIGH Warning: Bullying Content Detected",
        "message": "Your child received a bullying message...",
        "tone": "urgent"
      }
    ],
    "message_id": "msg_123",
    "followup_required": true
  },
  "message": "Actions planned and messages generated"
}
```

## 🏃‍♂️ Quick Start

### 1. Start the Guardian Layer (Python)
```bash
cd guardian_layer
python -m uvicorn api.guardian_api:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start the App Layer (Node.js)
```bash
cd app_layer/nodejs
npm install
node index.js
```

### 3. Open the Frontend
Navigate to: `http://localhost:3000`

## 🎯 How It Works

### Message Flow
1. **Message Received** → WhatsApp webhook or frontend interface
2. **Guardian Analysis** → AI analyzes content for threats
3. **Agent Decision** → If threats detected, plans 3 required actions
4. **Action Execution** → Sends notifications, education, and warnings
5. **Frontend Display** → Shows original message + actions taken

### Frontend Features
- **Beeper-like Interface** - Modern messaging UI
- **Real-time Safety Monitoring** - Live threat detection
- **Action Visualization** - Shows what actions were taken
- **Multi-conversation Support** - Handle multiple contacts
- **Safety Notifications** - Alerts for parents and administrators

## 🧪 Testing the System

### Test with Frontend
1. Open `http://localhost:3000`
2. Select a conversation
3. Type a suspicious message like: "Can you send me a photo?"
4. Watch the system detect threats and apply actions

### Test with API
```bash
# Send a suspicious message
curl -X POST http://localhost:8000/guardian/auto-analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "Hey kid, want to be friends?", "user_id": "test_user"}'
```

### Test WhatsApp Integration
```bash
# Simulate receiving a message
curl -X POST http://localhost:3000/api/simulate-message \
  -H "Content-Type: application/json" \
  -d '{"from": "918765432109", "message": "Can you send me your photo?"}'
```

## 🔧 Configuration

### Environment Variables (.env)
```env
# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_id_here
PARENT_PHONE_NUMBER=parent_number_here

# Webhook
WEBHOOK_VERIFY_TOKEN=kid-shield-token

# Server
PORT=3000
```

## 📱 Frontend Interface

### Main Features
- **Conversation List** - Shows all active conversations with safety status
- **Message Display** - Original messages with threat indicators
- **Action Panels** - Visual display of safety actions taken
- **Real-time Updates** - Live notifications and status updates
- **Safety Indicators** - Color-coded threat levels

### Safety Actions Display
When a threat is detected, the interface shows:
- 🛡️ **Actions Taken** panel
- 👨‍👩‍👧 **Parent Notification** - "Parents have been notified"
- 📚 **Child Education** - "Educational content provided"  
- ⚠️ **Sender Warning** - "Sender has been warned"

## 🔍 System Integration

### Guardian Layer → Agent Layer
- Guardian detects threats and severity
- Agent plans appropriate response actions
- Enhanced decision engine ensures 3 required actions

### Agent Layer → App Layer  
- Agent generates specific messages for each recipient
- App layer executes actions (WhatsApp, email, etc.)
- Frontend displays actions taken

### Real-time Communication
- WebSocket connections for live updates
- Webhook integration for WhatsApp messages
- API endpoints for frontend communication

## 🛠️ Development

### Adding New Threat Types
1. Update `ThreatType` enum in `agent_layer/models/message.py`
2. Add handling in `agent_layer/decision_engine/decision_engine.py`
3. Update message templates in `agent_layer/communication/message_generator.py`

### Customizing Actions
1. Modify `_determine_communication_actions()` in decision engine
2. Update message generation templates
3. Add new action execution in Node.js backend

## 🚨 Safety Features

- **Automatic Threat Detection** - AI-powered content analysis
- **Guaranteed Response** - Always takes protective actions
- **Multi-channel Notifications** - WhatsApp, email, SMS support
- **Age-appropriate Education** - Tailored safety content
- **Sender Accountability** - Warnings with threat classification
- **Parent Involvement** - Immediate notifications for guardians

## 📊 Monitoring

The system provides comprehensive logging:
- Message analysis results
- Actions taken and their outcomes
- System performance metrics
- Safety incident reports

## 🔒 Privacy & Security

- Messages analyzed locally (no external AI services by default)
- Minimal data retention
- Encrypted communications
- Parental consent mechanisms
- GDPR/COPPA compliance considerations

---

**🎉 The system is now complete with guaranteed 3-action response and simplified API format!**
