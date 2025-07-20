"""
Chat views for WebLLM Chat Application.

Contains view functions for chat sessions and WebLLM integration.
"""

import logging
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_chat_sessions(request):
    """Get chat sessions."""
    try:
        sessions = ChatSession.objects.all()[:10]  # Limit to 10 recent sessions
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                'id': str(session.id),
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat(),
            })
        
        return Response({
            'success': True,
            'sessions': sessions_data
        })
        
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_chat_session(request):
    """Create a new chat session."""
    try:
        title = request.data.get('title', 'New Chat')
        session = ChatSession.objects.create(title=title)
        
        return Response({
            'success': True,
            'session': {
                'id': str(session.id),
                'title': session.title,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_session_messages(request, session_id):
    """Get messages from a chat session."""
    try:
        session = ChatSession.objects.get(id=session_id)
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        messages_data = []
        for message in messages:
            messages_data.append({
                'id': str(message.id),
                'message_type': message.message_type,
                'message': message.message,
                'response': message.response,
                'created_at': message.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'messages': messages_data
        })
        
    except ChatSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_chat_message(request, session_id):
    """Send a message and create a placeholder response."""
    try:
        session = ChatSession.objects.get(id=session_id)
        content = request.data.get('content')
        message_type = request.data.get('message_type', 'user')
        metadata = request.data.get('metadata', {})
        
        if not content:
            return Response({
                'success': False,
                'error': 'Content is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create message record
        chat_message = ChatMessage.objects.create(
            session=session,
            content=content,
            message_type=message_type,
            metadata=metadata
        )
        
        return Response({
            'success': True,
            'message': {
                'id': str(chat_message.id),
                'content': chat_message.content,
                'message_type': chat_message.message_type,
                'metadata': chat_message.metadata,
                'created_at': chat_message.created_at.isoformat()
            }
        })
        
    except ChatSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error sending chat message: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_chat_session(request, session_id):
    """Delete a chat session."""
    try:
        session = ChatSession.objects.get(id=session_id)
        session.delete()
        
        return Response({
            'success': True,
            'message': 'Session deleted successfully'
        })
        
    except ChatSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def update_session_title(request, session_id):
    """Update a chat session title."""
    try:
        session = ChatSession.objects.get(id=session_id)
        if not session:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        title = request.data.get('title')
        if not title:
            return Response({
                'success': False,
                'error': 'Title is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        session.title = title
        session.save()
        
        return Response({
            'success': True,
            'message': 'Title updated successfully'
        })
        
    except ChatSession.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error updating session title: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)