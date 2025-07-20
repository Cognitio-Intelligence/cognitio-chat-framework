"""
API URL Configuration for WebLLM Chat Application.
"""
from django.urls import path, include
from django.http import JsonResponse

from .views import chat_views, webllm_views, auth_views

app_name = 'api'


def health_check(request):
    """Health check endpoint for the backend API."""
    return JsonResponse({
        'status': 'healthy',
        'service': 'WebLLM Chat Backend API',
        'version': '1.0.0'
    })

# Auth URL patterns
auth_patterns = [
    path('csrf-token/', auth_views.get_csrf_token, name='get_csrf_token'),
    path('refresh-token/', auth_views.refresh_token, name='refresh_token'),
    path('login/', auth_views.login_with_cloud_api, name='login_with_cloud_api'),
    path('signup/', auth_views.signup_with_cloud_api, name='signup_with_cloud_api'),
    path('status/', auth_views.auth_status, name='auth_status'),
    path('logout/', auth_views.logout_user, name='logout_user'),
]

# Chat URL patterns
chat_patterns = [
    path('sessions/', chat_views.get_chat_sessions, name='get_chat_sessions'),
    path('sessions/create/', chat_views.create_chat_session, name='create_chat_session'),
    path('sessions/<str:session_id>/', chat_views.get_session_messages, name='get_session_messages'),
    path('sessions/<str:session_id>/send/', chat_views.send_chat_message, name='send_chat_message'),
    path('sessions/<str:session_id>/delete/', chat_views.delete_chat_session, name='delete_chat_session'),
    path('sessions/<str:session_id>/update/', chat_views.update_session_title, name='update_session_title'),
]

# WebLLM URL patterns
webllm_patterns = [
    path('generate/', webllm_views.webllm_generate, name='generate'),
    path('chat/', webllm_views.webllm_chat, name='chat'),
    path('status/', webllm_views.webllm_status, name='webllm_status'),
    path('diagnostic/', webllm_views.webllm_diagnostic, name='webllm_diagnostic'),
    path('insights/', webllm_views.webllm_insights, name='webllm_insights'),
    path('webllm-local-log/', webllm_views.webllm_local_log, name='webllm_local_log'),
    path('processing/', webllm_views.webllm_processing, name='webllm_processing'),
]

# Main URL patterns
urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # API endpoints
    path('auth/', include(auth_patterns)),
    path('chat/', include(chat_patterns)),
    path('webllm/', include(webllm_patterns)),
]
