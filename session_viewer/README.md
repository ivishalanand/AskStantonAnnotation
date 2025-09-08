# Session Viewer

A Django app for prettyfying users Sessions
## Purpose


## Current Status

✅ **Fully Functional** - Displays active Django sessions with user information, expiration times, and session metadata.

## Features


## Access Control

Access to the Session Viewer is controlled through Django's group-based permission system:

- **Permission Group**: `session_viewers`
- **Access Level**: Users must be added to the `session_viewers` group
- **Superuser Access**: Automatic access for all superusers

### Managing Access

#### Via Management Command
```bash
# Grant session viewer access to a user
python manage.py setup_tool_permissions --user username --tool session_viewer

# Grant all tool permissions to a user
python manage.py setup_tool_permissions --user username --tool all

# List current group assignments
python manage.py setup_tool_permissions --list-groups
```

#### Via Django Admin
1. Go to `/admin/auth/group/`
2. Click on `session_viewers`
3. Add/remove users from the group

## URL Structure

- **Main Interface**: `/tools/sessions/`
- **URL Name**: `session_viewer:index`

## Templates

- **Base Template**: Extends `base_with_sidebar.html`
- **Main Template**: `session_viewer/templates/session_viewer/index.html`
- **Features**: Bootstrap 5 styling, responsive tables, breadcrumb navigation

## Technical Implementation

### Session Data Processing

The Session Viewer queries Django's `Session` model and processes:

1. **Active Sessions**: Filters sessions by expiration date
2. **User Association**: Decodes session data to identify users
3. **Session Metadata**: Extracts and displays session information
4. **Current Session**: Highlights the user's current session

### Security Considerations

- Session keys are truncated for security
- Only authenticated users with proper permissions can access
- Session data is handled securely
- Sensitive information warnings are displayed

## Testing

Run tests for the session viewer:

```bash
python manage.py test session_viewer.tests
```

## Development

### File Structure

```
session_viewer/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models.py              # No custom models (uses Django Session)
├── tests.py              # Comprehensive test suite
├── urls.py               # URL routing
├── views.py              # Session data processing
├── templates/
│   └── session_viewer/
│       └── index.html    # Main interface template
└── README.md             # This file
```

### View Logic

The main view (`session_viewer.views.index`):

1. Retrieves active sessions from Django's Session model
2. Decodes session data to extract user information
3. Formats data for template display
4. Identifies the current user's session
5. Provides context for template rendering
