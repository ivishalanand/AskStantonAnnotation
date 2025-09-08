from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages

# Custom login view using Django's built-in LoginView
class CustomLoginView(LoginView):
    """
    Custom login view that extends Django's LoginView.
    Uses a custom template and handles login logic.
    """
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Called when valid form data has been POSTed"""
        # Log the user in
        login(self.request, form.get_user())
        return super().form_valid(form)

# Password change view
class CustomPasswordChangeView(PasswordChangeView):
    """
    Custom password change view that updates the must_change_password flag
    after a successful password change.
    """
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('core:dashboard')
    
    def form_valid(self, form):
        """
        Called when the password change form is valid.
        Updates the must_change_password flag to False.
        """
        # Save the new password
        response = super().form_valid(form)
        
        # Update the must_change_password flag
        user = self.request.user
        if hasattr(user, 'must_change_password'):
            user.must_change_password = False
            user.save(update_fields=['must_change_password'])
            messages.success(self.request, 'Your password has been changed successfully!')
        
        return response

# Custom logout view that handles GET requests
def logout_view(request):
    """
    Custom logout view that handles both GET and POST requests.
    Logs out the user and redirects to login page with a success message.
    """
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f'You have been successfully logged out. Goodbye, {username}!')
    
    return redirect('login')

# Dashboard view (simple view for now)
@login_required
def dashboard_view(request):
    """
    Simple dashboard view that displays a welcome message.
    Only accessible to logged-in users.
    """
    return render(request, 'accounts/dashboard.html', {
        'user': request.user
    })
