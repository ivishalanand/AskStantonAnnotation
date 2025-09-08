"""
URL configuration for the session viewer app.
"""

from django.urls import path
from . import views

# Namespace for session viewer URLs
app_name = 'session_viewer'

urlpatterns = [
    # Main session viewer index page
    path('', views.index, name='index'),
]