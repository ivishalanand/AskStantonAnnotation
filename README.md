## Features

- Custom User model with forced password change flag
- Middleware that enforces password change for flagged users
- Clean, responsive login and dashboard interface
- Admin panel integration with user management
- Production-ready deployment configuration for Railway

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

## Project Structure

```
AskStantonAnnotation/
- accounts/               # Custom authentication app
    - models.py          # Custom User model
    - views.py           # Login, password change, dashboard views
    - middleware.py      # Force password change middleware
    - templates/         # Authentication templates
- annotation/            # Main Django project settings
- templates/             # Base templates
- staticfiles/          # Collected static files (production)
- requirements.txt      # Python dependencies
- railway.json         # Railway deployment configuration
- Procfile            # Process definition for deployment
- .env.example        # Environment variables template
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
