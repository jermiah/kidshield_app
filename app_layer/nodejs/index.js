require('dotenv').config();
const express = require('express');
const app = express();
const axios = require('axios');

const PORT = process.env.PORT || 3000;
// Set this in your .env and in the Meta "Verify Token" field
const WEBHOOK_VERIFY_TOKEN = process.env.WEBHOOK_VERIFY_TOKEN || 'kid-shield-token';

app.use(express.json());

// Health check
app.get('/', (_req, res) => res.send('Hello, Thamim!'));

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

    const url = `https://graph.facebook.com/v21.0/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`;
    const payload = {
      messaging_product: 'whatsapp',
      to: '919952072184',   // fixed recipient
      type: 'text',
      text: { body: text }
    };
    const headers = {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${process.env.WHATSAPP_ACCESS_TOKEN}`  // ✅ correct token
    };

    const { data } = await axios.post(url, payload, { headers });
    console.log('✅ Sent message:', data);
    res.json(data);
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

  // Always acknowledge quickly
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
      const from = msg.from;              // WhatsApp user phone number
      const type = msg.type;              // text, image, etc.
      const text = msg.text?.body;
      console.log('✅ Received message:', { from, type, text, msg});

      // Send message to Guardian Layer for analysis using simple format
      if (text) {
        try {
          const guardianResponse = await axios.post('http://localhost:8000/guardian/auto-analyze', {
            content: text,
            user_id: from
          });

          console.log('🛡️ Guardian Layer Analysis:', guardianResponse.data);

          // Check if message is safe or contains threats
          const analysisResult = guardianResponse.data.data;
          if (analysisResult && analysisResult.status) {
            if (analysisResult.status.value === 'safe') {
              console.log('✅ Message is safe');
              // Could send a confirmation or just log
            } else {
              console.log('⚠️ Message contains threats:', analysisResult.status.value);
              // Could send warning message or take action
              await sendWhatsAppText(from, '⚠️ This message has been flagged for review by our safety system.');
            }
          }
        } catch (error) {
          console.error('❌ Error analyzing message with Guardian Layer:', error.message);
        }
      }

      return;
    }

    // Status updates (message delivery/read receipts)
    if (value.statuses && value.statuses.length > 0) {
      console.log('ℹ️ Status update:', value.statuses[0]);
      return;
    }

    // Other webhook deliveries (e.g., template, errors)
    console.log('ℹ️ Other change value:', value);
  } catch (e) {
    console.error('❌ Error handling webhook:', e);
  }
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
