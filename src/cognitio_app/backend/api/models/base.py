"""
This module contains the base model classes that are inherited by other models.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class TimeStampedModel(models.Model):
    """
    Abstract base class that provides self-updating 'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UUIDModel(TimeStampedModel):
    """
    Abstract base class with UUID primary key and timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True


class OwnedModel(UUIDModel):
    """
    Abstract base class for models that are owned by a user.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        abstract = True 


class ActivityLog(UUIDModel):
    """
    Abstract base class for activity logs.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.created_at}"
    
    def save(self, *args, **kwargs):
        # Custom save logic can be added here
        super().save(*args, **kwargs)  