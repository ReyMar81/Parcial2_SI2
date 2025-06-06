#!/bin/bash
set -e

cd /app

echo "🔄 Ejecutando makemigrations para todas las apps..."
python manage.py makemigrations

echo "🔄 Ejecutando migrate..."
python manage.py migrate --noinput

echo "🔄 Ejecutando collectstatic..."
python manage.py collectstatic --noinput

# Crear superusuario automáticamente si no existe
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists())" | grep -q True; then
  echo "🛠️ Creando superusuario..."
  python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    "${DJANGO_SUPERUSER_USERNAME}",
    "${DJANGO_SUPERUSER_EMAIL}",
    "${DJANGO_SUPERUSER_PASSWORD}"
)
END
else
  echo "✅ Superusuario ya existe."
fi

echo "🚀 Iniciando Gunicorn..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:8000