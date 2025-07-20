"""
API views package for WebLLM Chat Application.

Contains view functions and classes for WebLLM chat endpoints.
"""

from .chat_views import (
    get_chat_sessions,
    create_chat_session,
    get_session_messages,
    send_chat_message,
    delete_chat_session,
    update_session_title
)

from .webllm_views import (
    webllm_generate,
    webllm_chat,
    webllm_status,
    webllm_diagnostic,
    webllm_insights,
    webllm_local_log
)

from .auth_views import (
    get_csrf_token,
    refresh_token,
    login_with_cloud_api,
    signup_with_cloud_api,
    auth_status,
    logout_user

)



__all__ = [
    # Chat views
    'get_chat_sessions',
    'create_chat_session',
    'get_session_messages',
    'send_chat_message',
    'delete_chat_session',
    'update_session_title',
    # WebLLM views
    'webllm_generate',
    'webllm_chat',
    'webllm_status',
    'webllm_diagnostic',
    'webllm_insights',
    'webllm_local_log',
    # Auth views
    'get_csrf_token',
    'refresh_token',
    'login_with_cloud_api',
    'signup_with_cloud_api',
    'auth_status',
    'logout_user'
] 