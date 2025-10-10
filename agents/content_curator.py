"""
Content Curator Agent - Manages and recommends onboarding content
"""

import boto3
from config import config

class ContentCuratorAgent:
    """
    Manages content discovery, organization, and recommendations
    """
    
    def __init__(self):
        self.s3 = boto3.client('s3', region_name=config.REGION_NAME)
        self.bucket = config.S3_BUCKET
    
    def get_content_by_category(self, category):
        """
        Get content organized by category
        """
        content_categories = {
            'company_culture': {
                'title': 'Company Culture & Values',
                'items': [
                    {'name': 'Welcome Video', 'type': 'video', 'duration': '15 min'},
                    {'name': 'Mission & Vision', 'type': 'document', 'duration': '10 min'},
                    {'name': 'Company History', 'type': 'article', 'duration': '8 min'},
                ]
            },
            'technical': {
                'title': 'Technical Resources',
                'items': [
                    {'name': 'Development Setup Guide', 'type': 'guide', 'duration': '30 min'},
                    {'name': 'Architecture Overview', 'type': 'video', 'duration': '45 min'},
                    {'name': 'Best Practices', 'type': 'document', 'duration': '20 min'},
                ]
            },
            'policies': {
                'title': 'Policies & Procedures',
                'items': [
                    {'name': 'Employee Handbook', 'type': 'document', 'duration': '30 min'},
                    {'name': 'Code of Conduct', 'type': 'document', 'duration': '15 min'},
                    {'name': 'Security Policies', 'type': 'document', 'duration': '20 min'},
                ]
            },
            'tools': {
                'title': 'Tools & Systems',
                'items': [
                    {'name': 'Slack Guide', 'type': 'guide', 'duration': '10 min'},
                    {'name': 'Project Management Tools', 'type': 'video', 'duration': '15 min'},
                    {'name': 'Communication Best Practices', 'type': 'article', 'duration': '12 min'},
                ]
            }
        }
        
        return content_categories.get(category, {})
    
    def search_content(self, query):
        """
        Search for content based on query
        """
        # Simplified search - in production, use vector search or full-text search
        all_content = []
        
        categories = ['company_culture', 'technical', 'policies', 'tools']
        for cat in categories:
            content = self.get_content_by_category(cat)
            if content:
                all_content.extend(content.get('items', []))
        
        # Filter based on query
        query_lower = query.lower()
        results = [
            item for item in all_content 
            if query_lower in item['name'].lower()
        ]
        
        return results
    
    def get_recommended_content(self, user_role, completed_modules):
        """
        Get recommended content based on role and progress
        """
        recommendations = []
        
        # Role-based recommendations
        if 'engineer' in user_role.lower():
            recommendations.extend([
                {'name': 'Code Review Best Practices', 'reason': 'Essential for engineers'},
                {'name': 'System Architecture Deep Dive', 'reason': 'Understanding our stack'},
            ])
        
        if 'sales' in user_role.lower():
            recommendations.extend([
                {'name': 'Product Demo Training', 'reason': 'Core sales skill'},
                {'name': 'Customer Success Stories', 'reason': 'Learn from wins'},
            ])
        
        # Progress-based recommendations
        if len(completed_modules) < 3:
            recommendations.append({
                'name': 'Getting Started Guide',
                'reason': 'Start with the basics'
            })
        
        return recommendations
    
    def list_s3_content(self, prefix=''):
        """
        List content stored in S3 bucket
        """
        try:
            response = self.s3.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix
            )
            
            contents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    contents.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat()
                    })
            
            return contents
        
        except Exception as e:
            print(f"Error listing S3 content: {e}")
            return []
    
    def get_content_stats(self):
        """
        Get statistics about available content
        """
        categories = ['company_culture', 'technical', 'policies', 'tools']
        
        stats = {
            'total_categories': len(categories),
            'content_by_category': {}
        }
        
        for cat in categories:
            content = self.get_content_by_category(cat)
            stats['content_by_category'][cat] = len(content.get('items', []))
        
        stats['total_items'] = sum(stats['content_by_category'].values())
        
        return stats
