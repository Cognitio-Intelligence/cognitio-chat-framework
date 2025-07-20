"""
This module contains models related to chat sessions, messages, query executions.
"""

import uuid
from typing import Dict, Any, Optional
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from .base import TimeStampedModel, UUIDModel


User = get_user_model()


class ChatSession(UUIDModel):
    """
    Represents a chat session between user and AI assistant.
    """
    
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, help_text="Session title (auto-generated or user-defined)")
    
    # Session metadata
    is_active = models.BooleanField(default=True, help_text="Whether this session is currently active")
    message_count = models.IntegerField(default=0, help_text="Total number of messages in this session")
    
    system_prompt = models.TextField(
        blank=True, 
        help_text="Custom system prompt for this session"
    )
    
    class Meta:
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_last_message_preview(self) -> str:
        """Get a preview of the last message in this session."""
        last_message = self.messages.order_by('-created_at').first()
        if last_message:
            content = last_message.content[:100]
            return content + "..." if len(last_message.content) > 100 else content
        return "No messages yet"


class ChatMessage(UUIDModel):
    """
    Individual message in a chat session.
    """
    
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('assistant', 'Assistant Message'),
        ('system', 'System Message'),
        ('error', 'Error Message'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='chat_messages')
    
    # Message content
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField(help_text="Message content")
    
    # Processing metadata
    processing_time_ms = models.IntegerField(null=True, blank=True, help_text="Time taken to process this message")
    tokens_used = models.IntegerField(null=True, blank=True, help_text="Number of tokens used for AI processing")

    # WebLLM and general metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for this message (model info, usage stats, etc.)"
    )
    
    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['message_type']),
        ]
    
    def __str__(self):
        return f"{self.get_message_type_display()} in {self.session.title}"