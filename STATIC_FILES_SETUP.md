# Static Files Setup Guide

## Important: How to Run the Project Correctly

The CSS and templates will **NOT work** if you open the HTML files directly in the browser. You **MUST** run Django's development server.

## Steps to Run the Project:

1. **Open Terminal/Command Prompt** in the project directory

2. **Run Django Development Server:**
   ```bash
   python manage.py runserver
   ```

3. **Access the application at:**
   ```
   http://127.0.0.1:8000/
   ```
   **NOT** `127.0.0.1:5500` (that's a simple HTTP server, not Django)

## What Was Fixed:

1. ✅ **Removed duplicate STATIC_URL** in `settings.py`
2. ✅ **Added STATIC_ROOT** for production builds
3. ✅ **Added static file serving** in `urls.py` for development
4. ✅ **Fixed `{% load static %}`** in login.html and signup.html
5. ✅ **All templates now properly load CSS** from `static/style.css`

## File Structure:

```
MaintenanceTracker-main/
├── static/
│   └── style.css          ← Your CSS file is here
├── core/
│   ├── settings.py        ← Static files configured
│   └── urls.py            ← Static serving added
├── gearguard/
│   └── templates/
│       ├── base.html      ← Loads CSS correctly
│       ├── dashboard.html
│       ├── kanban_board.html
│       ├── calendar.html
│       └── equipment_detail.html
└── accounts/
    └── templates/
        ├── login.html     ← Fixed to load CSS
        └── signup.html    ← Fixed to load CSS
```

## Troubleshooting:

### If CSS still doesn't load:

1. **Clear browser cache** (Ctrl+Shift+R or Cmd+Shift+R)
2. **Check Django server is running** on port 8000
3. **Verify static file exists:** `static/style.css`
4. **Check browser console** for 404 errors on CSS file

### If templates show raw Django tags:

- You're viewing the file directly, not through Django
- **Always use:** `http://127.0.0.1:8000/` (Django server)
- **Never use:** `file:///` or `127.0.0.1:5500` (static file server)

## Testing:

After running `python manage.py runserver`, visit:
- Login: `http://127.0.0.1:8000/accounts/login/`
- Dashboard: `http://127.0.0.1:8000/dashboard/`
- Kanban: `http://127.0.0.1:8000/kanban/`
- Calendar: `http://127.0.0.1:8000/calendar/`

All pages should now display with beautiful, professional styling! 🎨

