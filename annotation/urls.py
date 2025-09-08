"""
URL configuration for the Admin Tools Platform.

This file organizes all URL patterns for the platform in a clean, hierarchical structure.
All admin tools follow the pattern: /tools/<tool-name>/

URL Structure:
    /                       - Root redirect to login
    /login/                 - User authentication
    /logout/                - User logout  
    /password-change/       - Password change form
    /dashboard/             - Main admin dashboard
    /admin/                 - Django admin panel
    /tools/annotation/      - Annotation tool interface
    /tools/sessions/        - Session viewer tool interface
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def root_redirect(request):
    """
    Root URL redirect handler.
    Redirects anonymous users to login, maintaining clean URL structure.
    """
    return redirect('login')


urlpatterns = [
    # ===========================================
    # ROOT & CORE NAVIGATION
    # ===========================================
    
    # Root URL - redirect to appropriate landing page
    path('', root_redirect, name='root'),
    
    # Core dashboard and shared functionality
    path('', include('core.urls')),
    
    # ===========================================
    # AUTHENTICATION & USER MANAGEMENT
    # ===========================================
    
    # User authentication, logout, password management
    path('', include('accounts.urls')),
    
    # ===========================================
    # ADMIN INTERFACE
    # ===========================================
    
    # Django built-in admin panel
    path('admin/', admin.site.urls, name='django_admin'),
    
    # ===========================================
    # ADMIN TOOLS
    # ===========================================
    # All tools follow the pattern: /tools/<tool-name>/
    
    # Data annotation and labeling tool
    path('tools/annotation/', include('annotation_tool.urls')),
    
    # Session monitoring and management tool
    path('tools/sessions/', include('session_viewer.urls')),
    
    # Future tools can be added here following the same pattern:
    # path('tools/reports/', include('report_tool.urls')),
    # path('tools/analytics/', include('analytics_tool.urls')),
]
