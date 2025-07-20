"""
Django models for WebLLM Chat Application.

This package contains simplified models for basic chat functionality with WebLLM.
"""

# Import base models
from .base import TimeStampedModel, UUIDModel, OwnedModel, ActivityLog

# Import chat models
from .chat import ChatSession, ChatMessage

from .system import ErrorLog

from .users import UserPreferences,UserSession

__all__ = [
    # Base
    'TimeStampedModel', 'UUIDModel', 'OwnedModel', 'ActivityLog',
    
    # System
    'ErrorLog',
    
    # Users
    'UserPreferences', 'UserSession',
    
    # Chat
    'ChatSession', 'ChatMessage',


] 