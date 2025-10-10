"""
Meeting Scheduler - Automated meeting scheduling

"""

import boto3
from config import config
from datetime import datetime, timedelta
import json

class MeetingScheduler:
    """
    Automated meeting scheduling and calendar management
    """
    
    def __init__(self):
        self.dynamodb = None
        self.enabled = config.ENABLE_SCHEDULER
        
        if self.enabled:
            try:
                self.dynamodb = boto3.resource('dynamodb', region_name=config.REGION_NAME)
            except:
                print("Scheduler not available")
    
    def get_upcoming_meetings(self, user_id):
        """
        Get list of upcoming meetings for user
        """
        # Mock data is used here for testing in production, query from calendar system. URLs are removed before commit
        today = datetime.now()
        
        meetings = [
            {
                'id': 'meet_001',
                'title': 'Welcome Meeting with Manager',
                'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'time': '10:00 AM',
                'duration': '60 minutes',
                'attendees': ['Manager', 'HR Representative'],
                'location': 'Conference Room A',
                'type': 'onboarding',
                'status': 'scheduled',
                'meeting_link': 'https://meet.company.com/abc123' 
            },
            {
                'id': 'meet_002',
                'title': 'Team Introduction',
                'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '2:00 PM',
                'duration': '45 minutes',
                'attendees': ['Team Members'],
                'location': 'Virtual',
                'type': 'team_building',
                'status': 'scheduled',
                'meeting_link': 'https://meet.company.com/xyz789'
            },
            {
                'id': 'meet_003',
                'title': 'Technical Onboarding Session',
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '11:00 AM',
                'duration': '90 minutes',
                'attendees': ['Tech Lead', 'Senior Engineer'],
                'location': 'Training Room',
                'type': 'training',
                'status': 'scheduled',
                'meeting_link': None
            }
        ]
        
        return meetings
    
    def schedule_meeting(self, meeting_data):
        """
        Schedule a new meeting
        """
        required_fields = ['title', 'date', 'time', 'duration', 'attendees']
        
        for field in required_fields:
            if field not in meeting_data:
                return {
                    'success': False,
                    'error': f'Missing required field: {field}'
                }
        
        # Create meeting ID
        meeting_id = f"meet_{int(datetime.now().timestamp())}"
        
        meeting = {
            'id': meeting_id,
            'title': meeting_data['title'],
            'date': meeting_data['date'],
            'time': meeting_data['time'],
            'duration': meeting_data['duration'],
            'attendees': meeting_data['attendees'],
            'location': meeting_data.get('location', 'Virtual'),
            'type': meeting_data.get('type', 'general'),
            'status': 'scheduled',
            'created_at': datetime.now().isoformat(),
            'meeting_link': self._generate_meeting_link(meeting_id)
        }
        
        # In production, this needs to be saved to database, and returned messages
        
        return {
            'success': True,
            'meeting': meeting,
            'message': 'Meeting scheduled successfully'
        }
    
    def _generate_meeting_link(self, meeting_id):
        """
        Generate virtual meeting link
        """
        return f"https://meet.company.com/{meeting_id}"
    
    def reschedule_meeting(self, meeting_id, new_date, new_time):
        """
        Reschedule an existing meeting
        """
        # In production, update database and notify attendees
        return {
            'success': True,
            'meeting_id': meeting_id,
            'new_date': new_date,
            'new_time': new_time,
            'message': 'Meeting rescheduled successfully'
        }
    
    def cancel_meeting(self, meeting_id, reason=None):
        """
        Cancel a meeting
        """
        # In production, update database and notify attendees
        return {
            'success': True,
            'meeting_id': meeting_id,
            'status': 'cancelled',
            'reason': reason,
            'message': 'Meeting cancelled successfully'
        }
    
    def get_available_time_slots(self, date, duration_minutes):
        """
        Find available time slots for a given date
        """
        # Mock available slots - in production, check calendar availability
        available_slots = [
            {'time': '9:00 AM', 'available': True},
            {'time': '10:00 AM', 'available': False},
            {'time': '11:00 AM', 'available': True},
            {'time': '1:00 PM', 'available': True},
            {'time': '2:00 PM', 'available': True},
            {'time': '3:00 PM', 'available': False},
            {'time': '4:00 PM', 'available': True}
        ]
        
        return [slot for slot in available_slots if slot['available']]
    
    def suggest_meeting_times(self, attendees, duration_minutes, preferred_days=7):
        """
        Suggest optimal meeting times based on attendee availability
        """
        suggestions = []
        today = datetime.now()
        
        for i in range(1, preferred_days + 1):
            date = (today + timedelta(days=i)).strftime('%Y-%m-%d')
            slots = self.get_available_time_slots(date, duration_minutes)
            
            if slots:
                suggestions.append({
                    'date': date,
                    'day_name': (today + timedelta(days=i)).strftime('%A'),
                    'available_times': [slot['time'] for slot in slots[:3]]  # Top 3 slots
                })
        
        return suggestions[:5]  # Return top 5 days
