"""
Context processors for the core app.
Provides global context variables for all templates.
"""

def tools_context(request):
    """
    Add available tools information to template context.
    This allows templates to dynamically show/hide tools based on permissions.
    """
    
    # Define available tools with their metadata
    tools = []
    
    # Check if user is authenticated before checking permissions
    if request.user.is_authenticated:
        # Annotation Tool - check if user has permission
        if request.user.has_perm('annotation_tool.view_annotation') or request.user.is_superuser:
            tools.append({
                'name': 'Annotation Tool',
                'icon': 'bi-pencil-square',
                'url_name': 'annotation_tool:index',
                'description': 'Tool for annotating and labeling data',
                'permission_required': 'annotation_tool.view_annotation'
            })
        
        # Session Viewer - check if user has permission
        if request.user.has_perm('session_viewer.view_session') or request.user.is_superuser:
            tools.append({
                'name': 'Session Viewer',
                'icon': 'bi-eye',
                'url_name': 'session_viewer:index',
                'description': 'View and manage active user sessions',
                'permission_required': 'session_viewer.view_session'
            })
    
    return {
        'available_tools': tools,
        'tools_count': len(tools)
    }