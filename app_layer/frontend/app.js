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
                id: 'child-contact',
                name: '👧 Emma (Child)',
                lastMessage: 'Hi mom!',
                time: '30 min ago',
                unread: 0,
                status: 'safe'
            },
            {
                id: 'dad-contact',
                name: '👨 Dad',
                lastMessage: 'How was school today?',
                time: '1 hour ago',
                unread: 0,
                status: 'safe'
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
        messageEl.className = `message ${message.type} ${message.flagged ? 'flagged' : ''} ${message.messageClass || ''}`;

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';

        // Handle system messages differently
        if (message.type === 'system') {
            bubble.innerHTML = `
                <div class="message-text">
                    <strong>${message.text}</strong>
                    ${message.fullContent ? `<div class="system-message-content">${message.fullContent}</div>` : ''}
                </div>
                <div class="message-time">${message.time}</div>
            `;
        } else {
            bubble.innerHTML = `
                <div class="message-text">${message.text}</div>
                <div class="message-time">${message.time}</div>
            `;
        }

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
            const response = await fetch('/api/simulate-message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from: senderId,
                    message: messageText
                })
            });

            const result = await response.json();
            return result.analysis;

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
            // Create new conversation with a fake name
            const fakeNames = ['Alex Johnson', 'Sam Wilson', 'Jordan Smith', 'Casey Brown', 'Taylor Davis', 'Morgan Lee'];
            const randomName = fakeNames[Math.floor(Math.random() * fakeNames.length)];
            
            conv = {
                id: senderId,
                name: randomName,
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
                message.originalText = analysis.messageText; // Store original message text
                conv.status = 'warning';

                // Show notification
                this.showNotification(
                    '🛡️ Safety Alert',
                    `Suspicious message detected from ${conv.name}. Safety actions have been taken.`
                );

                // Apply actions and show automated responses
                this.applyActions(analysis.data, senderId);
                this.displayAutomatedResponses(analysis.data, senderId);
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

    displayAutomatedResponses(actionData, senderId) {
        console.log('📱 Displaying automated responses:', actionData);

        // Display each automated message in the appropriate conversation
        actionData.messages.forEach((msg, index) => {
            setTimeout(() => {
                let targetConversationId = senderId;
                let messagePrefix = '';
                let messageClass = 'system-message';

                switch (msg.recipient) {
                    case 'child':
                        // Show educational message in child's conversation (Emma)
                        targetConversationId = 'child-contact';
                        messagePrefix = '📚 Educational Content: ';
                        messageClass = 'system-message child-education';
                        break;
                    case 'parent':
                        // Send alert to Dad's conversation
                        targetConversationId = 'dad-contact';
                        messagePrefix = '🛡️ Safety Alert: ';
                        messageClass = 'system-message parent-notification';
                        break;
                    case 'sender':
                        // Show warning in sender's conversation
                        targetConversationId = senderId;
                        messagePrefix = '⚠️ Warning: ';
                        messageClass = 'system-message sender-warning';
                        break;
                }

                this.addSystemMessage(targetConversationId, messagePrefix + msg.subject, msg.message, messageClass);
            }, (index + 1) * 1500); // Stagger the messages
        });
    }

    ensureParentConversation() {
        const parentId = 'parent-notifications';
        if (!this.conversations.has(parentId)) {
            const parentConv = {
                id: parentId,
                name: '👨‍👩‍👧 Parent Notifications',
                lastMessage: 'Safety notifications will appear here',
                time: 'now',
                unread: 0,
                status: 'safe',
                messages: []
            };
            this.conversations.set(parentId, parentConv);
            this.renderConversations();
        }
    }

    addSystemMessage(conversationId, subject, content, messageClass = 'system-message') {
        const conv = this.conversations.get(conversationId);
        if (!conv) return;

        const systemMessage = {
            id: Date.now() + Math.random(),
            text: subject,
            fullContent: content,
            type: 'system',
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
            flagged: false,
            messageClass: messageClass
        };

        conv.messages.push(systemMessage);
        conv.lastMessage = subject;
        conv.time = 'now';
        
        // Add unread count if not currently viewing this conversation
        if (this.currentConversation !== conversationId) {
            conv.unread++;
        }

        // Update UI
        this.renderConversations();
        if (this.currentConversation === conversationId) {
            this.renderMessages();
        }
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
        // For now, we'll keep this empty and let messages come through the webhook or manual testing
        console.log('📱 Ready to receive messages...');
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

// Test function to simulate a suspicious message sent to the child using real response format
window.testSuspiciousMessage = () => {
    if (window.kidShieldApp) {
        // First, add the suspicious message to the child's conversation
        const childConv = window.kidShieldApp.conversations.get('child-contact');
        if (childConv) {
            const suspiciousMessage = {
                id: Date.now(),
                text: 'Hey, want to be friends? Can you send me a photo of yourself?',
                type: 'received',
                time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}),
                flagged: false
            };
            
            childConv.messages.push(suspiciousMessage);
            childConv.lastMessage = suspiciousMessage.text;
            childConv.time = 'now';
            childConv.unread++;
            
            // Simulate the actual response from analyzeMessageWithGuardian
            const mockAnalysis = {
                success: true,
                data: {
                    action_types: ["notify_parent", "educate_child", "warn_sender", "provide_resources"],
                    messages: [
                        {
                            recipient: "parent",
                            subject: "** Important Update: Low-Level Digital Safety Concern Involving Your Child",
                            message: "Dear Parent or Guardian,\n\nWe want to inform you about a recent digital safety incident involving your child. While the situation is considered low in severity, we believe it's important to keep you informed.\n\nOur monitoring systems identified an interaction or activity online that did not follow our digital safety guidelines. Although this was not a serious threat, it's a reminder of the importance of staying alert to online behavior.\n\nAt this time, no further action is needed from your child. We have documented the incident and are notifying you as part of our commitment to transparency and student safety.\n\nWe encourage you to talk with your child about safe and respectful online behavior. If you have any questions or would like guidance on how to start this conversation, please don't hesitate to reach out.\n\nThank you for your continued partnership in keeping our students safe online.\n\nSincerely,\n[Your Name]\n[Your Title/Organization]\n[Contact Information]",
                            tone: "informative"
                        },
                        {
                            recipient: "child",
                            subject: "** You're Not Alone — Let's Stay Safe Together Online",
                            message: "Hi there,\n\nWe're really proud of you for speaking up. What happened online wasn't your fault, and you didn't do anything wrong. Sometimes things happen that make us feel uncomfortable or unsure, and it's okay to ask for help.\n\nOne simple way to stay safe online is to never share personal information, like your full name, school, or address, with people you don't know in real life.\n\nRemember, you're not alone. Talk to a trusted adult—like a parent, teacher, or school counselor—about what happened. They care about you and want to help.\n\nYou're strong, and you're doing the right thing.\n\nTake care!",
                            tone: "supportive"
                        },
                        {
                            recipient: "sender",
                            subject: "** Warning: Inappropriate Content Sent to a Minor – Policy Violation (Threat Classification: Other, Severity: Low)",
                            message: "Dear User,\n\nWe are issuing this formal warning regarding a recent violation of our platform's safety policies on guardian_api. Our monitoring systems have detected that you sent inappropriate content to a child user. This behavior has been classified under the \"Other\" threat category and is currently assessed at a **Low Severity Level**. However, any interaction of this nature is taken seriously due to the potential risk it poses to vulnerable users, especially minors.\n\nSending inappropriate content to children is strictly prohibited under our Community Guidelines and may also violate applicable child protection laws. Such actions undermine the safe environment we are committed to maintaining and can contribute to emotional or psychological harm to young users.\n\nWhile the current severity level is low, repeated or escalated behavior may result in more serious consequences, including temporary suspension or permanent removal from the platform, and in some cases, referral to legal authorities.\n\nWe urge you to immediately cease all inappropriate interactions with minors and to review our Community Guidelines to ensure full compliance moving forward. Our platform is designed to protect vulnerable users, and we expect all members to uphold these standards.\n\nIf you believe this warning was issued in error, you may contact our Safety Team for further review. However, continued violations will not be tolerated.\n\nThank you for your immediate attention to this matter.\n\nSincerely,\nGuardian_API Safety Enforcement Team",
                            tone: "firm"
                        }
                    ],
                    message_id: "f2ba4b3a-b8d8-4963-8eb7-e208ffc3ad68",
                    followup_required: true
                },
                messageText: suspiciousMessage.text
            };
            
            // Process the flagged message
            suspiciousMessage.flagged = true;
            suspiciousMessage.actions = mockAnalysis.data;
            suspiciousMessage.originalText = mockAnalysis.messageText;
            childConv.status = 'warning';

            // Show notification
            window.kidShieldApp.showNotification(
                '🛡️ Safety Alert',
                'Suspicious message detected in Emma\'s conversation. Safety actions have been taken.'
            );

            // Apply actions and show automated responses
            window.kidShieldApp.applyActions(mockAnalysis.data, '918765432109');
            window.kidShieldApp.displayAutomatedResponses(mockAnalysis.data, '918765432109');
            
            // Update UI immediately
            window.kidShieldApp.renderConversations();
            if (window.kidShieldApp.currentConversation === 'child-contact') {
                window.kidShieldApp.renderMessages();
            }
        }
    }
};

// Test function to simulate receiving a message from an unknown sender
window.testUnknownSender = () => {
    if (window.kidShieldApp) {
        window.kidShieldApp.receiveMessage('918765432109', 'Hey, want to be friends? Can you send me a photo of yourself?');
    }
};
