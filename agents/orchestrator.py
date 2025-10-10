"""
Orchestrator Agent - Main coordinator for all specialized agents
Uses Bedrock agent setup
"""

import boto3
from botocore.config import Config as BotoConfig
from config import config
import time

class OrchestratorAgent:
    """
    Main orchestrator that coordinates all specialized agents
    """
    
    def __init__(self):
        self.boto_config = BotoConfig(
            region_name=config.REGION_NAME,
            connect_timeout=10,
            read_timeout=config.BEDROCK_TIMEOUT
        )
        self.client = boto3.client('bedrock-agent-runtime', config=self.boto_config)
        self.agent_id = config.AGENT_ID
        self.agent_alias_id = config.AGENT_ALIAS_ID
    
    def ask_agent(self, question, session_id, retries=None):
        """
        Ask the main Bedrock agent with retry logic
        """
        retries = retries or config.API_RETRY_COUNT
        delay = config.API_RETRY_DELAY
        
        for attempt in range(retries):
            try:
                response = self.client.invoke_agent(
                    agentId=self.agent_id,
                    agentAliasId=self.agent_alias_id,
                    sessionId=session_id,
                    inputText=question
                )
                
                response_text = ""
                for event in response['completion']:
                    if 'chunk' in event:
                        response_text += event['chunk']['bytes'].decode('utf-8')
                
                return {
                    'success': True,
                    'response': response_text,
                    'session_id': session_id
                }
            
            except self.client.exceptions.InternalServerException:
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    return {
                        'success': False,
                        'error': 'Service temporarily unavailable',
                        'response': 'Sorry, I am temporarily unavailable. Please try again later.'
                    }
            
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e),
                    'response': f'An error occurred: {str(e)}'
                }
    
    def get_personalized_response(self, question, user_profile, session_id):
        """
        Get personalized response based on user profile
        """
        # Enhance question with user context
        context = f"User Role: {user_profile.get('role', 'Unknown')}. "
        context += f"Department: {user_profile.get('department', 'Unknown')}. "
        context += f"Question: {question}"
        
        return self.ask_agent(context, session_id)
    
    def route_to_specialist(self, query_type, question, session_id):
        """
        Route questions to specialized agents based on query type
        """
        routing_prompts = {
            'learning_path': f"Create a personalized learning path. {question}",
            'assessment': f"Provide skills assessment guidance. {question}",
            'content': f"Find and recommend relevant content. {question}",
            'progress': f"Analyze and report on progress. {question}"
        }
        
        enhanced_question = routing_prompts.get(query_type, question)
        return self.ask_agent(enhanced_question, session_id)
