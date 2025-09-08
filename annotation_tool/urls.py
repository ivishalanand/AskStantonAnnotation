"""
URL configuration for the annotation tool app.

URL Structure:
    /tools/annotation/                   - Main index (redirects to queues)
    /tools/annotation/queues/            - Queue list view
    /tools/annotation/queues/<queue_id>/ - Queue detail view
"""

from django.urls import path
from . import views

# Namespace for annotation tool URLs
app_name = 'annotation_tool'

urlpatterns = [
    # Main annotation tool index page (redirects to queue list)
    path('', views.index, name='index'),
    
    # Queue management URLs
    path('queues/', views.queue_list, name='queue_list'),
    path('queues/<str:queue_id>/', views.queue_detail, name='queue_detail'),
]