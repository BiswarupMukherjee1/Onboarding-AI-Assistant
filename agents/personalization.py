"""
Personalization Agent to create an adaptive learning experiences
"""

import boto3
from config import config
import json

class PersonalizationAgent:
    """
    Specialized agent for personalization and adaptive learning
    """
    
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb', region_name=config.REGION_NAME)
        self.table = None
        
        # Only initialize DynamoDB if tracking is enabled
        if config.ENABLE_PROGRESS_TRACKING:
            try:
                self.table = self.dynamodb.Table(config.DYNAMODB_ONBOARDING_TABLE)
            except:
                print("DynamoDB table not available. Progress tracking disabled.")
    
    def create_learning_path(self, user_profile):
        """
        Create personalized learning path based on user profile
        """
        role = user_profile.get('role', '').lower()
        experience = user_profile.get('experience_level', 'beginner')
        
        # Define learning modules based on role
        learning_paths = {
            'engineer': [
                {'module': 'Company Culture', 'duration': '2 hours', 'priority': 'high'},
                {'module': 'Technical Stack Overview', 'duration': '4 hours', 'priority': 'high'},
                {'module': 'Development Environment Setup', 'duration': '3 hours', 'priority': 'high'},
                {'module': 'Code Review Process', 'duration': '2 hours', 'priority': 'medium'},
                {'module': 'Deployment Procedures', 'duration': '2 hours', 'priority': 'medium'},
            ],
            'sales': [
                {'module': 'Company Culture', 'duration': '2 hours', 'priority': 'high'},
                {'module': 'Product Knowledge', 'duration': '4 hours', 'priority': 'high'},
                {'module': 'Sales Process & CRM', 'duration': '3 hours', 'priority': 'high'},
                {'module': 'Customer Success Stories', 'duration': '2 hours', 'priority': 'medium'},
            ],
            'marketing': [
                {'module': 'Company Culture', 'duration': '2 hours', 'priority': 'high'},
                {'module': 'Brand Guidelines', 'duration': '3 hours', 'priority': 'high'},
                {'module': 'Marketing Tools', 'duration': '2 hours', 'priority': 'high'},
                {'module': 'Campaign Processes', 'duration': '2 hours', 'priority': 'medium'},
            ],
            'default': [
                {'module': 'Company Culture', 'duration': '2 hours', 'priority': 'high'},
                {'module': 'Company Policies', 'duration': '1 hour', 'priority': 'high'},
                {'module': 'Team Introduction', 'duration': '1 hour', 'priority': 'high'},
                {'module': 'Tools & Systems', 'duration': '2 hours', 'priority': 'medium'},
            ]
        }
        
        # Get appropriate learning path
        path = learning_paths.get(role, learning_paths['default'])
        
        # Adjust based on experience level
        if experience == 'senior':
            # Filter out basic modules for senior employees
            path = [m for m in path if m['module'] not in ['Company Culture']]
        
        return {
            'learning_path': path,
            'estimated_completion': self._calculate_total_time(path),
            'personalization_factors': {
                'role': role,
                'experience': experience
            }
        }
    
    def _calculate_total_time(self, modules):
        """Calculate total estimated time for learning path"""
        total_hours = 0
        for module in modules:
            duration = module['duration'].split()[0]
            total_hours += int(duration)
        return f"{total_hours} hours"
    
    def get_recommendations(self, user_id, current_progress):
        """
        Get personalized content recommendations based on progress
        """
        recommendations = []
        
        # Analyze current progress
        completion_rate = current_progress.get('completion_rate', 0)
        
        if completion_rate < 30:
            recommendations.append({
                'type': 'encouragement',
                'message': 'Great start! Keep up the momentum.',
                'action': 'Continue with your current module'
            })
        elif completion_rate < 70:
            recommendations.append({
                'type': 'milestone',
                'message': 'You are halfway there! 🎉',
                'action': 'Take a short break and review what you have learned'
            })
        else:
            recommendations.append({
                'type': 'completion',
                'message': 'Almost done! You are doing great!',
                'action': 'Prepare for final assessment'
            })
        
        return recommendations
    
    def save_progress(self, user_id, progress_data):
        """
        Save user progress to DynamoDB
        """
        if not self.table:
            return {'success': False, 'message': 'Progress tracking not available'}
        
        try:
            self.table.put_item(
                Item={
                    'user_id': user_id,
                    'progress': json.dumps(progress_data),
                    'last_updated': str(boto3.dynamodb.types.datetime.datetime.now())
                }
            )
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_progress(self, user_id):
        """
        Retrieve user progress from DynamoDB
        """
        if not self.table:
            return None
        
        try:
            response = self.table.get_item(Key={'user_id': user_id})
            if 'Item' in response:
                return json.loads(response['Item']['progress'])
            return None
        except Exception as e:
            print(f"Error retrieving progress: {e}")
            return None
