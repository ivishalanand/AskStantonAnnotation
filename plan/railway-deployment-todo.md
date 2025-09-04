# Railway Deployment Plan - Django Authentication App

## Project Goal
Deploy the Django authentication application with forced password change functionality to Railway platform for production use.

## Project Details
**Scope:** Configure and deploy an existing Django MVP authentication system to Railway's cloud platform  
**Purpose:** Make the authentication system accessible via web for production use with minimal changes to existing codebase  
**Context:** Early-stage startup MVP focusing on core functionality - users must change password on first login  
**Current State:** Fully functional local Django app with custom authentication, needs production configuration  
**Target Platform:** Railway with PostgreSQL database and WhiteNoise for static files  

## Deployment Configuration
- **Database:** PostgreSQL (Railway-provided)
- **Static Files:** WhiteNoise
- **Environment:** .env files for dev/prod separation
- **Domain:** Railway subdomain initially
- **Package Management:** Convert from uv to requirements.txt

---

## Phase 1: Environment Configuration
- [x] Install python-dotenv to handle .env files
- [x] Create .env.example file with all required variables (template)
- [x] Update settings.py to read from environment variables:
  - [x] SECRET_KEY from env
  - [x] DEBUG from env (True for dev, False for prod)
  - [x] ALLOWED_HOSTS from env
  - [x] DATABASE_URL for PostgreSQL connection
- [x] Create local .env file for development (won't be committed)

## Phase 2: Database Configuration
- [x] Add dj-database-url package for DATABASE_URL parsing
- [x] Update settings.py to use PostgreSQL in production, SQLite in dev
- [x] Keep existing SQLite for local development (no changes to workflow)

## Phase 3: Static Files Setup
- [x] Install whitenoise for static file serving
- [x] Add WhiteNoise middleware to settings.py
- [x] Configure STATIC_ROOT for production
- [x] Verify existing templates/static structure remains unchanged

## Phase 4: Dependencies Management
- [x] Generate requirements.txt from current uv setup
- [x] Include all production dependencies:
  - [x] Django (existing version)
  - [x] psycopg2-binary (PostgreSQL adapter)
  - [x] dj-database-url (database URL parsing)
  - [x] python-dotenv (environment variables)
  - [x] whitenoise (static files)
  - [x] gunicorn (WSGI server)

## Phase 5: Railway Configuration
- [x] Create railway.json with build and start commands
- [x] Create Procfile for web process definition
- [x] Add runtime.txt to specify Python version

## Phase 6: Production Settings
- [x] Add CSRF_TRUSTED_ORIGINS for Railway domain
- [x] Ensure middleware order is correct
- [x] Add basic security settings (minimal, MVP-focused)

## Phase 7: Testing & Verification
- [x] Test local development still works with .env
- [x] Verify SQLite still works locally
- [x] Confirm no breaking changes to authentication flow
- [x] Test static files are served correctly (collected 127 files)

## Phase 8: Deployment
- [ ] Push changes to GitHub repository
- [ ] Connect Railway to GitHub repo
- [ ] Add PostgreSQL database in Railway
- [ ] Set environment variables in Railway dashboard:
  - [ ] SECRET_KEY (generate new secure key)
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS=your-app.up.railway.app
  - [ ] DATABASE_URL (auto-provided by Railway)
- [ ] Deploy and test authentication flow in production

## Post-Deployment Checklist
- [ ] Verify login functionality
- [ ] Test forced password change flow
- [ ] Confirm admin panel access
- [ ] Check static files are loading
- [ ] Monitor for any errors in Railway logs

---

## Notes
- **No changes to:** Authentication logic, User model, middleware, templates, views, URL patterns
- **Local dev command unchanged:** `uv run python manage.py runserver`
- **Focus:** Minimal changes for working MVP, avoiding overengineering

---

*This todo list will be updated as development progresses. Each task will be marked as completed when finished.*