from django.db import models


class AnnotationQueue(models.Model):
    """
    Model representing an annotation queue from Langfuse API.
    
    This model provides a data structure for annotation queue information
    fetched from the Langfuse API. Currently used for data representation
    only - no database persistence for MVP.
    """
    
    # Langfuse queue identifier (primary key from API)
    queue_id = models.CharField(max_length=255, unique=True, help_text="Langfuse queue ID")
    
    # Basic queue information
    name = models.CharField(max_length=255, help_text="Queue display name")
    description = models.TextField(blank=True, null=True, help_text="Queue description")
    
    # Metadata from API
    created_at = models.DateTimeField(help_text="Queue creation timestamp from API")
    updated_at = models.DateTimeField(help_text="Queue last update timestamp from API")
    
    # Additional fields for future use
    is_active = models.BooleanField(default=True, help_text="Whether queue is active")
    
    # Django model metadata
    created = models.DateTimeField(auto_now_add=True, help_text="Local creation timestamp")
    modified = models.DateTimeField(auto_now=True, help_text="Local modification timestamp")
    
    class Meta:
        verbose_name = "Annotation Queue"
        verbose_name_plural = "Annotation Queues"
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['queue_id']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """String representation of the annotation queue."""
        return f"{self.name} ({self.queue_id})"
    
    @classmethod
    def from_api_data(cls, api_data: dict) -> 'AnnotationQueue':
        """
        Create an AnnotationQueue instance from Langfuse API data.
        
        Args:
            api_data (dict): Raw data from Langfuse API
            
        Returns:
            AnnotationQueue: Model instance (not saved to database)
        """
        from datetime import datetime
        
        # Parse timestamps from API
        created_at = datetime.fromisoformat(api_data['createdAt'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(api_data['updatedAt'].replace('Z', '+00:00'))
        
        return cls(
            queue_id=api_data['id'],
            name=api_data['name'],
            description=api_data.get('description'),
            created_at=created_at,
            updated_at=updated_at,
            is_active=True  # Assume active by default
        )
    
    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary for template context.
        
        Returns:
            dict: Serialized queue data
        """
        return {
            'queue_id': self.queue_id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
        }
    
    def get_absolute_url(self):
        """Get the absolute URL for this queue detail view."""
        from django.urls import reverse
        return reverse('annotation_tool:queue_detail', kwargs={'queue_id': self.queue_id})


class AnnotationQueueItem(models.Model):
    """
    Model representing an item in an annotation queue.
    
    This model provides structure for queue items fetched from Langfuse API.
    Currently used for data representation only - no database persistence for MVP.
    """
    
    # Item identifiers
    item_id = models.CharField(max_length=255, unique=True, help_text="Langfuse item ID")
    queue_id = models.CharField(max_length=255, help_text="Parent queue ID")
    object_id = models.CharField(max_length=255, help_text="ID of object being annotated")
    
    # Item metadata
    object_type = models.CharField(max_length=50, help_text="Type of object (TRACE, SESSION, etc.)")
    status = models.CharField(max_length=50, help_text="Item status (PENDING, COMPLETED, etc.)")
    
    # Timestamps
    created_at = models.DateTimeField(help_text="Item creation timestamp from API")
    updated_at = models.DateTimeField(help_text="Item last update timestamp from API")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Item completion timestamp")
    
    # Django model metadata
    created = models.DateTimeField(auto_now_add=True, help_text="Local creation timestamp")
    modified = models.DateTimeField(auto_now=True, help_text="Local modification timestamp")
    
    class Meta:
        verbose_name = "Annotation Queue Item"
        verbose_name_plural = "Annotation Queue Items"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['item_id']),
            models.Index(fields=['queue_id']),
            models.Index(fields=['status']),
            models.Index(fields=['object_type']),
        ]
    
    def __str__(self):
        """String representation of the queue item."""
        return f"{self.object_type} {self.object_id} ({self.status})"
    
    @classmethod
    def from_api_data(cls, api_data: dict) -> 'AnnotationQueueItem':
        """
        Create an AnnotationQueueItem instance from Langfuse API data.
        
        Args:
            api_data (dict): Raw data from Langfuse API
            
        Returns:
            AnnotationQueueItem: Model instance (not saved to database)
        """
        from datetime import datetime
        
        # Parse timestamps from API
        created_at = datetime.fromisoformat(api_data['createdAt'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(api_data['updatedAt'].replace('Z', '+00:00'))
        
        completed_at = None
        if api_data.get('completedAt'):
            completed_at = datetime.fromisoformat(api_data['completedAt'].replace('Z', '+00:00'))
        
        return cls(
            item_id=api_data['id'],
            queue_id=api_data['queueId'],
            object_id=api_data['objectId'],
            object_type=api_data['objectType'],
            status=api_data['status'],
            created_at=created_at,
            updated_at=updated_at,
            completed_at=completed_at
        )
    
    def to_dict(self) -> dict:
        """
        Convert model instance to dictionary for template context.
        
        Returns:
            dict: Serialized item data
        """
        return {
            'item_id': self.item_id,
            'queue_id': self.queue_id,
            'object_id': self.object_id,
            'object_type': self.object_type,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at,
        }
    
    def get_display_status(self) -> str:
        """
        Get a user-friendly display version of the status.
        
        Returns:
            str: Formatted status for display
        """
        if not self.status:
            return "Unknown"
        return self.status.title()
    
    def get_display_object_type(self) -> str:
        """
        Get a user-friendly display version of the object type.
        
        Returns:
            str: Formatted object type for display
        """
        if not self.object_type:
            return "Unknown"
        return self.object_type.title()
    
    def is_completed(self) -> bool:
        """
        Check if the queue item is completed.
        
        Returns:
            bool: True if the item is completed
        """
        return self.status == 'COMPLETED'
    
    def is_pending(self) -> bool:
        """
        Check if the queue item is pending.
        
        Returns:
            bool: True if the item is pending
        """
        return self.status == 'PENDING'
