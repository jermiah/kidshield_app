class KidShieldApp {
    constructor() {
        this.conversations = new Map();
        this.currentConversation = null;
        this.socket = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadConversations();
    }

    setupEventListeners() {
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');

        // Send message on button click
        sendButton.addEventListener('click', () => this.sendMessage());

        // Send message on Enter key
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });

        // Auto-resize input
        messageInput.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        });
    }

    connectWebSocket() {
        // In a real app, this would connect to a WebSocket server
        // For demo purposes, we'll simulate real-time updates
        console.log('🔌 Connecting to WebSocket...');
        
        // Simulate receiving messages periodically for demo
        this.simulateIncomingMessages();
    }

    loadConversations() {
        // Load existing conversations (in real app, from API)
        const demoConversations = [
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

        demoConversations.forEach(conv => {
            this.conversations.set(conv.id, {
                ...conv,
                messages: []
            });
        });

        this.renderConversations();
    }

    renderConversations() {
        const container = document.getElementById('conversations');
        container.innerHTML = '';

        this.conversations.forEach((conv, id) => {
            const item = document.createElement('div');
            item.className = `conversation-item ${this.currentConversation === id ? 'active' : ''}`;
            item.onclick = () => this.selectConversation(id);

            const statusClass = conv.status === 'safe' ? 'status-safe' : 
                               conv.status === 'warning' ? 'status-warning' : 'status-danger';

            item.innerHTML = `
                <div class="conversation-time">${conv.time}</div>
                <div class="conversation-name">
                    <span class="status-indicator ${statusClass}"></span>
                    ${conv.name}
                    ${conv.unread > 0 ? `<span style="background: #f44336; color: white; border-radius: 10px; padding: 2px 6px; font-size: 12px; margin-left: 5px;">${conv.unread}</span>` : ''}
                </div>
                <div class="conversation-preview">${conv.lastMessage}</div>
            `;

            container.appendChild(item);
        });
    }

    selectConversation(conversationId) {
        this.currentConversation = conversationId;
        const conv = this.conversations.get(conversationId);
        
        // Update UI
        document.getElementById('chatTitle').textContent = conv.name;
        document.getElementById('messageInput').disabled = false;
        document.getElementById('sendButton').disabled = false;
        
        // Mark as read
        conv.unread = 0;
        
        this.renderConversations();
        this.renderMessages();
    }

    renderMessages() {
        const container = document.getElementById('messagesContainer');
        const conv = this.conversations.get(this.currentConversation);
        
        if (!conv) return;

        container.innerHTML = '';

        conv.messages.forEach(message => {
            const messageEl = this.createMessageElement(message);
            container.appendChild(messageEl);
        });

        // Scroll to bottom
        container.scrollTop = container.scrollHeight;
    }

    createMessageElement(message) {
        const messageEl = document.createElement('div');
        messageEl.className = `message ${message.type} ${message.flagged ? 'flagged' : ''}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        bubble.innerHTML = `
            <div class="message-text">${message.text}</div>
            <div class="message-time">${message.time}</div>
        `;

        messageEl.appendChild(bubble);

        // Add actions if message was flagged
        if (message.flagged && message.actions) {
            const actionsEl = this.createActionsElement(message.actions);
            messageEl.appendChild(actionsEl);
        }

        return messageEl;
    }

    createActionsElement(actions) {
        const actionsEl = document.createElement('div');
        actionsEl.className = 'message-actions';

        const title = document.createElement('div');
        title.style.fontWeight = '600';
        title.style.marginBottom = '10px';
        title.textContent = '🛡️ Safety Actions Taken:';
        actionsEl.appendChild(title);

        actions.action_types.forEach(actionType => {
            const actionEl = document.createElement('div');
            actionEl.className = 'action-item';

            const icon = document.createElement('div');
            icon.className = 'action-icon';
            
            let iconText = '';
            let iconClass = '';
            let actionText = '';

            switch(actionType) {
                case 'notify_parent':
                    iconText = '👨‍👩‍👧';
                    iconClass = 'parent';
                    actionText = 'Parents have been notified';
                    break;
                case 'educate_child':
                    iconText = '📚';
                    iconClass = 'child';
                    actionText = 'Educational content provided';
                    break;
                case 'warn_sender':
                    iconText = '⚠️';
                    iconClass = 'sender';
                    actionText = 'Sender has been warned';
                    break;
                default:
                    iconText = '🔧';
                    iconClass = 'sender';
                    actionText = actionType.replace('_', ' ');
            }

            icon.className += ` ${iconClass}`;
            icon.textContent = iconText;

            const text = document.createElement('span');
            text.textContent = actionText;

            actionEl.appendChild(icon);
            actionEl.appendChild(text);
            actionsEl.appendChild(actionEl);
        });

        return actionsEl;
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const text = input.value.trim();
        
        if (!text || !this.currentConversation) return;

        // Add message to UI immediately
        const message = {
            id: Date.now(),
            text: text,
            type: 'sent',
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            flagged: false
        };

        const conv = this.conversations.get(this.currentConversation);
        conv.messages.push(message);
        conv.lastMessage = text;
        conv.time = 'now';

        // Clear input
        input.value = '';

        // Update UI
        this.renderConversations();
        this.renderMessages();

        // Send to backend for analysis
        try {
            const response = await fetch('http://localhost:3000/api/send-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    to: this.currentConversation,
                    message: text
                })
            });

            const result = await response.json();
            console.log('📤 Message sent:', result);

        } catch (error) {
            console.error('❌ Error sending message:', error);
            this.showNotification('Error', 'Failed to send message');
        }
    }

    async analyzeMessage(messageText, senderId) {
        try {
            const response = await fetch('http://localhost:8000/guardian/auto-analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    content: messageText,
                    user_id: senderId
                })
            });

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('❌ Error analyzing message:', error);
            return null;
        }
    }

    receiveMessage(senderId, messageText) {
        console.log('📨 Received message from:', senderId, messageText);

        // Add message to conversation
        let conv = this.conversations.get(senderId);
        if (!conv) {
            // Create new conversation
            conv = {
                id: senderId,
                name: `Contact ${senderId.slice(-4)}`,
                lastMessage: messageText,
                time: 'now',
                unread: 1,
                status: 'safe',
                messages: []
            };
            this.conversations.set(senderId, conv);
        }

        const message = {
            id: Date.now(),
            text: messageText,
            type: 'received',
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            flagged: false
        };

        conv.messages.push(message);
        conv.lastMessage = messageText;
        conv.time = 'now';
        conv.unread++;

        // Analyze message for safety
        this.analyzeMessage(messageText, senderId).then(analysis => {
            if (analysis && analysis.success && analysis.data.action_types.length > 0) {
                // Message was flagged
                message.flagged = true;
                message.actions = analysis.data;
                conv.status = 'warning';

                // Show notification
                this.showNotification(
                    '🛡️ Safety Alert',
                    `Suspicious message detected from ${conv.name}. Safety actions have been taken.`
                );

                // Apply actions
                this.applyActions(analysis.data, senderId);
            }

            // Update UI
            this.renderConversations();
            if (this.currentConversation === senderId) {
                this.renderMessages();
            }
        });

        // Update UI immediately
        this.renderConversations();
        if (this.currentConversation === senderId) {
            this.renderMessages();
        }
    }

    applyActions(actionData, senderId) {
        console.log('🔧 Applying actions:', actionData);

        // Send messages based on actions
        actionData.messages.forEach(msg => {
            console.log(`📧 Sending ${msg.recipient} message:`, msg.subject);
            
            // In a real app, these would be sent via email, SMS, etc.
            // For demo, we'll show them as notifications
            setTimeout(() => {
                this.showNotification(
                    `Message to ${msg.recipient}`,
                    `${msg.subject}: ${msg.message.substring(0, 100)}...`
                );
            }, 1000);
        });
    }

    showNotification(title, message) {
        const panel = document.getElementById('notificationPanel');
        const titleEl = document.getElementById('notificationTitle');
        const messageEl = document.getElementById('notificationMessage');

        titleEl.textContent = title;
        messageEl.textContent = message;

        panel.classList.add('show');

        // Auto-hide after 5 seconds
        setTimeout(() => {
            panel.classList.remove('show');
        }, 5000);
    }

    simulateIncomingMessages() {
        // Simulate receiving messages for demo purposes
        const demoMessages = [
            { from: '918765432109', text: 'Hey, want to be friends?', delay: 3000 },
            { from: '918765432109', text: 'Can you send me a photo of yourself?', delay: 8000 },
            { from: '919952072184', text: 'Mom, someone is bothering me online', delay: 15000 }
        ];

        demoMessages.forEach(msg => {
            setTimeout(() => {
                this.receiveMessage(msg.from, msg.text);
            }, msg.delay);
        });
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.kidShieldApp = new KidShieldApp();
    console.log('🚀 KidShield App initialized');
});

// Expose functions for testing
window.testReceiveMessage = (from, text) => {
    if (window.kidShieldApp) {
        window.kidShieldApp.receiveMessage(from, text);
    }
};
