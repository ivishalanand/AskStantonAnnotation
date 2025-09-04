# Django Authentication Implementation Todo List

## Phase 1: Project Setup
- [x] Initialize Django project 'annotation'
  - Created Django project using `uv` and `django-admin`
  - Set up pyproject.toml with Django dependency
- [x] Create Django app 'accounts' for authentication  
  - Generated accounts app using `manage.py startapp`
- [x] Configure basic settings (SECRET_KEY, INSTALLED_APPS, etc.)
  - Added 'accounts' to INSTALLED_APPS
  - Configured templates directory  
  - Added authentication redirect settings

## Phase 2: Custom User Model
- [x] Create Custom User Model extending AbstractUser
  - Created User class in accounts/models.py
  - Extends Django's AbstractUser
- [x] Add must_change_password boolean field to User model
  - Added BooleanField with default=True
  - Includes help_text for admin clarity
- [x] Configure AUTH_USER_MODEL in settings
  - Set AUTH_USER_MODEL = 'accounts.User'
  - Database migrations created and applied

## Phase 3: Database Setup
- [x] Run initial database migrations
  - Applied all migrations successfully
  - Created custom User table with must_change_password field
- [x] Create superuser for admin access
  - Superuser 'vishal' created via CLI
  - Used `uv run python manage.py createsuperuser` command

## Phase 4: Authentication Views
- [x] Create login view using Django's LoginView
  - Created CustomLoginView in accounts/views.py
  - Extends Django's built-in LoginView
- [x] Create login template with user ID and password fields
  - Created registration/login.html template
  - Clean form with username/password fields
- [x] Create password change view using PasswordChangeForm
  - Created CustomPasswordChangeView in views.py
  - Uses Django's PasswordChangeView
- [x] Create password change template
  - Created accounts/password_change.html
  - Shows warning if password change required
- [x] Update must_change_password flag after successful password change
  - Implemented in CustomPasswordChangeView.form_valid()
  - Sets must_change_password to False after change

## Phase 5: Middleware for Force Password Change
- [x] Create middleware to check must_change_password flag
  - Created ForcePasswordChangeMiddleware in accounts/middleware.py
  - Checks authenticated users for must_change_password flag
- [x] Configure middleware to redirect to password change page
  - Redirects to password_change URL when flag is True
  - Exempts login, logout, password change, and admin URLs
- [x] Add middleware to settings.py
  - Added to MIDDLEWARE list after AuthenticationMiddleware
  - Ensures password change enforcement on all requests

## Phase 6: Dashboard
- [x] Create dashboard view with welcome message
  - Created dashboard_view in accounts/views.py
  - Login required decorator ensures authentication
- [x] Create dashboard template with logout link
  - Created accounts/dashboard.html template
  - Shows user info and navigation links
  - Includes logout link in navigation bar

## Phase 7: Admin Configuration
- [x] Register custom User model in admin
  - Created CustomUserAdmin class extending UserAdmin
  - Registered User model with admin site
- [x] Add 'Force password change' checkbox in admin
  - Added must_change_password to list_display and list_filter
  - Made must_change_password editable in list view
  - Added to fieldsets for edit and creation forms
  - Customized admin site headers

## Phase 8: URLs and Templates
- [x] Configure authentication URLs (login, logout, password-change)
  - Created accounts/urls.py with all auth URLs
  - Included in main project URLs
- [x] Setup dashboard URL and login redirects
  - Configured LOGIN_URL, LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL
  - Root URL redirects to login page
- [x] Create base template with basic styling
  - Created templates/base.html with clean CSS
  - Simple, responsive design for MVP

## Phase 9: Testing
- [ ] Test complete authentication flow

---
*This todo list will be updated as development progresses. Each task will be marked as completed when finished.*