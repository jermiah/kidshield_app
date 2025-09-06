"""
Main API for KidShield App Layer
Handles user interactions and coordinates with Guardian and Agent layers
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
from datetime import datetime
import sys
from pathlib import Path
import logging

# Add paths for layer imports
app_root = Path(__file__).parent.parent.parent
sys.path.append(str(app_root / "guardian_layer"))
sys.path.append(str(app_root / "agent_layer"))

# Import Guardian Layer
from guardian_layer.api.guardian_api import GuardianAPI
from guardian_layer.models import InputMessage

# Import Agent Layer
from agent_layer.integrations.guardian_integration import convert_guardian_to_kidshield
from agent_layer.agents.ai_agent import AIAgent
from agent_layer.models.message import ChildProfile

# Import App Layer models
from ..models.user_models import Parent, Child, MessageRequest

app = Flask(__name__)
app.secret_key = 'kidshield_secret_key_change_in_production'
CORS(app)

# Initialize components
guardian_api = GuardianAPI()
ai_agent = AIAgent(use_llm=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'layers': {
            'app_layer': 'active',
            'guardian_layer': 'active',
            'agent_layer': 'active'
        }
    })

@app.route('/api/analyze-message', methods=['POST'])
def analyze_message():
    """
    Main endpoint for analyzing messages through the three-layer system
    Flow: App Layer → Guardian Layer → Agent Layer → App Layer
    """
    try:
        # Parse request
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['content', 'child_id', 'sender_info']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # Step 1: Create Guardian Layer input
        guardian_input = InputMessage(
            message_id=f"app_{datetime.now().timestamp()}",
            text=data.get('content'),
            image_data=data.get('image_data'),
            user_id=data['child_id']
        )
        
        # Step 2: Send to Guardian Layer for analysis
        logger.info(f"Sending message to Guardian Layer: {guardian_input.message_id}")
        guardian_response = guardian_api.analyze_content(guardian_input)
        
        # Step 3: Convert Guardian response to Agent Layer format
        child_profile = ChildProfile(
            child_id=data['child_id'],
            age=data.get('child_age', 12),
            name=data.get('child_name', 'Child'),
            grade_level=data.get('grade_level'),
            previous_incidents=data.get('previous_incidents', 0)
        )
        
        additional_metadata = {
            'sender_id': data['sender_info'].get('sender_id', 'unknown'),
            'sender_type': data['sender_info'].get('sender_type', 'unknown'),
            'platform': data.get('platform', 'unknown'),
            'message_frequency': data.get('message_frequency', 1)
        }
        
        suspicious_message = convert_guardian_to_kidshield(
            guardian_response,
            data['content'],
            child_profile,
            additional_metadata
        )
        
        # Step 4: Process with Agent Layer
        logger.info(f"Processing with Agent Layer: {suspicious_message.message_id}")
        action_plan = ai_agent.process_suspicious_message(suspicious_message)
        
        # Step 5: Format response for App Layer
        response = {
            'message_id': suspicious_message.message_id,
            'analysis_result': {
                'threat_type': suspicious_message.threat_type.value,
                'severity': suspicious_message.severity.value,
                'risk_score': guardian_response.get('risk_score', 0),
                'guardian_status': guardian_response.get('status', 'unknown')
            },
            'actions_taken': {
                'total_actions': len(action_plan.decisions),
                'immediate_actions': len([d for d in action_plan.decisions if d.priority.value == 'immediate']),
                'communications_sent': len(action_plan.communications),
                'followup_required': action_plan.followup_required,
                'followup_date': action_plan.followup_date.isoformat() if action_plan.followup_date else None
            },
            'notifications': {
                'parent_notified': any(c.recipient_type == 'parent' for c in action_plan.communications),
                'child_educated': any(c.recipient_type == 'child' for c in action_plan.communications),
                'sender_warned': any(c.recipient_type == 'sender' for c in action_plan.communications)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Successfully processed message: {suspicious_message.message_id}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/api/parent/dashboard', methods=['GET'])
def parent_dashboard():
    """Get parent dashboard data"""
    try:
        parent_id = request.args.get('parent_id')
        if not parent_id:
            return jsonify({'error': 'parent_id required'}), 400
        
        # This would typically fetch from database
        dashboard_data = {
            'parent_id': parent_id,
            'children': [
                {
                    'child_id': 'child_1',
                    'name': 'Emma',
                    'age': 12,
                    'recent_incidents': 2,
                    'last_activity': datetime.now().isoformat()
                }
            ],
            'recent_alerts': [
                {
                    'alert_id': 'alert_1',
                    'child_name': 'Emma',
                    'threat_type': 'bullying',
                    'severity': 'medium',
                    'timestamp': datetime.now().isoformat(),
                    'status': 'resolved'
                }
            ],
            'statistics': {
                'total_messages_analyzed': 156,
                'threats_detected': 8,
                'threats_blocked': 3,
                'educational_content_delivered': 12
            }
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error fetching dashboard: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/child/profile', methods=['GET', 'POST'])
def child_profile():
    """Get or update child profile"""
    try:
        if request.method == 'GET':
            child_id = request.args.get('child_id')
            if not child_id:
                return jsonify({'error': 'child_id required'}), 400
            
            # This would typically fetch from database
            profile_data = {
                'child_id': child_id,
                'name': 'Emma',
                'age': 12,
                'grade_level': '7th',
                'previous_incidents': 2,
                'safety_settings': {
                    'content_filtering': 'high',
                    'stranger_contact_blocking': True,
                    'educational_mode': 'age_appropriate'
                },
                'notification_preferences': {
                    'immediate_alerts': True,
                    'daily_summary': False,
                    'weekly_report': True
                }
            }
            
            return jsonify(profile_data)
            
        elif request.method == 'POST':
            data = request.get_json()
            child_id = data.get('child_id')
            
            if not child_id:
                return jsonify({'error': 'child_id required'}), 400
            
            # This would typically update database
            logger.info(f"Updated profile for child: {child_id}")
            
            return jsonify({
                'message': 'Profile updated successfully',
                'child_id': child_id,
                'updated_at': datetime.now().isoformat()
            })
            
    except Exception as e:
        logger.error(f"Error handling child profile: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/notifications/send', methods=['POST'])
def send_notification():
    """Send notification to parent"""
    try:
        data = request.get_json()
        
        required_fields = ['recipient_type', 'message', 'priority']
        if not all(field in data for field in required_fields):
            return jsonify({
                'error': 'Missing required fields',
                'required': required_fields
            }), 400
        
        # This would typically integrate with notification service
        notification_id = f"notif_{datetime.now().timestamp()}"
        
        logger.info(f"Sent {data['recipient_type']} notification: {notification_id}")
        
        return jsonify({
            'notification_id': notification_id,
            'status': 'sent',
            'recipient_type': data['recipient_type'],
            'priority': data['priority'],
            'sent_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate safety report"""
    try:
        data = request.get_json()
        report_type = data.get('report_type', 'weekly')
        child_id = data.get('child_id')
        
        if not child_id:
            return jsonify({'error': 'child_id required'}), 400
        
        # This would typically generate from database
        report_data = {
            'report_id': f"report_{datetime.now().timestamp()}",
            'report_type': report_type,
            'child_id': child_id,
            'period': {
                'start_date': '2024-01-01',
                'end_date': '2024-01-07'
            },
            'summary': {
                'messages_analyzed': 45,
                'threats_detected': 3,
                'actions_taken': 8,
                'educational_content_delivered': 5
            },
            'threat_breakdown': {
                'bullying': 1,
                'inappropriate_content': 1,
                'stranger_contact': 1
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(report_data)
        
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
