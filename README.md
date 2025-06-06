# Proyecto Parcial2_SI2

Este proyecto es una aplicación web que consta de dos partes: un backend desarrollado en Django y un frontend desarrollado en Angular.

## Estructura del Proyecto

```
Parcial2_SI2
├── backend
│   ├── manage.py
│   ├── requirements.txt
│   ├── backend
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── apps
│       └── __init__.py
├── frontend
│   ├── angular.json
│   ├── package.json
│   ├── tsconfig.json
│   ├── src
│   │   ├── main.ts
│   │   ├── app
│   │   │   ├── app.module.ts
│   │   │   └── app.component.ts
│   │   └── environments
│   │       ├── environment.ts
│   │       └── environment.prod.ts
└── README.md
```

## Backend (Django)

El backend está construido con la última versión de Django. Los archivos principales incluyen:

- **manage.py**: Script principal para interactuar con el proyecto Django.
- **requirements.txt**: Lista de dependencias necesarias, incluyendo Django.
- **settings.py**: Configuración del proyecto, incluyendo la base de datos y aplicaciones instaladas.
- **urls.py**: Definición de las rutas de la aplicación.
- **wsgi.py**: Punto de entrada para servidores WSGI.

## Frontend (Angular)

El frontend está desarrollado en Angular. Se recomienda usar Angular Material para componentes UI. Los archivos principales incluyen:

- **angular.json**: Configuración del proyecto Angular.
- **package.json**: Configuración para npm, incluyendo dependencias.
- **tsconfig.json**: Configuración de TypeScript.
- **src/main.ts**: Punto de entrada de la aplicación Angular.
- **src/app/app.module.ts**: Definición del módulo principal de la aplicación.
- **src/app/app.component.ts**: Definición del componente principal.

## Instrucciones de Configuración

### Backend

1. Navega a la carpeta `backend`.
2. Instala las dependencias con:
   ```
   pip install -r requirements.txt
   ```
3. Ejecuta el servidor con:
   ```
   python manage.py runserver
   ```

### Frontend

1. Navega a la carpeta `frontend`.
2. Instala las dependencias con:
   ```
   npm install
   ```
3. Ejecuta la aplicación con:
   ```
   ng serve
   ```

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cambios.

## Licencia

Este proyecto está bajo la Licencia MIT.