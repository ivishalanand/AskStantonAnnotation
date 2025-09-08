"""
Permission utilities for the admin tools platform.
Provides helper functions for checking user permissions for different tools.
"""

from django.contrib.auth.models import Group
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


def user_has_tool_permission(user, tool_name):
    """
    Check if a user has permission to access a specific tool.
    
    Args:
        user: Django User instance
        tool_name: String name of the tool ('annotation' or 'session_viewer')
    
    Returns:
        Boolean: True if user has access, False otherwise
    """
    # Superusers have access to all tools
    if user.is_superuser:
        return True
    
    # Check if user is in the appropriate group
    if tool_name == 'annotation':
        return user.groups.filter(name='annotation_users').exists()
    elif tool_name == 'session_viewer':
        return user.groups.filter(name='session_viewers').exists()
    
    return False


def get_user_available_tools(user):
    """
    Get a list of tools the user has access to.
    
    Args:
        user: Django User instance
        
    Returns:
        List of tool names the user can access
    """
    available_tools = []
    
    # Check each tool permission
    if user_has_tool_permission(user, 'annotation'):
        available_tools.append('annotation')
    
    if user_has_tool_permission(user, 'session_viewer'):
        available_tools.append('session_viewer')
    
    return available_tools


def require_tool_permission(tool_name):
    """
    Decorator to require specific tool permission for a view.
    
    Usage:
        @require_tool_permission('annotation')
        def my_view(request):
            ...
    
    Args:
        tool_name: String name of the tool to check permission for
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Check if user has permission
            if not user_has_tool_permission(request.user, tool_name):
                # Add error message
                messages.error(
                    request, 
                    f"You don't have permission to access the {tool_name.replace('_', ' ').title()} tool. "
                    "Please contact your administrator for access."
                )
                # Redirect to dashboard
                return redirect('core:dashboard')
            
            # User has permission, proceed to view
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def assign_user_to_tool(user, tool_name):
    """
    Helper function to assign a user to a tool group.
    Useful for management commands or admin actions.
    
    Args:
        user: Django User instance
        tool_name: String name of the tool ('annotation' or 'session_viewer')
    
    Returns:
        Boolean: True if assignment was successful
    """
    try:
        if tool_name == 'annotation':
            group = Group.objects.get(name='annotation_users')
        elif tool_name == 'session_viewer':
            group = Group.objects.get(name='session_viewers')
        else:
            return False
        
        user.groups.add(group)
        return True
    except Group.DoesNotExist:
        return False