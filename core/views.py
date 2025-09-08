"""
Views for the core app.
Handles the main dashboard and shared functionality.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .permissions import user_has_tool_permission

@login_required
def dashboard(request):
    """
    Main dashboard view showing available admin tools.
    Displays tool cards based on user permissions.
    """
    
    # Define all available tools with their information
    all_tools = [
        {
            'name': 'Annotation Tool',
            'description': 'Annotate and label data for machine learning and analysis',
            'icon': 'bi-pencil-square',
            'color': 'primary',
            'url': '/tools/annotation/',
            'url_name': 'annotation_tool:index',
            'permission': 'annotation_tool.view_annotation',
            'status': 'Active'
        },
        {
            'name': 'Session Viewer',
            'description': 'Monitor active user sessions and manage session data',
            'icon': 'bi-eye',
            'color': 'success',
            'url': '/tools/sessions/',
            'url_name': 'session_viewer:index',
            'permission': 'session_viewer.view_session',
            'status': 'Active'
        }
    ]
    
    # Filter tools based on user permissions
    available_tools = []
    for tool in all_tools:
        # Check if user has permission for this specific tool
        tool_name = 'annotation' if 'annotation' in tool['url'] else 'session_viewer'
        
        if user_has_tool_permission(request.user, tool_name):
            available_tools.append(tool)
    
    # Prepare context for template
    context = {
        'tools': available_tools,
        'total_tools': len(all_tools),
        'available_count': len(available_tools)
    }
    
    return render(request, 'core/dashboard.html', context)
