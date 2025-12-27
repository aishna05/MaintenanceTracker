from django.urls import path
from . import views

app_name = 'gearguard'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Equipment
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/<int:pk>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/create/', views.equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/update/', views.equipment_update, name='equipment_update'),
    
    # Maintenance Requests
    path('kanban/', views.kanban_board, name='kanban_board'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:pk>/update/', views.request_update, name='request_update'),
    path('requests/<int:pk>/update-stage/', views.request_update_stage, name='request_update_stage'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar_view'),
    
    # Reporting
    path('reporting/', views.reporting, name='reporting'),
    
    # Teams
    path('teams/', views.teams_list, name='teams_list'),
]