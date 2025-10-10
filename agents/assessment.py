"""
Assessment Agent - Skills evaluation and testing
"""

import boto3
from config import config
import json
import random

class AssessmentAgent:
    """
    Manages skills assessments and evaluations
    """
    
    def __init__(self):
        self.dynamodb = None
        self.table = None
        
        if config.ENABLE_ASSESSMENTS:
            try:
                self.dynamodb = boto3.resource('dynamodb', region_name=config.REGION_NAME)
                self.table = self.dynamodb.Table(config.DYNAMODB_ASSESSMENTS_TABLE)
            except:
                print("Assessment table not available. Assessments disabled.")
    
    def get_available_assessments(self, user_role):
        """
        Get list of available assessments for user role
        """
        assessments = {
            'engineer': [
                {
                    'id': 'tech_001',
                    'name': 'Technical Fundamentals',
                    'duration': '30 min',
                    'questions': 20,
                    'difficulty': 'intermediate',
                    'status': 'available'
                },
                {
                    'id': 'code_001',
                    'name': 'Coding Best Practices',
                    'duration': '45 min',
                    'questions': 15,
                    'difficulty': 'intermediate',
                    'status': 'available'
                },
                {
                    'id': 'arch_001',
                    'name': 'System Architecture',
                    'duration': '40 min',
                    'questions': 25,
                    'difficulty': 'advanced',
                    'status': 'locked'
                }
            ],
            'sales': [
                {
                    'id': 'product_001',
                    'name': 'Product Knowledge',
                    'duration': '25 min',
                    'questions': 30,
                    'difficulty': 'beginner',
                    'status': 'available'
                },
                {
                    'id': 'sales_001',
                    'name': 'Sales Process',
                    'duration': '30 min',
                    'questions': 20,
                    'difficulty': 'intermediate',
                    'status': 'available'
                }
            ],
            'default': [
                {
                    'id': 'culture_001',
                    'name': 'Company Culture Quiz',
                    'duration': '15 min',
                    'questions': 15,
                    'difficulty': 'beginner',
                    'status': 'available'
                },
                {
                    'id': 'policy_001',
                    'name': 'Policies & Compliance',
                    'duration': '20 min',
                    'questions': 20,
                    'difficulty': 'beginner',
                    'status': 'available'
                }
            ]
        }
        
        role_key = 'engineer' if 'engineer' in user_role.lower() else \
                   'sales' if 'sales' in user_role.lower() else 'default'
        
        return assessments.get(role_key, assessments['default'])
    
    def get_assessment_questions(self, assessment_id):
        """
        Get questions for a specific assessment
        """
        # Sample question bank
        question_banks = {
            'culture_001': [
                {
                    'id': 1,
                    'question': 'What is our company\'s primary mission?',
                    'type': 'multiple_choice',
                    'options': [
                        'Maximize profits',
                        'Deliver innovative solutions to customers',
                        'Expand globally',
                        'Reduce costs'
                    ],
                    'correct_answer': 1
                },
                {
                    'id': 2,
                    'question': 'Which value is most important in our company culture?',
                    'type': 'multiple_choice',
                    'options': [
                        'Competition',
                        'Individual achievement',
                        'Collaboration and teamwork',
                        'Speed over quality'
                    ],
                    'correct_answer': 2
                }
            ],
            'tech_001': [
                {
                    'id': 1,
                    'question': 'What is the recommended approach for code reviews?',
                    'type': 'multiple_choice',
                    'options': [
                        'Review only critical bugs',
                        'All code must be reviewed before merging',
                        'Reviews are optional',
                        'Only senior developers review code'
                    ],
                    'correct_answer': 1
                }
            ]
        }
        
        return question_banks.get(assessment_id, [])
    
    def submit_assessment(self, user_id, assessment_id, answers):
        """
        Submit assessment and calculate score
        """
        questions = self.get_assessment_questions(assessment_id)
        
        if not questions:
            return {'success': False, 'error': 'Assessment not found'}
        
        # Calculate score
        correct = 0
        total = len(questions)
        
        for i, question in enumerate(questions):
            if i < len(answers) and answers[i] == question['correct_answer']:
                correct += 1
        
        score = (correct / total) * 100
        passed = score >= 70  # 70% passing grade
        
        result = {
            'success': True,
            'assessment_id': assessment_id,
            'user_id': user_id,
            'score': score,
            'correct_answers': correct,
            'total_questions': total,
            'passed': passed,
            'feedback': self._generate_feedback(score)
        }
        
        # Save result to DynamoDB/ or any other database can be used
        if self.table:
            try:
                self.table.put_item(Item={
                    'user_id': user_id,
                    'assessment_id': assessment_id,
                    'result': json.dumps(result)
                })
            except Exception as e:
                print(f"Error saving assessment result: {e}")
        
        return result
    
    def _generate_feedback(self, score):
        """Generate feedback based on score"""
        if score >= 90:
            return "Excellent! You have demonstrated mastery of this topic."
        elif score >= 80:
            return "Great job! You have a strong understanding of this material."
        elif score >= 70:
            return "Good work! You passed the assessment. Review the materials to strengthen your knowledge."
        else:
            return "You did not pass this time. Please review the materials and try again."
    
    def get_assessment_history(self, user_id):
        """Get user's assessment history"""
        if not self.table:
            return []
        
        try:
            response = self.table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
            
            return response.get('Items', [])
        except Exception as e:
            print(f"Error retrieving assessment history: {e}")
            return []
