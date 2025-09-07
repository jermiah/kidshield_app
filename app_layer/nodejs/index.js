require('dotenv').config();
const express = require('express');
const path = require('path');
const app = express();
const axios = require('axios');
const cors = require('cors');
app.use(cors());

let clients = [];

let badMessage = '';

// Helper: add client
function addClient(res) {
  const clientId = Date.now();
  const newClient = { id: clientId, res };
  clients.push(newClient);
  console.log(`👥 Client ${clientId} connected. Total: ${clients.length}`);
  return clientId;
}

// Helper function to broadcast messages to all clients
function broadcastMessage(data) {
  clients.forEach(client => client.write(`data: ${JSON.stringify(data)}\n\n`));
}


// Helper: remove client
function removeClient(id) {
  clients = clients.filter(c => c.id !== id);
  console.log(`❌ Client ${id} disconnected. Total: ${clients.length}`);
}

app.get('/events', (req, res) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  console.log('👥 Client connected to SSE');

  // Keep connection open
  clients.push(res);

  // Clean up when client disconnects
  req.on('close', () => {
    console.log('❌ Client disconnected from SSE');
    clients = clients.filter(client => client !== res);
  });
});

const PORT = process.env.PORT || 3000;
// Set this in your .env and in the Meta "Verify Token" field
const WEBHOOK_VERIFY_TOKEN = process.env.WEBHOOK_VERIFY_TOKEN || 'kid-shield-token';

app.use(express.json());

// Serve static files from frontend directory
app.use(express.static(path.join(__dirname, '../frontend')));

// Serve the main app
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

// Health check
app.get('/health', (_req, res) => res.send('KidShield Backend is running!'));

// API endpoint for sending messages from frontend
app.post('/api/send-message', async (req, res) => {
  try {
    const { to, message } = req.body;
    
    console.log('📤 Sending message to:', to, message);
    
    // Send via WhatsApp if configured
    if (process.env.WHATSAPP_ACCESS_TOKEN && process.env.WHATSAPP_PHONE_NUMBER_ID) {
      const result = await sendWhatsAppText(to, message);
      console.log('✅ WhatsApp message sent:', result);
    }
    
    res.json({ success: true, message: 'Message sent successfully' });
  } catch (error) {
    console.error('❌ Error sending message:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// API endpoint to get conversations (for frontend)
app.get('/api/conversations', (req, res) => {
  // In a real app, this would fetch from a database
  const conversations = [
    {
      id: '919952072184',
      name: 'Emma (Child)',
      lastMessage: 'Hi mom, how are you?',
      time: '2 min ago',
      unread: 0,
      status: 'safe'
    },
    {
      id: '918765432109',
      name: 'Unknown Contact',
      lastMessage: 'Hey, want to be friends?',
      time: '5 min ago',
      unread: 1,
      status: 'warning'
    }
  ];
  
  res.json(conversations);
});

// API endpoint to simulate receiving a message (for testing)
app.post('/api/simulate-message', async (req, res) => {
  try {
    const { from, message } = req.body;
    
    console.log('🧪 Simulating message from:', from, message);
    
    // Analyze with Guardian Layer
    const analysisResult = await analyzeMessageWithGuardian(message, from);
    
    res.json({
      success: true,
      message: 'Message processed',
      analysis: analysisResult
    });
  } catch (error) {
    console.error('❌ Error processing simulated message:', error);
    res.status(500).json({ success: false, error: error.message });
  }
});

// Webhook verification (GET)
app.get('/webhook', (req, res) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode && token) {
    if (mode === 'subscribe' && token === WEBHOOK_VERIFY_TOKEN) {
      console.log('✅ WEBHOOK_VERIFIED');
      // Must echo challenge exactly as provided
      return res.status(200).send(challenge);
    }
    return res.sendStatus(403);
  }
  return res.sendStatus(400);
});

async function sendWhatsAppText(to, text) {
  const url = `https://graph.facebook.com/v21.0/${process.env.PHONE_NUMBER_ID}/messages`;

  const payload = {
    messaging_product: 'whatsapp',
    to: to,   // e.g., 15551234567 (international format, digits only)
    type: 'text',
    text: { body: text }
  };

  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`
  };

  const { data } = await axios.post(url, payload, { headers });
  return data;
}

async function analyzeMessageWithGuardian(messageText, userId) {
  try {
    console.log('🛡️ Analyzing message with Guardian Layer:', messageText);

    const response = await axios.post('http://localhost:8000/guardian/auto-analyze', {
      content: messageText,
      user_id: userId
    });

    broadcastMessage(response.data, messageText);

    return { ...response.data, text: messageText };
  } catch (error) {
    console.error('❌ Error analyzing message with Guardian Layer:', error.message);
    return null;
  }
}

async function applyAgentActions(actionData, originalMessage, senderId) {
  console.log('🤖 Applying agent actions:', actionData);
  
  if (!actionData || !actionData.data || !actionData.data.messages) {
    return;
  }

  // Process each message from the agent layer
  for (const msg of actionData.data.messages) {
    console.log(`📧 Processing ${msg.recipient} message: ${msg.subject}`);
    
    try {
      switch (msg.recipient) {
        case 'parent':
          // Send notification to parent
          await sendParentNotification(msg, senderId);
          break;
          
        case 'child':
          // Send educational content to child
          await sendChildEducation(msg, senderId);
          break;
          
        case 'sender':
          // Send warning to sender
          await sendSenderWarning(msg, senderId);
          break;
      }
    } catch (error) {
      console.error(`❌ Error sending ${msg.recipient} message:`, error);
    }
  }
}

async function sendParentNotification(message, childId) {
  console.log('👨‍👩‍👧 Sending parent notification:', message.subject);
  
  // In a real app, this would send email/SMS to parent
  // For demo, we'll send a WhatsApp message if parent number is configured
  const parentNumber = process.env.PARENT_PHONE_NUMBER;
  
  if (parentNumber && process.env.WHATSAPP_ACCESS_TOKEN) {
    const notificationText = `🛡️ KIDSHIELD ALERT\n\n${message.subject}\n\n${message.message}`;
    try {
      await sendWhatsAppText(parentNumber, notificationText);
      console.log('✅ Parent notification sent via WhatsApp');
    } catch (error) {
      console.error('❌ Failed to send parent notification:', error);
    }
  }
}

async function sendChildEducation(message, childId) {
  console.log('📚 Sending child education:', message.subject);
  
  // Send educational content to the child
  if (process.env.WHATSAPP_ACCESS_TOKEN) {
    const educationText = `📚 ${message.subject}\n\n${message.message}`;
    try {
      await sendWhatsAppText(childId, educationText);
      console.log('✅ Child education sent via WhatsApp');
    } catch (error) {
      console.error('❌ Failed to send child education:', error);
    }
  }
}

async function sendSenderWarning(message, senderId) {
  console.log('⚠️ Sending sender warning:', message.subject);
  
  // Send warning to the sender
  if (process.env.WHATSAPP_ACCESS_TOKEN) {
    const warningText = `⚠️ ${message.subject}\n\n${message.message}`;
    try {
      await sendWhatsAppText(senderId, warningText);
      console.log('✅ Sender warning sent via WhatsApp');
    } catch (error) {
      console.error('❌ Failed to send sender warning:', error);
    }
  }
}

app.get('/send-template', async (req, res) => {
  try {
    // read and trim envs (avoid trailing spaces/newlines)
    const PHONE_NUMBER_ID = (process.env.WHATSAPP_PHONE_NUMBER_ID || '').trim();
    const ACCESS_TOKEN = (process.env.WHATSAPP_ACCESS_TOKEN || '').trim();

    // quick sanity (masked)
    console.log('Env check:', {
      tokenPresent: !!ACCESS_TOKEN,
      tokenLen: ACCESS_TOKEN.length,
      phoneId: PHONE_NUMBER_ID
    });

    const url = `https://graph.facebook.com/v21.0/${PHONE_NUMBER_ID}/messages`;
    const payload = {
      messaging_product: 'whatsapp',
      to: '919952072184',
      type: 'template',
      template: { name: 'hello_world', language: { code: 'en_US' } }
    };
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${ACCESS_TOKEN}` // ✅ use the correct env var
    };

    const { data } = await axios.post(url, payload, { headers });
    res.json(data);
  } catch (err) {
    const status = err?.response?.status;
    const data = err?.response?.data;
    console.error('❌ Template send error:', status, data || err.message);
    res.status(500).json({ status, ...(data || { error: err.message }) });
  }
});

app.get('/send', async (req, res) => {
  try {
    const text = req.query.text || 'Hello from Express + WhatsApp 🚀';
    const to = req.query.to || '919952072184';   // allow dynamic recipient
    const check = req.query.check === 'true';   // check mode: analyze without sending

    // Analyze message for bad words using Guardian Layer
    const analysisResult = await analyzeMessageWithGuardian(text, to);

    if (analysisResult && analysisResult.success && analysisResult.data.action_types && analysisResult.data.action_types.length > 0) {
      console.log('⚠️ Bad word detected in message:', text);
      return res.json({
        success: false,
        message: 'Bad word detected. Message not sent.',
        actions: analysisResult.data
      });
    }

    if (check) {
      // In check mode, don't send, just return success
      console.log('✅ Message checked, no bad words:', text);
      return res.json({ success: true, message: 'Message is safe' });
    }

    const url = `https://graph.facebook.com/v21.0/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`;
    const payload = {
      messaging_product: 'whatsapp',
      to: to,
      type: 'text',
      text: { body: text }
    };
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`  // ✅ correct token
    };

    const { data } = await axios.post(url, payload, { headers });
    console.log('✅ Sent message:', data);
    res.json({ success: true, message: 'Message sent successfully', data });
  } catch (err) {
    const status = err?.response?.status;
    const data = err?.response?.data;
    console.error('❌ Send error:', status, data || err.message);
    res.status(500).json({ status, ...(data || { error: err.message }) });
  }
});

// Webhook events (POST)
app.post('/webhook', async (req, res) => {
  const body = req.body;

  // Acknowledge quickly
  res.status(200).send('EVENT_RECEIVED');

  try {
    if (!body || !body.entry || !body.entry[0]?.changes) {
      console.warn('⚠️ Unexpected body:', JSON.stringify(body));
      return;
    }

    const change = body.entry[0].changes[0];
    const value = change.value || {};
    const field = change.field;

    console.log('📩 Field:', field);

    // Messages (inbound user messages)
    if (value.messages && value.messages.length > 0) {
      const msg = value.messages[0];
      const from = msg.from;
      const type = msg.type;
      const text = msg.text?.body;
      console.log('✅ Received message:', { from, type, text });

      // ✅ Broadcast to all connected frontends
      if (text) {
        try {
          const analysisResult = await analyzeMessageWithGuardian(text, from);
          if (analysisResult?.success) {
            const actionData = analysisResult.data;
            if (actionData.action_types?.length > 0) {
              // broadcastMessage({ from, text, type, timestamp: Date.now()});
              console.log('⚠️ Suspicious message detected! Actions:', actionData.action_types);
              await applyAgentActions(analysisResult, text, from);
              console.log('✅ All safety actions have been applied');
            } else {
              console.log('✅ Message is safe - no actions needed');
            }
          }
        } catch (error) {
          console.error('❌ Error processing message:', error.message);
        }
      }
      return;
    }

    if (value.statuses && value.statuses.length > 0) {
      console.log('ℹ️ Status update:', value.statuses[0]);
      return;
    }

    console.log('ℹ️ Other change value:', value);
  } catch (e) {
    console.error('❌ Error handling webhook:', e);
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
