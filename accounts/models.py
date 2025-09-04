from django.db import models
from django.contrib.auth.models import AbstractUser

# Custom User model extending Django's AbstractUser
class User(AbstractUser):
    """
    Custom User model that extends Django's built-in AbstractUser.
    
    This model adds a must_change_password field to track whether
    a user needs to change their password on next login.
    """
    
    # Boolean field to track if user must change password
    # Default is True, meaning new users created by admin must change password
    must_change_password = models.BooleanField(
        default=True,
        help_text="If checked, user will be forced to change password on next login"
    )
    
    class Meta:
        # Specify the database table name (optional)
        db_table = 'accounts_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        """String representation of the User"""
        return self.username
