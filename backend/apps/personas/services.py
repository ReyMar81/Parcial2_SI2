from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from apps.personas.models import Persona, Alumno, Maestro, Tutor

User = get_user_model()

def crear_usuario_persona_rol(persona_data, rol, **extra_fields):
    # ---- FILTRAR SOLO LOS CAMPOS DE PERSONA ----
    persona_fields = [
        'nombre', 'apellido_paterno', 'apellido_materno', 'genero',
        'ci', 'direccion', 'contacto', 'fecha_nacimiento'
    ]
    # Extrae solo los campos válidos de persona
    persona_clean = {k: v for k, v in persona_data.items() if k in persona_fields}

    ci = persona_clean['ci']
    apellidos = f"{persona_clean['apellido_paterno']} {persona_clean.get('apellido_materno','')}".upper().strip()
    iniciales = "".join([ap[0] for ap in apellidos.split() if ap])
    from datetime import datetime
    año = datetime.now().year

    # Definir registro y grupo según el rol
    if rol == 'alumno':
        secuencia = Alumno.objects.count() + 1
        registro = f"{año}02{str(secuencia).zfill(2)}.{iniciales}"
        username = registro
        group_name = 'Alumno'
        model = Alumno
        create_kwargs = dict(registro=registro)
    elif rol == 'maestro':
        secuencia = Maestro.objects.count() + 1
        registro = f"{año}01{str(secuencia).zfill(2)}.{iniciales}"
        username = registro
        group_name = 'Maestro'
        model = Maestro
        create_kwargs = dict(registro=registro, **extra_fields)
    elif rol == 'tutor':
        username = f"{ci}.{iniciales}"
        group_name = 'Tutor'
        model = Tutor
        create_kwargs = dict(**extra_fields)
    else:
        raise ValueError("Rol no reconocido")

    password = ci

    user = User.objects.create_user(username=username, password=password)
    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    user.save()

    persona = Persona.objects.create(usuario=user, **persona_clean)
    rol_instance = model.objects.create(persona=persona, **create_kwargs)
    return rol_instance
