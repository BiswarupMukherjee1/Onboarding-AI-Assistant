"""
Email Automation Lambda Function
Sends scheduled emails and notifications for onboarding
"""

import json
import boto3
import logging
from datetime import datetime

# Initialize AWS clients
ses = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# These should be updated with correct values
SES_SENDER_EMAIL = 'noreply@company.com'  # Must be verified in SES
COMPANY_NAME = 'Company'

def lambda_handler(event, context):
    """
    Lambda handler triggered by EventBridge schedule or API Gateway
    """
    try:
        logger.info(f"Email automation triggered: {json.dumps(event)}")
        
        # Determine email type from event
        email_type = event.get('email_type', 'welcome')
        recipient_data = event.get('recipient_data', {})
        
        if email_type == 'welcome':
            result = send_welcome_email(recipient_data)
        elif email_type == 'progress_update':
            result = send_progress_update(recipient_data)
        elif email_type == 'assessment_reminder':
            result = send_assessment_reminder(recipient_data)
        elif email_type == 'meeting_reminder':
            result = send_meeting_reminder(recipient_data)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Unknown email type: {email_type}'})
            }
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    
    except Exception as e:
        logger.error(f"Error in email automation: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def send_welcome_email(recipient_data):
    """
    Send welcome email to new employee
    """
    try:
        recipient_email = recipient_data.get('email')
        recipient_name = recipient_data.get('name', 'New Employee')
        role = recipient_data.get('role', 'Team Member')
        
        subject = f"Welcome to {COMPANY_NAME}, {recipient_name}! 🎉"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); 
                           color: white; padding: 30px; text-align: center; }}
                .content {{ padding: 30px; }}
                .button {{ background: #667eea; color: white; padding: 12px 24px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; }}
                .footer {{ background: #f4f4f4; padding: 20px; text-align: center; 
                          font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to {COMPANY_NAME}!</h1>
            </div>
            <div class="content">
                <p>Dear {recipient_name},</p>
                
                <p>We're thrilled to welcome you to our team as a <strong>{role}</strong>! 
                Your journey with us begins today, and we're committed to supporting you every step of the way.</p>
                
                <h3>🚀 Get Started with Your AI Onboarding Assistant:</h3>
                <ul>
                    <li><strong>24/7 AI Support:</strong> Get instant answers to your questions</li>
                    <li><strong>Personalized Learning Path:</strong> Tailored to your role and experience</li>
                    <li><strong>VR Training:</strong> Immersive hands-on experiences</li>
                    <li><strong>Progress Tracking:</strong> Monitor your onboarding journey</li>
                </ul>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="https://onboarding.company.com" class="button">
                        Launch Your Onboarding Dashboard
                    </a>
                </p>
                
                <h3>📅 Your First Week:</h3>
                <ul>
                    <li><strong>Day 1:</strong> Meet your manager and team</li>
                    <li><strong>Day 2-3:</strong> Complete company culture training</li>
                    <li><strong>Day 4-5:</strong> Role-specific technical training</li>
                </ul>
                
                <p>If you have any questions, our AI assistant is available 24/7, or you can reach out 
                to <a href="mailto:hr@{COMPANY_NAME.lower().replace(' ', '')}.com">
                hr@{COMPANY_NAME.lower().replace(' ', '')}.com</a></p>
                
                <p>Welcome aboard!<br>
                <strong>The {COMPANY_NAME} Team</strong></p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.now().year} {COMPANY_NAME}. All rights reserved.</p>
                <p>This is an automated message from your AI Onboarding Assistant.</p>
            </div>
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
            }
        )
        
        logger.info(f"Welcome email sent to {recipient_email}")
        
        return {
            'success': True,
            'message_id': response['MessageId'],
            'recipient': recipient_email
        }
    
    except Exception as e:
        logger.error(f"Error sending welcome email: {str(e)}")
        return {'success': False, 'error': str(e)}

def send_progress_update(recipient_data):
    """
    Send progress update email
    """
    try:
        recipient_email = recipient_data.get('email')
        recipient_name = recipient_data.get('name')
        progress = recipient_data.get('progress', 0)
        
        subject = f"Your Onboarding Progress - {progress}% Complete!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Great Progress, {recipient_name}! 🌟</h2>
            <p>You're <strong>{progress}%</strong> through your onboarding journey!</p>
            <h3>Keep it up!</h3>
            <p><a href="https://onboarding.company.com">View Your Dashboard</a></p>
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
            }
        )
        
        return {'success': True, 'message_id': response['MessageId']}
    
    except Exception as e:
        logger.error(f"Error sending progress update: {str(e)}")
        return {'success': False, 'error': str(e)}

def send_assessment_reminder(recipient_data):
    """
    Send assessment reminder email
    """
    try:
        recipient_email = recipient_data.get('email')
        recipient_name = recipient_data.get('name')
        assessment_name = recipient_data.get('assessment_name', 'Onboarding Assessment')
        
        subject = f"Reminder: Complete Your {assessment_name}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Assessment Reminder ✅</h2>
            <p>Hi {recipient_name},</p>
            <p>Don't forget to complete your <strong>{assessment_name}</strong>!</p>
            <p><a href="https://onboarding.company.com/assessments">Start Assessment</a></p>
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
            }
        )
        
        return {'success': True, 'message_id': response['MessageId']}
    
    except Exception as e:
        logger.error(f"Error sending assessment reminder: {str(e)}")
        return {'success': False, 'error': str(e)}

def send_meeting_reminder(recipient_data):
    """
    Send meeting reminder email
    """
    try:
        recipient_email = recipient_data.get('email')
        recipient_name = recipient_data.get('name')
        meeting_title = recipient_data.get('meeting_title', 'Onboarding Meeting')
        meeting_time = recipient_data.get('meeting_time')
        meeting_link = recipient_data.get('meeting_link')
        
        subject = f"Reminder: {meeting_title}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Meeting Reminder 📅</h2>
            <p>Hi {recipient_name},</p>
            <p>This is a reminder about your upcoming meeting:</p>
            <p><strong>{meeting_title}</strong><br>
            Time: {meeting_time}</p>
            {f'<p><a href="{meeting_link}">Join Meeting</a></p>' if meeting_link else ''}
        </body>
        </html>
        """
        
        response = ses.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [recipient_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': html_body, 'Charset': 'UTF-8'}}
            }
        )
        
        return {'success': True, 'message_id': response['MessageId']}
    
    except Exception as e:
        logger.error(f"Error sending meeting reminder: {str(e)}")
        return {'success': False, 'error': str(e)}
