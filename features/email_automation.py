"""
Email Automation - Automated email campaigns and notifications
"""

import boto3
from config import config
from datetime import datetime

class EmailAutomation:
    """
    Manages automated email notifications and campaigns
    """
    
    def __init__(self):
        self.ses = None
        self.enabled = config.ENABLE_EMAIL_AUTOMATION
        
        if self.enabled:
            try:
                self.ses = boto3.client('ses', region_name=config.REGION_NAME)
            except:
                print("Email automation not available")
    
    def send_welcome_email(self, employee_data):
        """
        Send welcome email to new employee
        """
        subject = f"Welcome to {config.COMPANY_NAME}, {employee_data['name']}! 🎉"
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                .header {{ background: linear-gradient(135deg, {config.PRIMARY_COLOR}, {config.SECONDARY_COLOR}); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .button {{ background: {config.PRIMARY_COLOR}; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to {config.COMPANY_NAME}!</h1>
            </div>
            <div class="content">
                <p>Dear {employee_data['name']},</p>
                
                <p>We're thrilled to have you join our team as a {employee_data.get('role', 'Team Member')}! 
                Your journey with us begins today, and we're excited to support you every step of the way.</p>
                
                <h3>🚀 Get Started:</h3>
                <ul>
                    <li>Access your AI-powered onboarding assistant</li>
                    <li>Complete your personalized learning path</li>
                    <li>Experience our VR training modules</li>
                    <li>Connect with your mentor and team</li>
                </ul>
                
                <p style="text-align: center; margin: 30px 0;">
                    <a href="https://onboarding.company.com" class="button">Launch Your Onboarding</a>
                </p>
                
                <p>If you have any questions, our AI assistant is available 24/7, or you can reach out to 
                hr@{config.COMPANY_NAME.lower()}.com</p>
                
                <p>Welcome aboard!<br>
                The {config.COMPANY_NAME} Team</p>
            </div>
        </body>
        </html>
        """
        
        return self._send_email(
            employee_data['email'],
            subject,
            html_body
        )
    
    def send_progress_update(self, employee_data, progress_data):
        """
        Send progress update email
        """
        subject = f"Your Onboarding Progress - {progress_data.get('overall_progress', 0)}% Complete!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Great Progress, {employee_data['name']}! 🌟</h2>
            
            <p>You're <strong>{progress_data.get('overall_progress', 0)}%</strong> through your onboarding journey!</p>
            
            <h3>📊 Your Stats:</h3>
            <ul>
                <li>Modules Completed: {len(progress_data.get('completed_modules', []))}</li>
                <li>Learning Streak: {progress_data.get('learning_streak_days', 0)} days</li>
                <li>Assessments Passed: {progress_data.get('assessments_completed', 0)}</li>
            </ul>
            
            <h3>🎯 Next Steps:</h3>
            <ul>
                <li>Continue with your current module</li>
                <li>Try a VR training session</li>
                <li>Schedule time with your mentor</li>
            </ul>
            
            <p><a href="https://onboarding.company.com">Continue Your Journey →</a></p>
        </body>
        </html>
        """
        
        return self._send_email(
            employee_data['email'],
            subject,
            html_body
        )
    
    def send_assessment_reminder(self, employee_data, assessment_data):
        """
        Send assessment reminder email
        """
        subject = f"Assessment Ready: {assessment_data['name']}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Time to Test Your Knowledge! ✅</h2>
            
            <p>Hi {employee_data['name']},</p>
            
            <p>You're ready to take the <strong>{assessment_data['name']}</strong> assessment.</p>
            
            <p><strong>Details:</strong></p>
            <ul>
                <li>Duration: {assessment_data.get('duration', 'N/A')}</li>
                <li>Questions: {assessment_data.get('questions', 'N/A')}</li>
                <li>Passing Score: 70%</li>
            </ul>
            
            <p><a href="https://onboarding.company.com/assessments">Start Assessment →</a></p>
        </body>
        </html>
        """
        
        return self._send_email(
            employee_data['email'],
            subject,
            html_body
        )
    
    def send_meeting_reminder(self, employee_data, meeting_data):
        """
        Send meeting reminder email
        """
        subject = f"Reminder: {meeting_data['title']} - {meeting_data['date']}"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>📅 Meeting Reminder</h2>
            
            <p>Hi {employee_data['name']},</p>
            
            <p>This is a reminder about your upcoming meeting:</p>
            
            <p><strong>{meeting_data['title']}</strong><br>
            📅 {meeting_data['date']} at {meeting_data['time']}<br>
            ⏱️ Duration: {meeting_data['duration']}<br>
            📍 Location: {meeting_data.get('location', 'Virtual')}</p>
            
            {'<p><a href="' + meeting_data['meeting_link'] + '">Join Meeting</a></p>' if meeting_data.get('meeting_link') else ''}
            
            <p>Looking forward to seeing you!</p>
        </body>
        </html>
        """
        
        return self._send_email(
            employee_data['email'],
            subject,
            html_body
        )
    
    def _send_email(self, recipient, subject, html_body):
        """
        Internal method to send email via SES
        """
        if not self.enabled or not self.ses:
            print(f"Email would be sent to {recipient}: {subject}")
            return {
                'success': False,
                'message': 'Email automation not enabled'
            }
        
        try:
            response = self.ses.send_email(
                Source=config.SES_SENDER_EMAIL,
                Destination={'ToAddresses': [recipient]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            return {
                'success': True,
                'message_id': response['MessageId']
            }
        
        except Exception as e:
            print(f"Error sending email: {e}")
            return {
                'success': False,
                'error': str(e)
            }
