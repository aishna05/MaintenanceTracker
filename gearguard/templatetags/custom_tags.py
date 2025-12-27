from django import template
from gearguard.models import Equipment, MaintenanceTeam

register = template.Library()

@register.simple_tag
def get_equipment_count():
    return Equipment.objects.count()

@register.simple_tag
def get_teams_count():
    return MaintenanceTeam.objects.count()
