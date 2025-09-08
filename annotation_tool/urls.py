"""
URL configuration for the annotation tool app.
"""

from django.urls import path
from . import views

# Namespace for annotation tool URLs
app_name = 'annotation_tool'

urlpatterns = [
    # Main annotation tool index page
    path('', views.index, name='index'),
]