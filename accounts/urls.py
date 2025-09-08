from django.urls import path
from .views import CustomLoginView, CustomPasswordChangeView, logout_view

# URL patterns for authentication and account management
urlpatterns = [
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-change/', CustomPasswordChangeView.as_view(), name='password_change'),
    
    # Note: Dashboard is now handled by the core app at /dashboard/
]