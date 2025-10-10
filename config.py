"""
Configuration file for Onboarding AI Assistant

"""

import os
from dataclasses import dataclass

@dataclass
class Config:
    
    AGENT_ID = 'REMOVED'
    AGENT_ALIAS_ID = 'REMOVED'
    REGION_NAME = 'us-east-1'
    
    # S3 bucket
    S3_BUCKET = 'storevoice'
    
    # DynamoDB tables created in AWS
    DYNAMODB_ONBOARDING_TABLE = 'onboarding-progress'
    DYNAMODB_KNOWLEDGE_TABLE = 'knowledge-base'
    
    # SES configuration
    SES_SENDER_EMAIL = 'biswarup.mukherjee@company.com'  # this is a template
    
    # Application settings
    COMPANY_NAME = 'Company'
    APP_TITLE = 'PEP EASY ONBOARD'
    
    # Feature flags
    ENABLE_VR_TRAINING = True
    ENABLE_PROGRESS_TRACKING = True
    ENABLE_EMAIL_AUTOMATION = True
    ENABLE_SCHEDULER = True

config = Config()
