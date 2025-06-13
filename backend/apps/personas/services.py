from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from apps.personas.models import Persona, Alumno, Maestro, Tutor
from datetime import datetime
from django.db.models import Max
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from django.conf import settings

User = get_user_model()

def crear_usuario_persona_rol(persona_data, rol, ciclo_anio=None, **extra_fields):
    # ---- FILTRAR SOLO LOS CAMPOS DE PERSONA ----
    persona_fields = [
        'nombre', 'apellido_paterno', 'apellido_materno', 'genero',
        'ci', 'direccion', 'contacto', 'fecha_nacimiento'
    ]
    persona_clean = {k: v for k, v in persona_data.items() if k in persona_fields}

    ci = persona_clean['ci']
    apellidos = f"{persona_clean['apellido_paterno']} {persona_clean.get('apellido_materno','')}".upper().strip()
    iniciales = "".join([ap[0] for ap in apellidos.split() if ap])
    if ciclo_anio is not None:
        año = ciclo_anio
    else:
        año = datetime.now().year

    # Definir registro y grupo según el rol
    if rol == 'alumno':
        base_registro = f"{año}02"
        # Encuentra el registro mayor para el año actual
        max_registro = Alumno.objects.filter(registro__startswith=base_registro).aggregate(Max('registro'))['registro__max']
        if max_registro:
            last_seq = int(max_registro[-4:])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        registro = f"{año}02{str(next_seq).zfill(4)}"
        base_username = f"{registro}.{iniciales}"
        username = base_username
        sufijo = 2
        # Si ya existe, agrégale un sufijo hasta que sea único
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{sufijo}"
            sufijo += 1
        group_name = 'Alumno'
        model = Alumno
        create_kwargs = dict(registro=registro)
    elif rol == 'maestro':
        base_registro = f"{año}01"
        max_registro = Maestro.objects.filter(registro__startswith=base_registro).aggregate(Max('registro'))['registro__max']
        if max_registro:
            last_seq = int(max_registro[-4:])
            next_seq = last_seq + 1
        else:
            next_seq = 1
        registro = f"{año}01{str(next_seq).zfill(4)}"
        base_username = f"{registro}.{iniciales}"
        username = base_username
        sufijo = 2
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{sufijo}"
            sufijo += 1
        group_name = 'Maestro'
        model = Maestro
        create_kwargs = dict(registro=registro, **extra_fields)
    elif rol == 'tutor':
        base_username = f"{ci}.{iniciales}"
        username = base_username
        sufijo = 2
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{sufijo}"
            sufijo += 1
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

def send_fcm_v1_notification(token, title, body, data=None):
    print(f"[FCM DEBUG] Intentando enviar notificación a token: {token}")
    print(f"[FCM DEBUG] Título: {title} | Mensaje: {body}")
    credentials = service_account.Credentials.from_service_account_file(
        settings.FIREBASE_CREDENTIALS,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )
    credentials.refresh(Request())

    message = {
        "message": {
            "token": token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }
    if data:
        message["message"]["data"] = data
    print(f"[FCM DEBUG] Payload: {json.dumps(message)}")

    url = f"https://fcm.googleapis.com/v1/projects/{settings.FIREBASE_PROJECT_ID}/messages:send"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json; UTF-8",
    }

    response = requests.post(url, headers=headers, data=json.dumps(message))
    print(f"[FCM DEBUG] Respuesta de FCM: {response.status_code} - {response.text}")
    if response.status_code != 200:
        print(f"[FCM v1 ERROR] {response.status_code}: {response.text}")
    return response