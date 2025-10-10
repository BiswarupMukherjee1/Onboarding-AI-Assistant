"""
 Features for Onboarding AI Assistant
"""

from .vr_training import VRTrainingEngine
from .progress_tracker import ProgressTracker
from .scheduler import MeetingScheduler
from .email_automation import EmailAutomation

__all__ = [
    'VRTrainingEngine',
    'ProgressTracker',
    'MeetingScheduler',
    'EmailAutomation'
]
