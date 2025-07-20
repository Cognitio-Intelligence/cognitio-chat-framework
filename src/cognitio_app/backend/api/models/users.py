"""
This module contains models related to user preferences, sessions, and feedback.
"""

from typing import Dict, Any
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from .base import TimeStampedModel, UUIDModel

User = get_user_model()


class UserPreferences(TimeStampedModel):
    """
    User preferences for data source management.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='data_preferences')
    
    # Default connection settings
    default_query_timeout = models.IntegerField(default=300)
    default_max_rows_preview = models.IntegerField(default=1000)
    default_connection_timeout = models.IntegerField(default=30)
    
    # UI preferences
    preferred_date_format = models.CharField(max_length=50, default='YYYY-MM-DD')
    preferred_number_format = models.CharField(max_length=50, default='en-US')
    show_system_tables = models.BooleanField(default=False)
    auto_refresh_schema = models.BooleanField(default=True)
    
    # Privacy settings
    anonymize_sample_data = models.BooleanField(default=True)
    log_query_history = models.BooleanField(default=True)
    share_usage_analytics = models.BooleanField(default=False)
    
    # Notification preferences
    notify_connection_errors = models.BooleanField(default=True)
    notify_schema_changes = models.BooleanField(default=True)
    notify_query_completion = models.BooleanField(default=False)
    
    # Advanced settings
    custom_settings = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"


class UserSession(UUIDModel):
    """
    Track user sessions for analytics and behavior analysis.
    """
    
    SESSION_TYPES = [
        ('web', 'Web Browser'),
        ('mobile', 'Mobile App'),
        ('api', 'API Access'),
        ('desktop', 'Desktop App'),
    ]
    
    DEVICE_TYPES = [
        ('desktop', 'Desktop Computer'),
        ('mobile', 'Mobile Device'),
        ('tablet', 'Tablet'),
        ('unknown', 'Unknown Device'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics_sessions')
    
    # Session identification
    session_id = models.CharField(max_length=255, unique=True, help_text="Unique session identifier")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='web')
    
    # Device and browser information
    ip_address = models.GenericIPAddressField(help_text="User's IP address")
    user_agent = models.TextField(help_text="Browser user agent string")
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES, default='unknown')
    browser_name = models.CharField(max_length=100, blank=True, help_text="Browser name (Chrome, Firefox, etc.)")
    browser_version = models.CharField(max_length=50, blank=True, help_text="Browser version")
    operating_system = models.CharField(max_length=100, blank=True, help_text="Operating system")
    screen_resolution = models.CharField(max_length=20, blank=True, help_text="Screen resolution (e.g., 1920x1080)")
    
    # Geographic information
    country = models.CharField(max_length=100, blank=True, help_text="Country based on IP")
    city = models.CharField(max_length=100, blank=True, help_text="City based on IP")
    user_timezone = models.CharField(max_length=50, blank=True, help_text="User's timezone")
    
    # Session timing
    session_start = models.DateTimeField(auto_now_add=True)
    session_end = models.DateTimeField(null=True, blank=True, help_text="When session ended")
    last_activity = models.DateTimeField(auto_now=True, help_text="Last recorded activity")
    duration_seconds = models.IntegerField(default=0, help_text="Total session duration in seconds")
    
    # Activity metrics
    page_views = models.IntegerField(default=0, help_text="Number of pages viewed")
    actions_performed = models.IntegerField(default=0, help_text="Number of actions performed")
    data_sources_accessed = models.IntegerField(default=0, help_text="Number of data sources accessed")
    queries_executed = models.IntegerField(default=0, help_text="Number of queries executed")
    files_uploaded = models.IntegerField(default=0, help_text="Number of files uploaded")
    insights_generated = models.IntegerField(default=0, help_text="Number of insights generated")
    
    # Engagement metrics
    is_bounce = models.BooleanField(default=False, help_text="True if user left without meaningful interaction")
    is_active_session = models.BooleanField(default=True, help_text="Whether session is currently active")
    referrer_url = models.URLField(blank=True, help_text="URL that referred user to the app")
    entry_page = models.CharField(max_length=255, blank=True, help_text="First page user visited")
    exit_page = models.CharField(max_length=255, blank=True, help_text="Last page user visited")

    class Meta:
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-session_start']
        indexes = [
            models.Index(fields=['user', '-session_start']),
            models.Index(fields=['session_id']),
            models.Index(fields=['is_active_session']),
            models.Index(fields=['session_start']),
            models.Index(fields=['device_type']),
            models.Index(fields=['country']),
            models.Index(fields=['is_bounce']),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.user.username}"

    def end_session(self):
        """End the session and calculate duration."""
        if not self.session_end:
            self.session_end = timezone.now()
            self.is_active_session = False
            if self.session_start:
                self.duration_seconds = int((self.session_end - self.session_start).total_seconds())
            self.save()

    def get_duration_minutes(self) -> float:
        """Get session duration in minutes."""
        return self.duration_seconds / 60.0 if self.duration_seconds else 0.0