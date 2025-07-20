"""
This module contains models related to system metrics, and error logging.
"""

from typing import Dict, Any
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from .base import TimeStampedModel, UUIDModel
from .users import UserSession

User = get_user_model()

class ErrorLog(UUIDModel):
    """
    Track application errors for debugging and analytics.
    """
    
    ERROR_LEVELS = [
        ('debug', 'Debug'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    ERROR_CATEGORIES = [
        ('authentication', 'Authentication'),
        ('data_processing', 'Data Processing'),
        ('database', 'Database'),
        ('api', 'API'),
        ('ui', 'User Interface'),
        ('integration', 'Integration'),
        ('performance', 'Performance'),
        ('validation', 'Validation'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='error_logs')
    session = models.ForeignKey(UserSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='error_logs')
    
    # Error details
    error_level = models.CharField(max_length=20, choices=ERROR_LEVELS)
    error_category = models.CharField(max_length=30, choices=ERROR_CATEGORIES)
    error_code = models.CharField(max_length=50, blank=True, help_text="Application-specific error code")
    error_message = models.TextField(help_text="Error message")
    error_details = models.TextField(blank=True, help_text="Detailed error information")
    
    # Context
    url = models.URLField(blank=True, help_text="URL where error occurred")
    user_agent = models.TextField(blank=True, help_text="User agent string")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Technical details
    stack_trace = models.TextField(blank=True, help_text="Stack trace if available")
    request_data = models.JSONField(default=dict, blank=True, help_text="Request data that caused error")
    response_data = models.JSONField(default=dict, blank=True, help_text="Response data if available")
    
    # Resolution tracking
    is_resolved = models.BooleanField(default=False, help_text="Whether error has been resolved")
    resolution_notes = models.TextField(blank=True, help_text="Notes about error resolution")
    resolved_at = models.DateTimeField(null=True, blank=True, help_text="When error was resolved")
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='resolved_errors',
        help_text="Who resolved the error"
    )
    
    # Occurrence tracking
    occurrence_count = models.IntegerField(default=1, help_text="Number of times this error occurred")
    first_occurred = models.DateTimeField(auto_now_add=True)
    last_occurred = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Error Log'
        verbose_name_plural = 'Error Logs'
        ordering = ['-last_occurred']
        indexes = [
            models.Index(fields=['error_level', '-last_occurred']),
            models.Index(fields=['error_category', '-last_occurred']),
            models.Index(fields=['user', '-last_occurred']),
            models.Index(fields=['is_resolved']),
            models.Index(fields=['error_code']),
        ]

    def __str__(self):
        return f"{self.error_level.upper()}: {self.error_message[:100]}"

    def mark_resolved(self, resolved_by: User, notes: str = ""):
        """Mark error as resolved."""
        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by
        self.resolution_notes = notes
        self.save()