from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Equipment, MaintenanceRequest, MaintenanceTeam, TeamMember, MaintenanceLog
from .forms import EquipmentForm, MaintenanceRequestForm
import json

@login_required
def dashboard(request):
    """Main dashboard view"""
    # Critical equipment (high maintenance requests)
    critical_equipment = Equipment.objects.annotate(
        request_count=Count('maintenance_requests', 
            filter=Q(maintenance_requests__created_at__gte=timezone.now()-timedelta(days=30))
        )
    ).filter(request_count__gte=3, is_scrapped=False).order_by('-request_count')[:5]
    
    # Open requests stats
    open_requests = MaintenanceRequest.objects.exclude(stage__in=['repaired', 'scrap'])
    pending_requests = open_requests.filter(stage='new').count()
    overdue_requests = open_requests.filter(scheduled_date__lt=timezone.now().date()).count()
    
    # Technician utilization (for current user if they're a technician)
    user_team_membership = TeamMember.objects.filter(user=request.user).first()
    technician_stats = None
    if user_team_membership:
        assigned_count = MaintenanceRequest.objects.filter(
            assigned_to=request.user,
            stage__in=['new', 'in_progress']
        ).count()
        total_assigned = MaintenanceRequest.objects.filter(assigned_to=request.user).count()
        if total_assigned > 0:
            technician_stats = {
                'assigned': assigned_count,
                'total': total_assigned,
                'utilization': round((assigned_count / total_assigned) * 100) if total_assigned else 0
            }
    
    # Recent requests
    recent_requests = MaintenanceRequest.objects.select_related(
        'equipment', 'assigned_to', 'maintenance_team'
    ).order_by('-created_at')[:10]
    
    context = {
        'critical_equipment': critical_equipment,
        'pending_requests': pending_requests,
        'overdue_requests': overdue_requests,
        'technician_stats': technician_stats,
        'recent_requests': recent_requests,
        'today': timezone.now().date(),
    }
    return render(request, 'gearguard/dashboard.html', context)


@login_required
def equipment_list(request):
    """List all equipment"""
    equipment = Equipment.objects.filter(is_scrapped=False).select_related(
        'maintenance_team', 'assigned_employee', 'default_technician'
    )
    
    # Filters
    category = request.GET.get('category')
    department = request.GET.get('department')
    team = request.GET.get('team')
    search = request.GET.get('search')
    
    if category:
        equipment = equipment.filter(category=category)
    if department:
        equipment = equipment.filter(department=department)
    if team:
        equipment = equipment.filter(maintenance_team_id=team)
    if search:
        equipment = equipment.filter(
            Q(name__icontains=search) | 
            Q(serial_number__icontains=search) |
            Q(location__icontains=search)
        )
    
    context = {
        'equipment_list': equipment,
        'categories': Equipment.CATEGORY_CHOICES,
        'departments': Equipment.DEPARTMENT_CHOICES,
        'teams': MaintenanceTeam.objects.all(),
        'selected_category': category,
        'selected_department': department,
        'selected_team': team,
        'search_query': search,
    }
    return render(request, 'gearguard/equipment_detail.html', context)


@login_required
def equipment_detail(request, pk):
    """Equipment detail with maintenance history"""
    equipment = get_object_or_404(Equipment, pk=pk)
    maintenance_requests = equipment.maintenance_requests.all().order_by('-created_at')
    
    context = {
        'equipment': equipment,
        'maintenance_requests': maintenance_requests,
        'open_requests_count': equipment.get_open_requests_count(),
        'today': timezone.now().date(),
    }
    return render(request, 'gearguard/equipment_detail.html', context)


@login_required
def equipment_create(request):
    """Create new equipment"""
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            equipment = form.save()
            messages.success(request, f'Equipment {equipment.name} created successfully!')
            return redirect('equipment_detail', pk=equipment.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EquipmentForm()
    
    return render(request, 'gearguard/equipment_form.html', {'form': form, 'action': 'Create'})


@login_required
def equipment_update(request, pk):
    """Update equipment"""
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, f'Equipment {equipment.name} updated successfully!')
            return redirect('equipment_detail', pk=equipment.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EquipmentForm(instance=equipment)
    
    return render(request, 'gearguard/equipment_form.html', {
        'form': form, 
        'action': 'Update', 
        'equipment': equipment
    })


@login_required
def kanban_board(request):
    """Kanban board for maintenance requests"""
    team_filter = request.GET.get('team')
    
    requests_qs = MaintenanceRequest.objects.select_related(
        'equipment', 'assigned_to', 'maintenance_team'
    )
    
    if team_filter:
        requests_qs = requests_qs.filter(maintenance_team_id=team_filter)
    else:
        # Get user's team if they're a technician
        user_team = TeamMember.objects.filter(user=request.user).first()
        if user_team:
            requests_qs = requests_qs.filter(maintenance_team=user_team.team)
    
    requests = {
        'new': requests_qs.filter(stage='new').order_by('-priority', '-created_at'),
        'in_progress': requests_qs.filter(stage='in_progress').order_by('-priority', '-created_at'),
        'repaired': requests_qs.filter(stage='repaired').order_by('-completed_date')[:20],  # Limit repaired
        'scrap': requests_qs.filter(stage='scrap').order_by('-updated_at')[:10],  # Limit scrap
    }
    
    context = {
        'requests': requests,
        'teams': MaintenanceTeam.objects.all(),
        'selected_team': team_filter,
    }
    return render(request, 'gearguard/kanban_board.html', context)


@login_required
def request_create(request):
    """Create maintenance request"""
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST)
        if form.is_valid():
            maintenance_request = form.save(commit=False)
            maintenance_request.created_by = request.user
            maintenance_request.save()
            
            # Log creation
            MaintenanceLog.objects.create(
                request=maintenance_request,
                user=request.user,
                action='Request created',
                notes=f'Initial request: {maintenance_request.subject}'
            )
            
            messages.success(request, 'Maintenance request created successfully!')
            return redirect('kanban_board')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MaintenanceRequestForm()
        
        # Pre-fill equipment if provided
        equipment_id = request.GET.get('equipment')
        if equipment_id:
            try:
                equipment = Equipment.objects.get(pk=equipment_id)
                form.initial['equipment'] = equipment
                form.initial['maintenance_team'] = equipment.maintenance_team
            except Equipment.DoesNotExist:
                pass
        
        # Pre-fill scheduled date if provided
        scheduled_date = request.GET.get('scheduled_date')
        if scheduled_date:
            form.initial['scheduled_date'] = scheduled_date
    
    return render(request, 'gearguard/request_form.html', {'form': form, 'action': 'Create'})


@login_required
def request_update(request, pk):
    """Update maintenance request"""
    maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
    old_stage = maintenance_request.stage
    old_assigned = maintenance_request.assigned_to
    
    if request.method == 'POST':
        form = MaintenanceRequestForm(request.POST, instance=maintenance_request)
        if form.is_valid():
            updated_request = form.save()
            
            # Log changes
            changes = []
            if old_stage != updated_request.stage:
                changes.append(f'Stage: {old_stage} → {updated_request.stage}')
            if old_assigned != updated_request.assigned_to:
                old_name = old_assigned.get_full_name() if old_assigned else 'Unassigned'
                new_name = updated_request.assigned_to.get_full_name() if updated_request.assigned_to else 'Unassigned'
                changes.append(f'Assigned: {old_name} → {new_name}')
            
            if changes:
                MaintenanceLog.objects.create(
                    request=updated_request,
                    user=request.user,
                    action='Request updated',
                    notes=', '.join(changes)
                )
            
            messages.success(request, 'Maintenance request updated successfully!')
            return redirect('kanban_board')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = MaintenanceRequestForm(instance=maintenance_request)
    
    # Get logs for this request
    logs = maintenance_request.logs.all()[:10]
    
    return render(request, 'gearguard/request_form.html', {
        'form': form,
        'action': 'Update',
        'request': maintenance_request,
        'logs': logs,
    })


@login_required
def request_update_stage(request, pk):
    """API endpoint to update request stage (for drag & drop)"""
    if request.method == 'POST':
        maintenance_request = get_object_or_404(MaintenanceRequest, pk=pk)
        new_stage = request.POST.get('stage')
        
        if new_stage in dict(MaintenanceRequest.STAGE_CHOICES):
            old_stage = maintenance_request.stage
            maintenance_request.stage = new_stage
            
            # Auto-assign if moving to in_progress and not assigned
            if new_stage == 'in_progress' and not maintenance_request.assigned_to:
                maintenance_request.assigned_to = request.user
            
            # Set completed date if moved to repaired
            if new_stage == 'repaired' and not maintenance_request.completed_date:
                maintenance_request.completed_date = timezone.now()
            
            maintenance_request.save()
            
            # Log the change
            MaintenanceLog.objects.create(
                request=maintenance_request,
                user=request.user,
                action=f'Stage changed',
                notes=f'From {old_stage} to {new_stage}'
            )
            
            return JsonResponse({
                'status': 'success', 
                'message': 'Stage updated',
                'new_stage': new_stage
            })
        
        return JsonResponse({'status': 'error', 'message': 'Invalid stage'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


@login_required
def calendar_view(request):
    """Calendar view for preventive maintenance"""
    # Get all preventive maintenance requests
    preventive_requests = MaintenanceRequest.objects.filter(
        request_type='preventive'
    ).select_related('equipment', 'assigned_to')
    
    # Filter by date range if provided (for FullCalendar AJAX)
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    if start_date and end_date:
        preventive_requests = preventive_requests.filter(
            scheduled_date__range=[start_date, end_date]
        )
    
    # Convert to calendar event format
    events = []
    for req in preventive_requests:
        if req.scheduled_date:
            # Determine color based on stage and overdue status
            if req.stage == 'repaired':
                bg_color = '#28a745'
                border_color = '#28a745'
            elif req.is_overdue():
                bg_color = '#dc3545'
                border_color = '#dc3545'
            elif req.stage == 'in_progress':
                bg_color = '#17a2b8'
                border_color = '#17a2b8'
            else:
                bg_color = '#3788d8'
                border_color = '#3788d8'
            
            events.append({
                'id': req.id,
                'title': f"{req.equipment.name}: {req.subject}",
                'start': req.scheduled_date.isoformat(),
                'backgroundColor': bg_color,
                'borderColor': border_color,
                'url': f'/requests/{req.id}/update/',
                'extendedProps': {
                    'stage': req.stage,
                    'priority': req.priority,
                    'assigned_to': req.assigned_to.get_full_name() if req.assigned_to else 'Unassigned'
                }
            })
    
    # If this is an AJAX request for events, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(events, safe=False)
    
    context = {
        'events_json': json.dumps(events),
    }
    return render(request, 'gearguard/calendar.html', context)


@login_required
def reporting(request):
    """Reporting and analytics"""
    # Requests by team
    requests_by_team = MaintenanceTeam.objects.annotate(
        total_requests=Count('requests'),
        open_requests=Count('requests', filter=Q(requests__stage__in=['new', 'in_progress'])),
        completed_requests=Count('requests', filter=Q(requests__stage='repaired'))
    ).order_by('-total_requests')
    
    # Requests by equipment category
    from django.db.models import Value
    from django.db.models.functions import Coalesce
    
    requests_by_category = []
    for category_code, category_name in Equipment.CATEGORY_CHOICES:
        count = MaintenanceRequest.objects.filter(equipment__category=category_code).count()
        if count > 0:
            requests_by_category.append({
                'category': category_name,
                'count': count
            })
    requests_by_category.sort(key=lambda x: x['count'], reverse=True)
    
    # Requests by priority
    requests_by_priority = []
    for priority_code, priority_name in MaintenanceRequest.PRIORITY_CHOICES:
        count = MaintenanceRequest.objects.filter(priority=priority_code).count()
        requests_by_priority.append({
            'priority': priority_name,
            'count': count
        })
    
    # Monthly trend (last 6 months)
    current_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_6_months = []
    for i in range(6):
        month = current_month - timedelta(days=30*i)
        count = MaintenanceRequest.objects.filter(
            created_at__year=month.year,
            created_at__month=month.month
        ).count()
        last_6_months.append({
            'month': month.strftime('%B %Y'),
            'count': count
        })
    last_6_months.reverse()
    
    # Overall statistics
    total_equipment = Equipment.objects.filter(is_scrapped=False).count()
    total_requests = MaintenanceRequest.objects.count()
    open_requests = MaintenanceRequest.objects.exclude(stage__in=['repaired', 'scrap']).count()
    avg_resolution_time = MaintenanceRequest.objects.filter(
        stage='repaired',
        duration_hours__isnull=False
    ).aggregate(avg=Count('duration_hours'))
    
    context = {
        'requests_by_team': requests_by_team,
        'requests_by_category': requests_by_category,
        'requests_by_priority': requests_by_priority,
        'monthly_trend': last_6_months,
        'total_equipment': total_equipment,
        'total_requests': total_requests,
        'open_requests': open_requests,
    }
    return render(request, 'gearguard/reporting.html', context)


@login_required
def teams_list(request):
    """List all maintenance teams"""
    teams = MaintenanceTeam.objects.annotate(
        member_count=Count('members'),
        request_count=Count('requests'),
        open_request_count=Count('requests', filter=Q(requests__stage__in=['new', 'in_progress']))
    ).prefetch_related('members__user')
    
    context = {
        'teams': teams,
    }
    return render(request, 'gearguard/teams_list.html', context)


# AJAX endpoint for auto-filling equipment details
@login_required
def get_equipment_details(request, pk):
    """API endpoint to get equipment details for auto-fill"""
    try:
        equipment = Equipment.objects.select_related('maintenance_team', 'default_technician').get(pk=pk)
        return JsonResponse({
            'status': 'success',
            'data': {
                'maintenance_team': equipment.maintenance_team.id if equipment.maintenance_team else None,
                'maintenance_team_name': equipment.maintenance_team.name if equipment.maintenance_team else '',
                'default_technician': equipment.default_technician.id if equipment.default_technician else None,
                'category': equipment.category,
                'department': equipment.department,
            }
        })
    except Equipment.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Equipment not found'}, status=404)