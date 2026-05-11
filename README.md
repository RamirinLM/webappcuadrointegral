# webappcuadrointegral

Sistema Django para gestion de proyectos del GAD Celica.

## Requisitos

- Python 3.12+ recomendado
- Entorno virtual
- Dependencias de `requirements.txt`

## Configuracion

1. Crear y activar un entorno virtual.
2. Instalar dependencias con `pip install -r requirements.txt`.
3. Copiar `.env.example` a `.env` y ajustar las variables necesarias.
4. Ejecutar migraciones con `python manage.py migrate`.
5. Iniciar el servidor con `python manage.py runserver`.

## Validacion

- `python -m pytest`
- `python manage.py check`

## Entornos

- Desarrollo: SQLite y email por consola por defecto.
- Produccion: configurar base de datos, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, correo SMTP y cookies seguras por variables de entorno.

