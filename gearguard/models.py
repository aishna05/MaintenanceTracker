from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class MaintenanceTeam(models.Model):
    """Teams responsible for maintenance work"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_member_count(self):
        return self.members.count()
    
    class Meta:
        ordering = ['name']


class TeamMember(models.Model):
    """Link between users and maintenance teams"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='team_memberships')
    team = models.ForeignKey(MaintenanceTeam, on_delete=models.CASCADE, related_name='members')
    is_lead = models.BooleanField(default=False)
    joined_date = models.DateField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'team']
        ordering = ['-is_lead', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.team.name}"


class Equipment(models.Model):
    """Assets/machines that need maintenance"""
    DEPARTMENT_CHOICES = [
        ('production', 'Production'),
        ('it', 'IT'),
        ('logistics', 'Logistics'),
        ('administration', 'Administration'),
        ('maintenance', 'Maintenance'),
        ('hr', 'Human Resources'),
    ]
    
    CATEGORY_CHOICES = [
        ('computer', 'Computer'),
        ('printer', 'Printer'),
        ('vehicle', 'Vehicle'),
        ('machinery', 'Machinery'),
        ('hvac', 'HVAC'),
        ('electrical', 'Electrical'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=200)
    serial_number = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    
    # Ownership
    assigned_employee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_equipment'
    )
    
    # Maintenance responsibility
    maintenance_team = models.ForeignKey(
        MaintenanceTeam,
        on_delete=models.SET_NULL,
        null=True,
        related_name='equipment'
    )
    default_technician = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='default_equipment'
    )
    
    # Purchase info
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=200)
    
    # Status
    is_scrapped = models.BooleanField(default=False)
    scrapped_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"
    
    def get_open_requests_count(self):
        return self.maintenance_requests.exclude(stage='repaired').exclude(stage='scrap').count()
    
    def get_health_status(self):
        """Calculate equipment health based on recent requests"""
        recent_requests = self.maintenance_requests.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        
        if recent_requests >= 5:
            return 'critical'
        elif recent_requests >= 3:
            return 'warning'
        return 'good'
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Equipment'


class MaintenanceRequest(models.Model):
    """Maintenance work requests"""
    REQUEST_TYPE_CHOICES = [
        ('corrective', 'Corrective (Breakdown)'),
        ('preventive', 'Preventive (Routine)'),
    ]
    
    STAGE_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('repaired', 'Repaired'),
        ('scrap', 'Scrap'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    # Basic info
    subject = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='corrective')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Related entities
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name='maintenance_requests'
    )
    maintenance_team = models.ForeignKey(
        MaintenanceTeam,
        on_delete=models.SET_NULL,
        null=True,
        related_name='requests'
    )
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_requests'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_requests'
    )
    
    # Scheduling
    scheduled_date = models.DateField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Duration tracking
    duration_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Hours spent on repair"
    )
    
    # Stage management
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='new')
    
    # Metadata
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.subject} - {self.equipment.name}"
    
    def is_overdue(self):
        """Check if request is overdue"""
        if self.stage in ['repaired', 'scrap']:
            return False
        if self.scheduled_date and self.scheduled_date < timezone.now().date():
            return True
        return False
    
    def save(self, *args, **kwargs):
        # Auto-fill logic: populate team from equipment
        if self.equipment and not self.maintenance_team:
            self.maintenance_team = self.equipment.maintenance_team
        
        # Mark completion date when moved to repaired
        if self.stage == 'repaired' and not self.completed_date:
            self.completed_date = timezone.now()
        
        # Handle scrap logic
        if self.stage == 'scrap' and not self.equipment.is_scrapped:
            self.equipment.is_scrapped = True
            self.equipment.scrapped_date = timezone.now()
            self.equipment.save()
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['stage', 'scheduled_date']),
            models.Index(fields=['equipment', 'stage']),
        ]


class MaintenanceLog(models.Model):
    """Log entries for maintenance activities"""
    request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name='logs'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.request.subject}"