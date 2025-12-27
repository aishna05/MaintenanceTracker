# 🚀 Complete Setup Guide - GearGuard Maintenance Tracker

## Step-by-Step Instructions to Run Your Website

### **Step 1: Open Terminal/Command Prompt**

Navigate to your project folder:
```bash
cd /Users/sunitachoudhary/Desktop/MaintenanceTracker-main
```

### **Step 2: Create Virtual Environment (Recommended)**

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### **Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

If you get an error, install Django directly:
```bash
pip install Django==5.2.9
```

### **Step 4: Run Database Migrations**

```bash
# Create database tables
python manage.py migrate

# Create superuser (admin account) - Optional but recommended
python manage.py createsuperuser
# Follow prompts to create admin username, email, and password
```

### **Step 5: Collect Static Files (Important for CSS)**

```bash
python manage.py collectstatic --noinput
```

### **Step 6: Run the Development Server**

```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### **Step 7: Open Your Website**

Open your web browser and go to:

**Main URLs:**
- **Home/Dashboard:** http://127.0.0.1:8000/
- **Login Page:** http://127.0.0.1:8000/accounts/login/
- **Sign Up:** http://127.0.0.1:8000/accounts/signup/
- **Admin Panel:** http://127.0.0.1:8000/admin/

**Other Pages:**
- **Kanban Board:** http://127.0.0.1:8000/kanban/
- **Calendar:** http://127.0.0.1:8000/calendar/
- **Equipment List:** http://127.0.0.1:8000/equipment/
- **Reports:** http://127.0.0.1:8000/reporting/
- **Teams:** http://127.0.0.1:8000/teams/

---

## 🔧 Troubleshooting

### **Problem: "ModuleNotFoundError: No module named 'django'"**

**Solution:**
```bash
pip install Django==5.2.9
```

### **Problem: "No such table" or Database errors**

**Solution:**
```bash
python manage.py migrate
```

### **Problem: CSS not loading / Styles not showing**

**Solutions:**
1. Clear browser cache: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Run collectstatic:
   ```bash
   python manage.py collectstatic --noinput
   ```
3. Make sure you're accessing via Django server (http://127.0.0.1:8000/)
   NOT via file:// or other servers

### **Problem: "Port 8000 already in use"**

**Solution:**
Run on a different port:
```bash
python manage.py runserver 8080
```
Then access: http://127.0.0.1:8080/

### **Problem: "TemplateDoesNotExist"**

**Solution:**
Check that templates are in the correct location:
- `gearguard/templates/` for gearguard templates
- `accounts/templates/` for accounts templates

### **Problem: Site shows raw Django template tags**

**Solution:**
- You're viewing files directly, not through Django
- **ALWAYS use:** http://127.0.0.1:8000/
- **NEVER use:** file:/// or 127.0.0.1:5500

---

## 📋 Quick Command Reference

```bash
# Navigate to project
cd /Users/sunitachoudhary/Desktop/MaintenanceTracker-main

# Activate virtual environment (if using)
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run server
python manage.py runserver

# Stop server
# Press Ctrl+C in terminal
```

---

## ✅ Verification Checklist

Before accessing the site, make sure:

- [ ] Virtual environment is activated (if using)
- [ ] Dependencies are installed (`pip install -r requirements.txt`)
- [ ] Migrations are run (`python manage.py migrate`)
- [ ] Server is running (`python manage.py runserver`)
- [ ] You see "Starting development server at http://127.0.0.1:8000/"
- [ ] You're accessing via http://127.0.0.1:8000/ (NOT file://)
- [ ] Browser cache is cleared

---

## 🎯 First Time Setup (Complete)

```bash
# 1. Navigate to project
cd /Users/sunitachoudhary/Desktop/MaintenanceTracker-main

# 2. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Mac/Linux

# 3. Install Django and dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Create admin account (optional)
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic --noinput

# 7. Run server
python manage.py runserver
```

Then open: **http://127.0.0.1:8000/accounts/login/**

---

## 📝 Notes

- **Always run the Django server** - Don't open HTML files directly
- **Use port 8000** - That's Django's default development server
- **Clear browser cache** if styles don't appear
- **Check terminal** for error messages if something doesn't work

---

## 🆘 Still Having Issues?

1. **Check Python version:**
   ```bash
   python --version
   # Should be Python 3.8 or higher
   ```

2. **Check Django installation:**
   ```bash
   python manage.py --version
   ```

3. **Check for errors in terminal:**
   - Look for red error messages
   - Copy the error and check what it says

4. **Verify file structure:**
   - Make sure `manage.py` exists in project root
   - Make sure `static/style.css` exists
   - Make sure templates are in correct folders

---

**Your website should now be running! 🎉**

