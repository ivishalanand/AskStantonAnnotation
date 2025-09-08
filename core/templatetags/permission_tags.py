"""
Template tags for checking tool permissions.
Provides easy permission checking within templates.
"""

from django import template
from core.permissions import user_has_tool_permission

register = template.Library()


@register.filter
def has_tool_permission(user, tool_name):
    """
    Template filter to check if a user has permission for a specific tool.
    
    Usage in template:
        {% if user|has_tool_permission:"annotation" %}
            <!-- Show annotation tool -->
        {% endif %}
    
    Args:
        user: Django User instance
        tool_name: String name of the tool
    
    Returns:
        Boolean: True if user has permission
    """
    return user_has_tool_permission(user, tool_name)


@register.simple_tag
def user_tool_count(user):
    """
    Template tag to get the number of tools a user has access to.
    
    Usage in template:
        {% user_tool_count user as tool_count %}
        User has access to {{ tool_count }} tools.
    
    Args:
        user: Django User instance
    
    Returns:
        Integer: Number of accessible tools
    """
    count = 0
    if user_has_tool_permission(user, 'annotation'):
        count += 1
    if user_has_tool_permission(user, 'session_viewer'):
        count += 1
    return count