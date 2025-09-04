from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Custom admin class for User model
class CustomUserAdmin(UserAdmin):
    """
    Custom admin configuration for User model.
    Extends the default UserAdmin to include the must_change_password field.
    """
    
    # Fields to display in the user list view
    list_display = ('username', 'email', 'first_name', 'last_name', 
                    'is_staff', 'must_change_password', 'last_login')
    
    # Fields that can be used to filter the user list
    list_filter = UserAdmin.list_filter + ('must_change_password',)
    
    # Fields that are editable directly in the list view
    list_editable = ('must_change_password',)
    
    # Add must_change_password to the user edit form
    fieldsets = UserAdmin.fieldsets + (
        ('Password Change Settings', {
            'fields': ('must_change_password',),
            'description': 'Control whether the user must change their password on next login.'
        }),
    )
    
    # Add must_change_password to the user creation form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Password Change Settings', {
            'fields': ('must_change_password',),
            'description': 'Set whether the user must change their password on first login.'
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to handle password change requirements.
        When creating a new user through admin, set must_change_password to True by default.
        """
        if not change:  # If creating a new user
            # New users created by admin should change password by default
            if not hasattr(obj, 'must_change_password'):
                obj.must_change_password = True
        
        super().save_model(request, obj, form, change)

# Register the custom User model with the custom admin class
admin.site.register(User, CustomUserAdmin)

# Customize admin site header and title
admin.site.site_header = "Annotation System Administration"
admin.site.site_title = "Annotation Admin"
admin.site.index_title = "Welcome to Annotation Administration"
