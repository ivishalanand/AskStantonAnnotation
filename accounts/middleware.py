from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    """
    Middleware to force users to change their password when must_change_password is True.
    
    This middleware checks if a logged-in user has the must_change_password flag set to True,
    and if so, redirects them to the password change page for any request except:
    - The password change page itself
    - Login/logout pages
    - Static files
    - Admin pages (for superusers)
    """
    
    def __init__(self, get_response):
        """Initialize the middleware with the get_response callable"""
        self.get_response = get_response
        
        # URLs that are exempt from password change enforcement
        self.exempt_urls = [
            reverse('password_change'),  # Allow access to password change page
            reverse('login'),             # Allow access to login page
            reverse('logout'),            # Allow access to logout page
            '/admin/',                    # Allow admin access for superusers
            '/static/',                   # Allow static files
            '/media/',                    # Allow media files
        ]
    
    def __call__(self, request):
        """Process each request"""
        
        # Check if user is authenticated and has must_change_password flag
        if request.user.is_authenticated:
            # Check if the current path is exempt
            is_exempt = any(request.path.startswith(url) for url in self.exempt_urls)
            
            # If user must change password and current URL is not exempt
            if hasattr(request.user, 'must_change_password') and \
               request.user.must_change_password and \
               not is_exempt:
                
                # Special case: Allow superusers to access admin
                if request.path.startswith('/admin/') and request.user.is_superuser:
                    pass  # Allow superusers to access admin even if must_change_password is True
                else:
                    # Redirect to password change page
                    return redirect('password_change')
        
        # Process the request normally
        response = self.get_response(request)
        return response