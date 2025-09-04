"""
URL configuration for annotation project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Root view to redirect to login
def root_redirect(request):
    """Redirect root URL to login page"""
    return redirect('login')

urlpatterns = [
    # Root URL redirect
    path('', root_redirect, name='root'),
    
    # Admin panel
    path('admin/', admin.site.urls),
    
    # Include accounts app URLs
    path('', include('accounts.urls')),
]
