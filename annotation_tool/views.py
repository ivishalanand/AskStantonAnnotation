"""
Views for the annotation tool app.
Provides data annotation and labeling functionality.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.permissions import require_tool_permission

@login_required
@require_tool_permission('annotation')
def index(request):
    """
    Main index view for the annotation tool.
    Currently shows a "Hello World" placeholder.
    """
    
    # Context for template
    context = {
        'tool_name': 'Annotation Tool',
        'description': 'Data annotation and labeling platform',
        'features': [
            'Data Import and Export',
            'Multiple Annotation Types (Labels, Categories, Text)',
            'User Management and Assignments', 
            'Progress Tracking and Analytics',
            'Quality Control and Review Workflow'
        ],
        'status': 'Under Development'
    }
    
    return render(request, 'annotation_tool/index.html', context)
