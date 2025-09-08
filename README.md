# Admin Tools Platform

A comprehensive Django-based platform for hosting multiple administrative tools with role-based access control, professional UI, and extensible architecture.

## Platform Overview

This platform serves as a centralized hub for various administrative tools, currently featuring:

### **🎯 Core Features**

- **Multi-Tool Architecture**: Modular Django apps for different administrative functions
- **Role-Based Access Control**: Fine-grained permissions using Django groups
- **Professional UI**: Bootstrap 5 with responsive design and consistent navigation
- **User Management**: Custom User model with forced password change functionality
- **Session Management**: Real-time session monitoring and security features
- **Production Ready**: Deployment configuration for Railway with PostgreSQL

### **🔧 Available Tools**

1. **Annotation Tool** (`/tools/annotation/`)
   - Data annotation and labeling platform
   - Currently in development (Hello World interface)
   - Planned features: Multi-format import/export, collaboration, quality control

2. **Session Viewer** (`/tools/sessions/`)
   - Real-time user session monitoring
   - Active session display with user details
   - Security monitoring and session analytics

### **🛡️ Security & Access Control**

- **Group-Based Permissions**: `annotation_users`, `session_viewers`
- **Automatic Superuser Access**: Superusers have access to all tools
- **Protected Views**: All tools require login and appropriate permissions
- **Session Security**: Secure session handling and monitoring

### **🎨 User Experience**

- **Unified Navigation**: Persistent sidebar with breadcrumb navigation
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Professional Alerts**: Enhanced error messages and user feedback
- **Consistent Branding**: Unified design language across all tools

## Local Development

### Prerequisites
- Python 3.12+
- uv package manager (or pip)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AskStantonAnnotation
   ```

2. **Install dependencies**
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

4. **Run migrations**
   ```bash
   uv run python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   uv run python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   uv run python manage.py runserver
   ```

7. **Access the application**
   - Application: http://localhost:8000
   - Admin panel: http://localhost:8000/admin/

## Product
### Deployment Status
- **URL**: https://annotation.up.railway.app
- **Admin Panel**: https://annotation.up.railway.app/admin/

### Initial Setup

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **On Railway Dashboard**
   - Create a new project
   - Connect your GitHub repository
   - Add PostgreSQL database (New � Database � PostgreSQL)
   - Set environmention Deployment on Railway
 variables in the web service:
     ```
     SECRET_KEY=<generate-secure-key>
     DEBUG=False
     ALLOWED_HOSTS=.railway.app,.up.railway.app
     CSRF_TRUSTED_ORIGINS=https://*.up.railway.app,https://*.railway.app
     DATABASE_URL=<auto-linked-from-postgres>
     ```

### Creating a Superuser on Railway

Railway uses Nixpacks for deployment, which installs Python packages in `/opt/venv/`. To create a superuser on your deployed Railway app:

#### Method 1: Railway SSH (Recommended)

1. **Get SSH command from Railway Dashboard**
   - Go to your Railway project
   - Right-click on your **web** service
   - Select **"Copy SSH Command"**
   - You'll get a command like:
     ```bash
     railway ssh --project=xxx --environment=xxx --service=xxx
     ```

2. **Connect via SSH and create superuser**
   ```bash
   # Paste the copied SSH command in your terminal
   railway ssh --project=xxx --environment=xxx --service=xxx
   
   # Once connected, run:
   /opt/venv/bin/python manage.py createsuperuser
   
   # Follow the prompts to create your admin user
   ```

#### Method 2: Railway CLI with Public Database URL

If SSH doesn't work, you can use the Railway CLI with the public database URL:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Get your DATABASE_PUBLIC_URL**
   - Go to Railway Dashboard � Postgres service � Variables
   - Copy the `DATABASE_PUBLIC_URL` value

3. **Run locally with Railway's database**
   ```bash
   # Set the public database URL
   export DATABASE_URL="your-database-public-url-here"
   
   # Run the command
   python manage.py createsuperuser
   ```

### Running Other Management Commands on Railway

Use the same SSH method for other Django management commands:

```bash
# Connect via SSH
railway ssh --project=xxx --environment=xxx --service=xxx

# Run migrations
/opt/venv/bin/python manage.py migrate

# Collect static files
/opt/venv/bin/python manage.py collectstatic --noinput

# Open Django shell
/opt/venv/bin/python manage.py shell

# Create custom management commands
/opt/venv/bin/python manage.py your_custom_command
```

### Useful Aliases in Railway SSH

When connected via SSH, you can create aliases for convenience:

```bash
# Create aliases
alias python='/opt/venv/bin/python'
alias manage='/opt/venv/bin/python manage.py'

# Now use simplified commands
manage createsuperuser
manage migrate
manage shell
```

## 🚀 Adding New Tools to the Platform

The platform is designed for easy expansion. Here's how to add a new administrative tool:

### 1. Create a New Django App

```bash
python manage.py startapp new_tool_name
```

### 2. Add to INSTALLED_APPS

In `annotation/settings.py`:
```python
INSTALLED_APPS = [
    # ... existing apps
    'new_tool_name',  # Your new tool
]
```

### 3. Create URL Structure

Create `new_tool_name/urls.py`:
```python
from django.urls import path
from . import views

app_name = 'new_tool_name'

urlpatterns = [
    path('', views.index, name='index'),
]
```

### 4. Add Tool URL to Main URLs

In `annotation/urls.py`:
```python
urlpatterns = [
    # ... existing patterns
    path('tools/new-tool/', include('new_tool_name.urls')),
]
```

### 5. Create Permission Group

Add a migration in the `core` app to create the group:
```python
# In core/migrations/
Group.objects.get_or_create(name='new_tool_users')
```

### 6. Create Views with Permissions

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.permissions import require_tool_permission

@login_required
@require_tool_permission('new_tool')
def index(request):
    return render(request, 'new_tool_name/index.html')
```

### 7. Update Core Dashboard

Add your tool to `core/views.py`:
```python
all_tools = [
    # ... existing tools
    {
        'name': 'New Tool',
        'description': 'Description of your new tool',
        'icon': 'bi-your-icon',
        'color': 'info',
        'url': '/tools/new-tool/',
        'url_name': 'new_tool_name:index',
        'permission': 'new_tool.view_permission',
        'status': 'Active'
    }
]
```

### 8. Update Permission System

In `core/permissions.py`, add your tool to the permission functions:
```python
def user_has_tool_permission(user, tool_name):
    if tool_name == 'new_tool':
        return user.groups.filter(name='new_tool_users').exists()
```

### 9. Create Templates

Create `new_tool_name/templates/new_tool_name/index.html`:
```html
{% extends "base_with_sidebar.html" %}

{% block title %}New Tool - Admin Tools{% endblock %}
{% block page_title %}New Tool{% endblock %}

{% block breadcrumb %}
<li class="breadcrumb-item active" aria-current="page">
    <i class="bi bi-your-icon"></i> New Tool
</li>
{% endblock %}

{% block content %}
<!-- Your tool content here -->
{% endblock %}
```

### 10. Add Tests

Create comprehensive tests in `new_tool_name/tests.py`:
```python
from django.test import TestCase
from django.contrib.auth import get_user_model
# ... test your tool functionality
```

### 11. Update Management Commands

The existing management command will automatically work with your new tool if you follow the naming convention: `new_tool_users` group name maps to `new_tool` tool name.

## Project Structure

```
AskStantonAnnotation/
├── accounts/                 # Custom authentication app
│   ├── models.py            # Custom User model with password change
│   ├── views.py             # Login, password change views
│   ├── middleware.py        # Force password change middleware
│   └── templates/           # Authentication templates
├── core/                    # Core platform functionality
│   ├── views.py             # Central dashboard
│   ├── permissions.py       # Permission utilities
│   ├── templatetags/        # Permission template tags
│   └── management/          # Management commands
├── annotation_tool/         # Data annotation tool (development)
├── session_viewer/          # Session monitoring tool (active)
├── annotation/              # Main Django project settings
├── templates/               # Shared base templates
├── static/                  # Static files (CSS, JS, images)
├── plan/                    # Development planning documentation
└── requirements.txt         # Python dependencies
```

## 🔧 Management Commands

The platform includes several management commands for easy administration:

### Tool Permissions
```bash
# List all permission groups and their members
python manage.py setup_tool_permissions --list-groups

# Grant specific tool access to a user
python manage.py setup_tool_permissions --user username --tool annotation

# Grant all permissions to all superusers
python manage.py setup_tool_permissions --superuser-all
```

### URL Validation
```bash
# Validate URL structure and patterns
python manage.py validate_urls
```

## 🧪 Testing

Run comprehensive tests for the entire platform:

```bash
# Run all tests
python manage.py test

# Run tests for specific apps
python manage.py test core.tests
python manage.py test annotation_tool.tests
python manage.py test session_viewer.tests

# Run tests with verbose output
python manage.py test --verbosity=2
```

## Authentication Flow

1. User logs in with username/password
2. If `must_change_password` flag is True, user is redirected to password change page
3. User cannot access any other page until password is changed
4. After successful password change, flag is set to False
5. User can now access the dashboard and other protected pages

## Admin Features

- View and edit users in Django admin
- Toggle "must change password" flag for any user
- Filter users by password change requirement
- Bulk actions to force password changes

## Security Notes

- Always use strong, unique SECRET_KEY in production
- Keep DEBUG=False in production
- Use HTTPS in production (Railway provides this automatically)
- Regularly update dependencies for security patches

## Troubleshooting

### "Too many redirects" error
- Ensure `SECURE_SSL_REDIRECT` is disabled (Railway handles SSL)
- Clear browser cookies and cache

### Cannot connect to database locally
- Make sure you're using the correct DATABASE_URL
- For local development, leave DATABASE_URL empty to use SQLite

### Static files not loading
- Run `python manage.py collectstatic`
- Ensure WhiteNoise middleware is properly configured

## Environment Variables

See `.env.example` for all required environment variables:
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains
- `DATABASE_URL`: PostgreSQL connection string (auto-set by Railway)
- `CSRF_TRUSTED_ORIGINS`: Comma-separated list of trusted origins
