"""
Data Processor - Data transformation and analysis utilities
"""

import pandas as pd
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any

class DataProcessor:
    """
    Utilities for processing and analyzing onboarding data
    """
    
    @staticmethod
    def calculate_completion_rate(completed_items: int, total_items: int) -> float:
        """
        Calculate completion rate percentage
        """
        if total_items == 0:
            return 0.0
        return round((completed_items / total_items) * 100, 2)
    
    @staticmethod
    def calculate_learning_streak(activity_dates: List[str]) -> int:
        """
        Calculate consecutive learning days streak
        """
        if not activity_dates:
            return 0
        
        # Sort dates
        sorted_dates = sorted([datetime.strptime(d, '%Y-%m-%d').date() for d in activity_dates])
        
        # Check from most recent
        today = datetime.now().date()
        if sorted_dates[-1] != today and sorted_dates[-1] != (today - timedelta(days=1)):
            return 0  # Streak broken
        
        streak = 1
        for i in range(len(sorted_dates) - 1, 0, -1):
            diff = (sorted_dates[i] - sorted_dates[i-1]).days
            if diff == 1:
                streak += 1
            else:
                break
        
        return streak
    
    @staticmethod
    def predict_completion_date(current_progress: float, days_elapsed: int) -> str:
        """
        Predict onboarding completion date based on current progress
        """
        if current_progress == 0 or days_elapsed == 0:
            return "Not enough data"
        
        progress_per_day = current_progress / days_elapsed
        remaining_progress = 100 - current_progress
        
        if progress_per_day == 0:
            return "Not enough data"
        
        days_remaining = int(remaining_progress / progress_per_day)
        completion_date = datetime.now() + timedelta(days=days_remaining)
        
        return completion_date.strftime('%Y-%m-%d')
    
    @staticmethod
    def categorize_progress(completion_rate: float) -> Dict[str, Any]:
        """
        Categorize progress into meaningful segments
        """
        if completion_rate < 25:
            return {
                'category': 'Getting Started',
                'emoji': '🚀',
                'message': 'Just beginning your journey!',
                'color': '#FFA500'
            }
        elif completion_rate < 50:
            return {
                'category': 'Making Progress',
                'emoji': '📈',
                'message': 'You are on the right track!',
                'color': '#4169E1'
            }
        elif completion_rate < 75:
            return {
                'category': 'Halfway There',
                'emoji': '🎯',
                'message': 'Great momentum!',
                'color': '#32CD32'
            }
        elif completion_rate < 100:
            return {
                'category': 'Almost Done',
                'emoji': '🏁',
                'message': 'The finish line is in sight!',
                'color': '#FFD700'
            }
        else:
            return {
                'category': 'Completed',
                'emoji': '🎉',
                'message': 'Congratulations!',
                'color': '#00FF00'
            }
    
    @staticmethod
    def generate_weekly_report(progress_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate weekly progress report
        """
        report = {
            'week_ending': datetime.now().strftime('%Y-%m-%d'),
            'summary': {
                'modules_completed': len(progress_data.get('completed_modules', [])),
                'assessments_taken': progress_data.get('assessments_completed', 0),
                'vr_experiences': progress_data.get('vr_experiences_completed', 0),
                'total_learning_hours': round(
                    progress_data.get('total_learning_time_minutes', 0) / 60, 1
                )
            },
            'progress_rate': progress_data.get('overall_progress', 0),
            'streak': progress_data.get('learning_streak_days', 0),
            'achievements': progress_data.get('milestones_achieved', [])
        }
        
        # Add insights
        if report['summary']['modules_completed'] >= 5:
            report['insight'] = 'Excellent progress this week! Keep it up!'
        elif report['summary']['modules_completed'] >= 3:
            report['insight'] = 'Good steady progress. Stay consistent!'
        else:
            report['insight'] = 'Try to complete more modules this week.'
        
        return report
    
    @staticmethod
    def format_duration(minutes: int) -> str:
        """
        Format duration in minutes to human-readable format
        """
        if minutes < 60:
            return f"{minutes} min"
        
        hours = minutes // 60
        remaining_minutes = minutes % 60
        
        if remaining_minutes == 0:
            return f"{hours} hr" if hours == 1 else f"{hours} hrs"
        else:
            return f"{hours} hr {remaining_minutes} min"
    
    @staticmethod
    def parse_user_profile(raw_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse and normalize user profile data
        """
        return {
            'user_id': raw_profile.get('user_id', ''),
            'name': raw_profile.get('name', 'Unknown'),
            'email': raw_profile.get('email', ''),
            'role': raw_profile.get('role', 'Employee'),
            'department': raw_profile.get('department', 'General'),
            'start_date': raw_profile.get('start_date', datetime.now().strftime('%Y-%m-%d')),
            'experience_level': raw_profile.get('experience_level', 'beginner'),
            'learning_style': raw_profile.get('learning_style', 'mixed')
        }
    
    @staticmethod
    def aggregate_progress_data(user_progresses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate progress data across multiple users
        """
        if not user_progresses:
            return {}
        
        total_users = len(user_progresses)
        
        total_completion = sum(p.get('overall_progress', 0) for p in user_progresses)
        avg_completion = total_completion / total_users if total_users > 0 else 0
        
        total_modules = sum(len(p.get('completed_modules', [])) for p in user_progresses)
        avg_modules = total_modules / total_users if total_users > 0 else 0
        
        return {
            'total_users': total_users,
            'average_completion_rate': round(avg_completion, 2),
            'average_modules_completed': round(avg_modules, 2),
            'users_completed': sum(1 for p in user_progresses if p.get('overall_progress', 0) >= 100),
            'users_at_risk': sum(1 for p in user_progresses if p.get('overall_progress', 0) < 30)
        }
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> bool:
        """
        Export data to CSV file
        """
        try:
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    @staticmethod
    def import_from_csv(filename: str) -> List[Dict[str, Any]]:
        """
        Import data from CSV file
        """
        try:
            df = pd.read_csv(filename)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            return []
    
    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """
        Sanitize user input for safety
        """
        # Remove potentially dangerous characters
        sanitized = user_input.strip()
        sanitized = sanitized.replace('<', '&lt;').replace('>', '&gt;')
        return sanitized
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """
        Format timestamp to readable format
        """
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime('%B %d, %Y at %I:%M %p')
        except:
            return timestamp

# Create singleton instance
data_processor = DataProcessor()
