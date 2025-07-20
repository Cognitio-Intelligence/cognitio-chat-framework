"""
Serializers for WebLLM chat functionality.
"""

from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for ChatSession model."""
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for ChatMessage model."""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'session', 'content', 'message_type', 'created_at', 'processing_time_ms', 'tokens_used', 'metadata']
        read_only_fields = ['id', 'created_at'] 