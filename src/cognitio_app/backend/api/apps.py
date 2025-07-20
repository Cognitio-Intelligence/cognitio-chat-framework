"""
Django app configuration for the API backend.
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration for the API app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cognitio_app.backend.api'
    verbose_name = 'WebLLM API'
