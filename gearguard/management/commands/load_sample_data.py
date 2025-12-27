# gearguard/management/commands/load_sample_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gearguard.models import MaintenanceTeam, TeamMember, Equipment, MaintenanceRequest
from django.utils import timezone
from datetime import timedelta
import random

class Command(BaseCommand):
    help = 'Load sample data for GearGuard'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading sample data...')
        
        # Create sample users (technicians)
        users = []
        for i, name in enumerate(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Williams'], 1):
            first, last = name.split()
            username = f"{first.lower()}.{last.lower()}"
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'email': f'{username}@example.com',
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {username}')
            users.append(user)
        
        # Create maintenance teams
        teams_data = [
            {'name': 'IT Support', 'description': 'Computer and network equipment maintenance'},
            {'name': 'Mechanics', 'description': 'Machinery and vehicle maintenance'},
            {'name': 'Electricians', 'description': 'Electrical equipment maintenance'},
            {'name': 'Facilities', 'description': 'Building and HVAC maintenance'},
        ]
        
        teams = []
        for team_data in teams_data:
            team, created = MaintenanceTeam.objects.get_or_create(
                name=team_data['name'],
                defaults={'description': team_data['description']}
            )
            if created:
                self.stdout.write(f'Created team: {team.name}')
            teams.append(team)
        
        # Assign users to teams
        for i, user in enumerate(users):
            team = teams[i % len(teams)]
            TeamMember.objects.get_or_create(
                user=user,
                team=team,
                defaults={'is_lead': i < 2}
            )
        
        # Create sample equipment
        equipment_data = [
            {'name': 'Printer 01', 'serial': 'PR-001', 'category': 'printer', 'dept': 'administration', 'team': teams[0], 'location': 'Office Floor 2'},
            {'name': 'CNC Machine Alpha', 'serial': 'CNC-A-001', 'category': 'machinery', 'dept': 'production', 'team': teams[1], 'location': 'Factory Floor 1'},
            {'name': 'Laptop-HR-05', 'serial': 'LT-HR-005', 'category': 'computer', 'dept': 'hr', 'team': teams[0], 'location': 'HR Department'},
            {'name': 'Forklift 03', 'serial': 'FK-003', 'category': 'vehicle', 'dept': 'logistics', 'team': teams[1], 'location': 'Warehouse'},
            {'name': 'HVAC Unit B', 'serial': 'HVAC-B-01', 'category': 'hvac', 'dept': 'maintenance', 'team': teams[3], 'location': 'Building B Roof'},
            {'name': 'Server Rack 1', 'serial': 'SRV-RK-01', 'category': 'computer', 'dept': 'it', 'team': teams[0], 'location': 'Data Center'},
            {'name': 'Laser Cutter', 'serial': 'LC-001', 'category': 'machinery', 'dept': 'production', 'team': teams[1], 'location': 'Factory Floor 2'},
            {'name': 'Generator Main', 'serial': 'GEN-M-01', 'category': 'electrical', 'dept': 'maintenance', 'team': teams[2], 'location': 'Generator Room'},
        ]
        
        equipment_list = []
        for eq_data in equipment_data:
            equipment, created = Equipment.objects.get_or_create(
                serial_number=eq_data['serial'],
                defaults={
                    'name': eq_data['name'],
                    'category': eq_data['category'],
                    'department': eq_data['dept'],
                    'maintenance_team': eq_data['team'],
                    'location': eq_data['location'],
                    'purchase_date': timezone.now().date() - timedelta(days=random.randint(365, 1095)),
                    'warranty_expiry': timezone.now().date() + timedelta(days=random.randint(-180, 365)),
                    'assigned_employee': random.choice(users),
                    'default_technician': random.choice([tm.user for tm in TeamMember.objects.filter(team=eq_data['team'])])
                }
            )
            if created:
                self.stdout.write(f'Created equipment: {equipment.name}')
            equipment_list.append(equipment)
        
        # Create sample maintenance requests
        request_subjects = [
            'Oil leak detected',
            'Strange noise during operation',
            'Software update required',
            'Routine checkup',
            'Power fluctuation issue',
            'Overheating problem',
            'Scheduled maintenance',
            'Belt replacement needed',
            'Filter cleaning',
            'Calibration required',
        ]
        
        priorities = ['low', 'medium', 'high', 'critical']
        stages = ['new', 'new', 'in_progress', 'repaired']
        request_types = ['corrective', 'preventive']
        
        for i in range(20):
            equipment = random.choice(equipment_list)
            request_type = random.choice(request_types)
            stage = random.choice(stages)
            
            MaintenanceRequest.objects.create(
                subject=random.choice(request_subjects),
                description=f'Sample maintenance request #{i+1}',
                request_type=request_type,
                priority=random.choice(priorities),
                equipment=equipment,
                maintenance_team=equipment.maintenance_team,
                assigned_to=random.choice(users) if stage != 'new' else None,
                created_by=random.choice(users),
                scheduled_date=timezone.now().date() + timedelta(days=random.randint(-7, 14)),
                stage=stage,
                duration_hours=random.uniform(0.5, 8.0) if stage == 'repaired' else None,
                completed_date=timezone.now() if stage == 'repaired' else None,
            )
        
        self.stdout.write(self.style.SUCCESS('✅ Sample data loaded successfully!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'  - {len(users)} users')
        self.stdout.write(f'  - {len(teams)} teams')
        self.stdout.write(f'  - {len(equipment_list)} equipment items')
        self.stdout.write(f'  - 20 maintenance requests')
        self.stdout.write('')
        self.stdout.write('Test credentials:')
        self.stdout.write('  Username: john.doe')
        self.stdout.write('  Password: password123')