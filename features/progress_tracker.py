"""
Progress Tracker - Analytics and progress monitoring
"""

import boto3
from config import config
from datetime import datetime, timedelta
import json

class ProgressTracker:
    """
    Tracks and analyzes employee onboarding progress
    """
    
    def __init__(self):
        self.dynamodb = None
        self.table = None
        
        if config.ENABLE_PROGRESS_TRACKING:
            try:
                self.dynamodb = boto3.resource('dynamodb', region_name=config.REGION_NAME)
                self.table = self.dynamodb.Table(config.DYNAMODB_ONBOARDING_TABLE)
            except:
                print("Progress tracking table not available")
    
    def initialize_progress(self, user_id, user_profile):
        """
        Initialize progress tracking for new user
        """
        initial_progress = {
            'user_id': user_id,
            'role': user_profile.get('role', 'Unknown'),
            'department': user_profile.get('department', 'Unknown'),
            'start_date': str(datetime.now().date()),
            'overall_progress': 0,
            'completed_modules': [],
            'in_progress_modules': [],
            'upcoming_modules': [],
            'assessments_completed': 0,
            'vr_experiences_completed': 0,
            'learning_streak_days': 0,
            'last_activity_date': str(datetime.now().date()),
            'milestones_achieved': [],
            'total_learning_time_minutes': 0
        }
        
        if self.table:
            try:
                self.table.put_item(Item=initial_progress)
            except Exception as e:
                print(f"Error initializing progress: {e}")
        
        return initial_progress
    
    def update_progress(self, user_id, update_data):
        """
        Update user progress
        """
        if not self.table:
            return {'success': False, 'message': 'Progress tracking not available'}
        
        try:
            # Get current progress
            response = self.table.get_item(Key={'user_id': user_id})
            
            if 'Item' not in response:
                return {'success': False, 'message': 'User progress not found'}
            
            current_progress = response['Item']
            
            # Update fields
            for key, value in update_data.items():
                current_progress[key] = value
            
            # Update last activity
            current_progress['last_activity_date'] = str(datetime.now().date())
            
            # Calculate learning streak
            current_progress['learning_streak_days'] = self._calculate_streak(
                current_progress.get('last_activity_date')
            )
            
            # Save updated progress
            self.table.put_item(Item=current_progress)
            
            return {
                'success': True,
                'progress': current_progress
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_progress(self, user_id):
        """
        Get current progress for user
        """
        if not self.table:
            # Return mock data if tracking not available
            return self._get_mock_progress(user_id)
        
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            
            if 'Item' in response:
                return response['Item']
            else:
                return self._get_mock_progress(user_id)
        
        except Exception as e:
            print(f"Error getting progress: {e}")
            return self._get_mock_progress(user_id)
    
    def _get_mock_progress(self, user_id):
        """
        Return mock progress data when DynamoDB is not available
        """
        return {
            'user_id': user_id,
            'overall_progress': 45,
            'completed_modules': ['Company Culture', 'IT Systems Setup'],
            'in_progress_modules': ['Role-Specific Training'],
            'upcoming_modules': ['Team Collaboration', 'Advanced Skills'],
            'assessments_completed': 2,
            'vr_experiences_completed': 1,
            'learning_streak_days': 12,
            'last_activity_date': str(datetime.now().date()),
            'total_learning_time_minutes': 180
        }
    
    def _calculate_streak(self, last_activity_date):
        """
        Calculate learning streak in days
        """
        try:
            last_date = datetime.strptime(last_activity_date, '%Y-%m-%d').date()
            today = datetime.now().date()
            diff = (today - last_date).days
            
            if diff == 0:
                return 1  # Active today
            elif diff == 1:
                return 1  # Continue streak
            else:
                return 0  # Streak broken
        except:
            return 0
    
    def complete_module(self, user_id, module_name, time_spent_minutes):
        """
        Mark a module as completed
        """
        progress = self.get_progress(user_id)
        
        if module_name not in progress.get('completed_modules', []):
            completed = progress.get('completed_modules', [])
            completed.append(module_name)
            
            # Remove from in-progress
            in_progress = progress.get('in_progress_modules', [])
            if module_name in in_progress:
                in_progress.remove(module_name)
            
            # Update total time
            total_time = progress.get('total_learning_time_minutes', 0)
            total_time += time_spent_minutes
            
            # Calculate new overall progress
            total_modules = len(completed) + len(in_progress) + len(progress.get('upcoming_modules', []))
            overall_progress = int((len(completed) / total_modules) * 100) if total_modules > 0 else 0
            
            update_data = {
                'completed_modules': completed,
                'in_progress_modules': in_progress,
                'total_learning_time_minutes': total_time,
                'overall_progress': overall_progress
            }
            
            return self.update_progress(user_id, update_data)
        
        return {'success': True, 'message': 'Module already completed'}
    
    def get_analytics_summary(self, user_id):
        """
        Get comprehensive analytics summary
        """
        progress = self.get_progress(user_id)
        
        # Calculate various metrics
        completed = len(progress.get('completed_modules', []))
        in_progress = len(progress.get('in_progress_modules', []))
        upcoming = len(progress.get('upcoming_modules', []))
        total = completed + in_progress + upcoming
        
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        # Estimate completion date
        days_active = 14  # Mock days_active, ideally should calculate from start_date
        avg_modules_per_day = completed / days_active if days_active > 0 else 0
        remaining_modules = in_progress + upcoming
        estimated_days_remaining = int(remaining_modules / avg_modules_per_day) if avg_modules_per_day > 0 else 30
        
        estimated_completion = datetime.now() + timedelta(days=estimated_days_remaining)
        
        return {
            'overall_metrics': {
                'completion_rate': round(completion_rate, 1),
                'modules_completed': completed,
                'modules_total': total,
                'learning_streak': progress.get('learning_streak_days', 0),
                'total_time_hours': round(progress.get('total_learning_time_minutes', 0) / 60, 1)
            },
            'progress_breakdown': {
                'completed': completed,
                'in_progress': in_progress,
                'upcoming': upcoming
            },
            'predictions': {
                'estimated_completion_date': estimated_completion.strftime('%Y-%m-%d'),
                'estimated_days_remaining': estimated_days_remaining,
                'on_track': completion_rate >= 40  #  threshold
            },
            'achievements': progress.get('milestones_achieved', []),
            'recommendations': self._generate_recommendations(progress)
        }
    
    def _generate_recommendations(self, progress):
        """
        Generate personalized recommendations based on progress
        """
        recommendations = []
        
        completion_rate = progress.get('overall_progress', 0)
        streak = progress.get('learning_streak_days', 0)
        
        if completion_rate < 30:
            recommendations.append({
                'type': 'encouragement',
                'message': 'Keep going! You are building great momentum.',
                'action': 'Complete one more module today'
            })
        
        if streak < 3:
            recommendations.append({
                'type': 'engagement',
                'message': 'Build your learning streak!',
                'action': 'Try to learn something every day'
            })
        
        if completion_rate >= 50 and progress.get('assessments_completed', 0) == 0:
            recommendations.append({
                'type': 'assessment',
                'message': 'Time to test your knowledge!',
                'action': 'Take your first assessment'
            })
        
        if progress.get('vr_experiences_completed', 0) == 0:
            recommendations.append({
                'type': 'vr_training',
                'message': 'Try our immersive VR training!',
                'action': 'Launch your first VR experience'
            })
        
        return recommendations
    
    def get_weekly_chart_data(self, user_id):
        """
        Get data for weekly progress chart
        """
        # Mock data - in production, we query historical data
        return {
            'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            'completed_modules': [2, 3, 1, 4, 2, 1, 0],
            'time_spent_minutes': [45, 60, 30, 90, 60, 45, 0]
        }
