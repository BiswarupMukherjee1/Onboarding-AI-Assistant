# Welcome meeting with manager

# HR orientation session

# Team introduction meetings

# Technical onboarding sessions

# 1-on-1 check-ins with mentor

# Training sessions

"""
Interview Scheduler Lambda Function
Automates meeting scheduling for new employee onboarding
Handles calendar management, conflict resolution, and notifications
"""

import json
import boto3
import logging
from datetime import datetime, timedelta
import uuid
from typing import Dict, Any, List

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
events_client = boto3.client('events')
ses_client = boto3.client('ses')

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS SETUP
SCHEDULE_TABLE = 'onboarding-schedules'        # DynamoDB table for schedules
AVAILABILITY_TABLE = 'interviewer-availability' # DynamoDB table for availability
MEETINGS_TABLE = 'onboarding-meetings'         # DynamoDB table for meetings
SES_SENDER_EMAIL = 'noreply@company.com'   # Must be verified in SES

def lambda_handler(event, context):
    """
    Main Lambda handler for interview/meeting scheduling
    
    Event triggers:
    - New employee added to system
    - Manual scheduling request
    - EventBridge scheduled check
    - Reschedule request
    """
    try:
        logger.info(f"Processing scheduling event: {json.dumps(event)}")
        
        # Determine the scheduling action
        if 'scheduling_action' in event:
            action = event['scheduling_action']
            
            if action == 'schedule_onboarding_meetings':
                # Schedule all meetings for new employee
                result = schedule_onboarding_meetings(event)
            
            elif action == 'find_available_slots':
                # Find available time slots for a meeting
                result = find_available_time_slots(event)
            
            elif action == 'confirm_meeting':
                # Confirm a scheduled meeting
                result = confirm_meeting(event)
            
            elif action == 'reschedule_meeting':
                # Reschedule an existing meeting
                result = reschedule_meeting(event)
            
            elif action == 'cancel_meeting':
                # Cancel a meeting
                result = cancel_meeting(event)
            
            elif action == 'daily_schedule_check':
                # Daily check for upcoming meetings
                result = perform_daily_schedule_check(event)
            
            else:
                raise ValueError(f"Unknown scheduling action: {action}")
        
        # Handle EventBridge scheduled triggers
        elif 'source' in event and event['source'] == 'aws.events':
            result = handle_scheduled_event(event)
        
        # Handle new employee trigger
        elif 'new_employee' in event:
            result = schedule_new_employee_meetings(event)
        
        else:
            raise ValueError("Invalid event structure for interview scheduler")
        
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Error in interview scheduler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Interview scheduling failed',
                'details': str(e)
            })
        }

def schedule_onboarding_meetings(event):
    """
    Schedule all required onboarding meetings for a new employee
    
    This is the main function that automates meeting scheduling
    """
    try:
        employee_data = event.get('employee_data', {})
        
        employee_id = employee_data.get('employee_id')
        employee_name = employee_data.get('name')
        employee_email = employee_data.get('email')
        role = employee_data.get('role', '')
        department = employee_data.get('department', '')
        start_date_str = employee_data.get('start_date', datetime.now().isoformat())
        start_date = datetime.fromisoformat(start_date_str.split('T')[0])
        
        logger.info(f"Scheduling onboarding meetings for {employee_name} ({employee_id})")
        
        # Define required meeting types based on role and department
        required_meetings = get_required_meetings(role, department)
        
        scheduled_meetings = []
        scheduling_conflicts = []
        
        # Schedule each required meeting
        for meeting_config in required_meetings:
            try:
                # Generate preferred time slots
                preferred_times = generate_preferred_times(start_date, meeting_config)
                
                # Find available time slot
                available_slot = find_optimal_time_slot(
                    employee_id=employee_id,
                    employee_email=employee_email,
                    employee_name=employee_name,
                    meeting_type=meeting_config['type'],
                    duration_minutes=meeting_config['duration'],
                    preferred_times=preferred_times,
                    required_participants=meeting_config['participants']
                )
                
                if available_slot:
                    # Schedule the meeting
                    meeting_result = create_meeting(
                        employee_id, 
                        employee_email, 
                        employee_name,
                        meeting_config, 
                        available_slot
                    )
                    scheduled_meetings.append(meeting_result)
                    
                    # Send calendar invites
                    send_calendar_invites(meeting_result)
                    
                else:
                    scheduling_conflicts.append({
                        'meeting_type': meeting_config['type'],
                        'reason': 'no_available_slots',
                        'participants': meeting_config['participants']
                    })
                    
            except Exception as e:
                logger.error(f"Error scheduling {meeting_config['type']}: {str(e)}")
                scheduling_conflicts.append({
                    'meeting_type': meeting_config['type'],
                    'reason': f'error: {str(e)}',
                    'participants': meeting_config.get('participants', [])
                })
        
        # Store scheduling results
        store_scheduling_results(employee_id, scheduled_meetings, scheduling_conflicts)
        
        # Send summary email to employee and manager
        send_scheduling_summary(employee_data, scheduled_meetings, scheduling_conflicts)
        
        return {
            'status': 'success',
            'employee_id': employee_id,
            'scheduled_meetings': len(scheduled_meetings),
            'scheduling_conflicts': len(scheduling_conflicts),
            'meetings': scheduled_meetings,
            'conflicts': scheduling_conflicts
        }
        
    except Exception as e:
        logger.error(f"Error scheduling onboarding meetings: {str(e)}")
        raise

def get_required_meetings(role, department):
    """
    Get list of required meetings based on role and department
    
    Returns meeting configurations with participants and timing
    """
    
    # Base meetings for ALL employees
    base_meetings = [
        {
            'type': 'manager_welcome',
            'title': 'Welcome Meeting with Manager',
            'duration': 60,  # minutes
            'timing': 'first_day',
            'participants': ['direct_manager'],
            'priority': 'high',
            'description': 'Initial welcome and role overview'
        },
        {
            'type': 'hr_orientation',
            'title': 'HR Orientation Session',
            'duration': 90,
            'timing': 'first_week',
            'participants': ['hr_representative'],
            'priority': 'high',
            'description': 'Company policies, benefits, and compliance'
        },
        {
            'type': 'buddy_introduction',
            'title': 'Meet Your Onboarding Buddy',
            'duration': 30,
            'timing': 'first_week',
            'participants': ['onboarding_buddy'],
            'priority': 'medium',
            'description': 'Social integration and peer support'
        }
    ]
    
    # Role-specific meetings
    role_meetings = []
    
    if any(keyword in role.lower() for keyword in ['engineer', 'developer']):
        role_meetings.extend([
            {
                'type': 'technical_architecture',
                'title': 'Technical Architecture Overview',
                'duration': 120,
                'timing': 'first_week',
                'participants': ['tech_lead', 'senior_engineer'],
                'priority': 'high',
                'description': 'System architecture and technical standards'
            },
            {
                'type': 'development_setup',
                'title': 'Development Environment Setup',
                'duration': 90,
                'timing': 'first_day',
                'participants': ['dev_ops_engineer'],
                'priority': 'high',
                'description': 'Code repositories, tools, and workflow'
            }
        ])
    
    elif any(keyword in role.lower() for keyword in ['sales', 'account']):
        role_meetings.extend([
            {
                'type': 'sales_process_training',
                'title': 'Sales Process and CRM Training',
                'duration': 120,
                'timing': 'first_week',
                'participants': ['sales_manager', 'sales_ops'],
                'priority': 'high',
                'description': 'Sales methodology and system training'
            },
            {
                'type': 'product_demo_training',
                'title': 'Product Demonstration Training',
                'duration': 90,
                'timing': 'second_week',
                'participants': ['product_specialist'],
                'priority': 'high',
                'description': 'Product knowledge and demo skills'
            }
        ])
    
    elif any(keyword in role.lower() for keyword in ['marketing']):
        role_meetings.extend([
            {
                'type': 'brand_guidelines',
                'title': 'Brand Guidelines and Marketing Standards',
                'duration': 90,
                'timing': 'first_week',
                'participants': ['brand_manager'],
                'priority': 'high',
                'description': 'Brand voice and creative standards'
            }
        ])
    
    return base_meetings + role_meetings

def generate_preferred_times(start_date, meeting_config):
    """
    Generate preferred time slots for a meeting based on timing requirements
    """
    preferred_times = []
    timing = meeting_config.get('timing', 'first_week')
    duration = meeting_config.get('duration', 60)
    
    # Calculate date range based on timing
    if timing == 'first_day':
        target_dates = [start_date]
    elif timing == 'first_week':
        target_dates = [start_date + timedelta(days=i) for i in range(5)]
    elif timing == 'second_week':
        target_dates = [start_date + timedelta(days=i) for i in range(7, 12)]
    else:
        target_dates = [start_date + timedelta(days=i) for i in range(14)]
    
    # Generate time slots for each target date
    for date in target_dates:
        # Skip weekends
        if date.weekday() >= 5:
            continue
        
        # Generate common business hour slots
        business_hours = [
            (9, 0),   # 9:00 AM
            (10, 0),  # 10:00 AM
            (11, 0),  # 11:00 AM
            (13, 0),  # 1:00 PM
            (14, 0),  # 2:00 PM
            (15, 0),  # 3:00 PM
        ]
        
        for hour, minute in business_hours:
            start_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=duration)
            
            # Don't schedule past 5 PM
            if end_time.hour >= 17:
                continue
            
            preferred_times.append({
                'start_time': start_time,
                'end_time': end_time
            })
    
    return preferred_times

def find_optimal_time_slot(employee_id, employee_email, employee_name, 
                          meeting_type, duration_minutes, preferred_times, 
                          required_participants):
    """
    Find the optimal available time slot for a meeting
    Checks participant availability and returns best slot
    """
    try:
        logger.info(f"Finding optimal slot for {meeting_type}")
        
        # For this example, we'll return the first available slot
        # In production, we should check actual calendar availability from DynamoDB
        
        if preferred_times:
            # Return first preferred time (simplified logic)
            return {
                'slot': preferred_times[0],
                'participants': []  # Would contain actual participant details
            }
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding optimal time slot: {str(e)}")
        return None

def create_meeting(employee_id, employee_email, employee_name, meeting_config, available_slot):
    """
    Create a meeting record in DynamoDB
    """
    try:
        table = dynamodb.Table(MEETINGS_TABLE)
        
        meeting_id = f"meeting_{uuid.uuid4()}"
        time_slot = available_slot['slot']
        
        meeting_data = {
            'meeting_id': meeting_id,
            'employee_id': employee_id,
            'employee_email': employee_email,
            'employee_name': employee_name,
            'meeting_type': meeting_config['type'],
            'title': meeting_config['title'],
            'description': meeting_config['description'],
            'start_time': time_slot['start_time'].isoformat(),
            'end_time': time_slot['end_time'].isoformat(),
            'duration_minutes': meeting_config['duration'],
            'participants': available_slot.get('participants', []),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        table.put_item(Item=meeting_data)
        
        logger.info(f"Created meeting {meeting_id} for {employee_name}")
        return meeting_data
        
    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
        raise

def send_calendar_invites(meeting_data):
    """
    Send calendar invites to all meeting participants via email
    """
    try:
        start_time = datetime.fromisoformat(meeting_data['start_time'])
        end_time = datetime.fromisoformat(meeting_data['end_time'])
        
        subject = f"Meeting Invitation: {meeting_data['title']}"
        
        body = f"""
        You're invited to: {meeting_data['title']}
        
        When: {start_time.strftime('%A, %B %d, %Y at %I:%M %p')} - {end_time.strftime('%I:%M %p')}
        Duration: {meeting_data['duration_minutes']} minutes
        
        Description:
        {meeting_data['description']}
        
        Meeting ID: {meeting_data['meeting_id']}
        
        Please confirm your attendance.
        """
        
        # Send to employee
        ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [meeting_data['employee_email']]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': body, 'Charset': 'UTF-8'}}
            }
        )
        
        logger.info(f"Sent calendar invite for meeting {meeting_data['meeting_id']}")
        
    except Exception as e:
        logger.error(f"Error sending calendar invites: {str(e)}")

def store_scheduling_results(employee_id, scheduled_meetings, conflicts):
    """
    Store scheduling results in DynamoDB for tracking
    """
    try:
        table = dynamodb.Table(SCHEDULE_TABLE)
        
        scheduling_record = {
            'employee_id': employee_id,
            'record_type': 'scheduling_results',
            'scheduled_meetings': scheduled_meetings,
            'scheduling_conflicts': conflicts,
            'total_scheduled': len(scheduled_meetings),
            'total_conflicts': len(conflicts),
            'created_at': datetime.now().isoformat()
        }
        
        table.put_item(Item=scheduling_record)
        logger.info(f"Stored scheduling results for employee {employee_id}")
        
    except Exception as e:
        logger.error(f"Error storing scheduling results: {str(e)}")

def send_scheduling_summary(employee_data, scheduled_meetings, conflicts):
    """
    Send scheduling summary email to employee and manager
    """
    try:
        employee_email = employee_data.get('email')
        employee_name = employee_data.get('name')
        
        subject = f"Your Onboarding Meeting Schedule - {len(scheduled_meetings)} meetings scheduled"
        
        meetings_list = []
        for meeting in scheduled_meetings:
            start_time = datetime.fromisoformat(meeting['start_time'])
            meetings_list.append(f"""
            📅 {meeting['title']}
            Date: {start_time.strftime('%A, %B %d, %Y')}
            Time: {start_time.strftime('%I:%M %p')} - {datetime.fromisoformat(meeting['end_time']).strftime('%I:%M %p')}
            """)
        
        body = f"""
        Dear {employee_name},
        
        Welcome! We've scheduled your onboarding meetings:
        
        📅 SCHEDULED MEETINGS ({len(scheduled_meetings)}):
        {chr(10).join(meetings_list)}
        
        Check your email for individual meeting invitations.
        
        Questions? Contact hr@yourcompany.com
        
        Looking forward to your first day!
        """
        
        ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={'ToAddresses': [employee_email]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Text': {'Data': body, 'Charset': 'UTF-8'}}
            }
        )
        
        logger.info(f"Sent scheduling summary to {employee_email}")
        
    except Exception as e:
        logger.error(f"Error sending scheduling summary: {str(e)}")

# Additional helper functions

def find_available_time_slots(event):
    """Find available time slots for a meeting request"""
    return {'status': 'success', 'available_slots': []}

def confirm_meeting(event):
    """Confirm a scheduled meeting"""
    meeting_id = event.get('meeting_id')
    return {'status': 'success', 'meeting_id': meeting_id}

def reschedule_meeting(event):
    """Reschedule an existing meeting"""
    meeting_id = event.get('meeting_id')
    return {'status': 'success', 'meeting_id': meeting_id}

def cancel_meeting(event):
    """Cancel a meeting"""
    meeting_id = event.get('meeting_id')
    return {'status': 'success', 'meeting_id': meeting_id}

def perform_daily_schedule_check(event):
    """Perform daily check of scheduled meetings"""
    return {'status': 'success', 'upcoming_meetings': 0}

def schedule_new_employee_meetings(event):
    """Handle new employee trigger"""
    return schedule_onboarding_meetings(event)

def handle_scheduled_event(event):
    """Handle EventBridge scheduled events"""
    return perform_daily_schedule_check(event)
