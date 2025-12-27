# MaintenanceTracker

## Authentication Module 


### Features

Signup & Login

Forgot Password (email reset)

Secure authentication

Protected Dashboard

Tech Stack

Django

PostgreSQL

Django Auth System

Flow

Signup/Login → Dashboard

Forgot Password → Reset via Email → Login

Notes

Passwords are securely hashed

Reset links shown in console (dev)

Dashboard requires login

# GearGuard - Maintenance Management System

A comprehensive Django-based maintenance tracking system for managing equipment, teams, and maintenance requests.

## Features

- **Equipment Management**: Track all company assets with detailed information
- **Maintenance Teams**: Organize technicians into specialized teams
- **Request Tracking**: Manage corrective and preventive maintenance
- **Kanban Board**: Drag-and-drop interface for workflow management
- **Calendar View**: Schedule preventive maintenance
- **Dashboard**: Real-time analytics and insights
- **Smart Automation**: Auto-fill team assignments based on equipment

## Installation

### 1. Create Django App

```bash
# In your Django project
python manage.py startapp gearguard
```

### 2. Add to settings.py

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'gearguard',  # Add this
]
```

### 3. Copy Files

Place the provided files in the following structure:

```
gearguard/
├── __init__.py
├── models.py          # Database models
├── admin.py           # Admin configuration
├── views.py           # View functions
├── forms.py           # Form definitions
├── urls.py            # URL routing
├── templates/
│   └── gearguard/
│       ├── dashboard.html
│       ├── kanban_board.html
│       ├── calendar.html
│       ├── equipment_list.html
│       ├── equipment_detail.html
│       ├── equipment_form.html
│       ├── request_form.html
│       ├── reporting.html
│       └── teams_list.html
└── static/
    └── gearguard/
        └── css/
            └── custom.css
```

### 4. Update Main urls.py

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gearguard.urls')),
]
```

### 5. Create Base Template

Create `templates/base.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}GearGuard{% endblock %}</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% if user.is_authenticated %}
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="{% url 'dashboard' %}">
                <i class="fas fa-tools"></i> GearGuard
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'dashboard' %}">Dashboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'kanban_board' %}">Kanban</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'calendar_view' %}">Calendar</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'equipment_list' %}">Equipment</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'teams_list' %}">Teams</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="{% url 'reporting' %}">Reports</a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i class="fas fa-user"></i> {{ user.username }}
                        </a>
                        <ul class="dropdown-menu dropdown-menu-end">
                            <li><a class="dropdown-item" href="{% url 'admin:index' %}">Admin</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{% url 'logout' %}">Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    {% endif %}

    {% if messages %}
    <div class="container mt-3">
        {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% block content %}{% endblock %}

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 6. Run Migrations

```bash
python manage.py makemigrations gearguard
python manage.py migrate
```

### 7. Create Superuser

```bash
python manage.py createsuperuser
```

### 8. Load Sample Data (Optional)

Create `gearguard/management/commands/load_sample_data.py`:

```python
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gearguard.models import MaintenanceTeam, TeamMember, Equipment

class Command(BaseCommand):
    help = 'Load sample data for GearGuard'

    def handle(self, *args, **kwargs):
        # Create teams
        it_team = MaintenanceTeam.objects.create(
            name='IT Support',
            description='Computer and network equipment'
        )
        mech_team = MaintenanceTeam.objects.create(
            name='Mechanics',
            description='Machinery and vehicle maintenance'
        )
        
        # Create sample equipment
        Equipment.objects.create(
            name='Printer 01',
            serial_number='PR-001',
            category='printer',
            department='administration',
            maintenance_team=it_team,
            location='Office Building Floor 2'
        )
        
        self.stdout.write(self.style.SUCCESS('Sample data loaded successfully'))
```

Run: `python manage.py load_sample_data`

### 9. Run Server

```bash
python manage.py runserver
```

Visit: `http://localhost:8000/`

## Usage

### Creating Equipment
1. Go to Equipment → Add Equipment
2. Fill in details and assign to a maintenance team
3. Save

### Creating Maintenance Requests
1. Click "New Request" from dashboard or Kanban board
2. Select equipment (team auto-fills)
3. Choose request type (Corrective or Preventive)
4. Set priority and scheduled date
5. Submit

### Using Kanban Board
1. View requests organized by stage
2. Drag and drop cards to update status
3. Click edit to add details or duration

### Scheduling Preventive Maintenance
1. Go to Calendar view
2. Click on a date
3. Create a preventive maintenance request

## Key Features Explained

### Auto-Fill Logic
When creating a request, selecting equipment automatically fills:
- Maintenance team
- Default technician

### Smart Buttons
Equipment detail pages show:
- Count of open maintenance requests
- Quick link to related requests

### Scrap Logic
Moving a request to "Scrap" stage automatically:
- Marks equipment as scrapped
- Records scrap date

### Overdue Detection
Requests are marked overdue if:
- Scheduled date has passed
- Status is not "Repaired" or "Scrap"

## Customization

### Adding Custom Fields
Edit `models.py` and add fields to models, then run migrations.

### Changing Stages
Modify `STAGE_CHOICES` in MaintenanceRequest model.

### Adding Reports
Create new views in `views.py` and templates for custom analytics.

## Troubleshooting

**Issue**: Drag and drop not working
- Check that JavaScript is enabled
- Ensure CSRF token is properly set

**Issue**: Calendar not displaying
- Verify FullCalendar CDN is loading
- Check browser console for errors

**Issue**: Auto-fill not working
- Ensure equipment has maintenance_team assigned
- Check form JavaScript in template

## Support

For issues and questions:
- Check the Django documentation
- Review the code comments
- Test with sample data first