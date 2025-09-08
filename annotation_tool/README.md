# Annotation Tool

A Django app for User thread annotation and labeling tasks, designed as part of the Stanton Admin Tools.

## Purpose

The Annotation Tool provides a web-based interface for annotating and labeling various types of data for AskStanton.

## Access Control

Access to the Annotation Tool is controlled through Django's group-based permission system:

- **Permission Group**: `annotation_users`
- **Access Level**: Users must be added to the `annotation_users` group
- **Superuser Access**: Automatic access for all superusers

### Managing Access

#### Via Management Command
```bash
# Grant annotation access to a user
python manage.py setup_tool_permissions --user username --tool annotation

# Grant all tool permissions to a user
python manage.py setup_tool_permissions --user username --tool all

# Grant permissions to all superusers
python manage.py setup_tool_permissions --superuser-all
```

#### Via Django Admin
1. Go to `/admin/auth/group/`
2. Click on `annotation_users`
3. Add/remove users from the group

## URL Structure

- **Main Interface**: `/tools/annotation/`
- **URL Name**: `annotation_tool:index`

## Templates

- **Base Template**: Extends `base_with_sidebar.html`
- **Main Template**: `annotation_tool/templates/annotation_tool/index.html`
- **Features**: Bootstrap 5 styling, breadcrumb navigation, responsive design

## Testing

Run tests for the annotation tool:

```bash
python manage.py test annotation_tool.tests
```

### Test Coverage

- Authentication and login requirements
- Permission-based access control
- Superuser access verification
- Template rendering and context data
- Content display verification

## Development

### Adding New Features

1. **Views**: Add new views in `annotation_tool/views.py`
2. **URLs**: Register new URLs in `annotation_tool/urls.py`
3. **Templates**: Create templates in `annotation_tool/templates/annotation_tool/`
4. **Tests**: Add tests in `annotation_tool/tests.py`

### File Structure

```
annotation_tool/
├── __init__.py
├── admin.py
├── apps.py
├── migrations/
├── models.py              # Future: Annotation data models
├── tests.py              # Comprehensive test suite
├── urls.py               # URL routing
├── views.py              # View logic
├── templates/
│   └── annotation_tool/
│       └── index.html    # Main interface template
└── README.md             # This file
```
