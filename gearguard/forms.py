from django import forms
from .models import Equipment, MaintenanceRequest, MaintenanceTeam
from django.contrib.auth.models import User


class EquipmentForm(forms.ModelForm):
    """Form for creating and updating equipment"""
    
    class Meta:
        model = Equipment
        fields = [
            'name', 
            'serial_number', 
            'category', 
            'department',
            'location', 
            'maintenance_team',
            'assigned_employee',
            'default_technician',
            'purchase_date',
            'warranty_expiry',
            'notes'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Equipment name'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serial number'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Location'}),
            'maintenance_team': forms.Select(attrs={'class': 'form-control'}),
            'assigned_employee': forms.Select(attrs={'class': 'form-control'}),
            'default_technician': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'warranty_expiry': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional notes'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['assigned_employee'].required = False
        self.fields['default_technician'].required = False
        self.fields['maintenance_team'].required = False
        self.fields['purchase_date'].required = False
        self.fields['warranty_expiry'].required = False
        self.fields['notes'].required = False


class MaintenanceRequestForm(forms.ModelForm):
    """Form for creating and updating maintenance requests"""
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'equipment',
            'request_type',
            'subject',
            'description',
            'priority',
            'stage',
            'maintenance_team',
            'assigned_to',
            'scheduled_date',
        ]
        widgets = {
            'equipment': forms.Select(attrs={'class': 'form-control'}),
            'request_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief description'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detailed description'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'stage': forms.Select(attrs={'class': 'form-control'}),
            'maintenance_team': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields optional
        self.fields['assigned_to'].required = False
        self.fields['scheduled_date'].required = False
        self.fields['maintenance_team'].required = False
        
        # Filter assigned_to to only show users who are team members
        from .models import TeamMember
        technician_ids = TeamMember.objects.values_list('user_id', flat=True)
        self.fields['assigned_to'].queryset = User.objects.filter(id__in=technician_ids)
        
        # Set default stage for new requests
        if not self.instance.pk:
            self.fields['stage'].initial = 'new'