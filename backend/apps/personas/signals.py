from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission

@receiver(post_migrate)
def crear_roles_y_permisos(sender, **kwargs):
    roles = [
        {"nombre": "Maestro", "permisos": [
            "add_nota", "change_nota", "delete_nota", "view_nota",
            "add_asistencia", "change_asistencia", "delete_asistencia", "view_asistencia",
            "add_participacion", "change_participacion", "delete_participacion", "view_participacion",
        ]},
        {"nombre": "Alumno", "permisos": [
            "view_nota", "view_asistencia", "view_participacion",
        ]},
        {"nombre": "Tutor", "permisos": [
            "view_nota", "view_asistencia", "view_participacion",
        ]},
    ]
    for rol in roles:
        group, _ = Group.objects.get_or_create(name=rol["nombre"])
        group.permissions.clear()
        for codename in rol["permisos"]:
            try:
                perm = Permission.objects.get(codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass
    print("✅ Roles y permisos actualizados automáticamente.")
