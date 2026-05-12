# WebApp Cuadro Integral — GAD Celica

Sistema Django para administración y seguimiento de proyectos del GAD Celica.

## Stack

| Componente | Tecnología |
|-----------|-----------|
| Backend | Django 5.2+ |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Templates | Django Templates + django-widget-tweaks |
| Tests | pytest + pytest-django + Playwright (E2E) |
| Auth | django.contrib.auth |

---

## Requisitos previos

- **Python 3.12+**
- **Git**
- **Node.js 18+** (solo para Playwright — tests E2E)
- Opcional: **GitHub Desktop** interfaz gráfica

---

## Setup paso a paso

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd webappcuadrointegral
```

### 2. Crear y activar entorno virtual

**Linux / WSL:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si vas a correr tests E2E (Playwright), además necesitas los navegadores:

```bash
playwright install chromium
```

### 4. Configurar variables de entorno

Crea el archivo `.env` en la raíz del proyecto:

```bash
cp .env.example .env
```

Las variables disponibles son:

| Variable | Obligatoria | Default | Descripción |
|----------|-------------|---------|-------------|
| `DJANGO_SECRET_KEY` | **SÍ** | — | Clave secreta de Django (generar una única) |
| `DJANGO_DEBUG` | No | `False` | Modo debug (`True` para desarrollo) |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1,testserver` | Hosts permitidos, separados por coma |
| `DJANGO_DB_ENGINE` | No | `django.db.backends.sqlite3` | Motor de BD |
| `DJANGO_DB_NAME` | No | `db.sqlite3` | Nombre BD o ruta archivo |
| `DJANGO_DB_USER` | No | — | Usuario BD |
| `DJANGO_DB_PASSWORD` | No | — | Contraseña BD |
| `DJANGO_DB_HOST` | No | — | Host BD |
| `DJANGO_DB_PORT` | No | — | Puerto BD |
| `DJANGO_LANGUAGE_CODE` | No | `es-ec` | Idioma |
| `DJANGO_TIME_ZONE` | No | `America/Guayaquil` | Zona horaria |
| `DJANGO_EMAIL_BACKEND` | No | `console` | Backend de correo (`console` imprime en terminal) |
| `DJANGO_EMAIL_HOST` / `PORT` / `USER` / `PASSWORD` / `USE_TLS` | No | — | Config SMTP |
| `DJANGO_DEFAULT_FROM_EMAIL` | No | `no-reply@celica.local` | Remitente por defecto |
| `DJANGO_SECURE_COOKIES` | No | `True` | Cookies seguras (poner `False` en desarrollo sin HTTPS) |
| `DJANGO_LOG_LEVEL` | No | `INFO` | Nivel de logging |

**Mínimo indispensable para desarrollo:**

```env
DJANGO_SECRET_KEY=clave-segura-aqui-cambiame-en-produccion
DJANGO_DEBUG=True
DJANGO_SECURE_COOKIES=False
```

> 💡 Para generar una `SECRET_KEY` con: `python -c "import secrets; print(secrets.token_urlsafe(50))"`

### 5. Ejecutar migraciones

```bash
python manage.py migrate
```

### 6. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 7. (Opcional) Cargar datos de prueba

```bash
python manage.py populate_test_data
```

Esto crea:
- 2 proyectos (uno en ejecución con datos EVM reales, otro en planificación)
- Actividades, hitos, recursos, riesgos, interesados
- 3 usuarios con roles distintos para probar permisos

### 8. Iniciar servidor de desarrollo

```bash
python manage.py runserver
```

Abrí http://localhost:8000 en el navegador.

---

## Comandos útiles

```bash
# Crear superusuario
python manage.py createsuperuser

# Ver rutas disponibles
python manage.py show_urls

# Validar configuración
python manage.py check --deploy

# Live reload (con django-watchfiles)
python manage.py runserver_plus  # si instalás django-extensions
```

---

## Tests

```bash
# Todos los tests
python -m pytest

# Solo unitarios
python -m pytest tests/unit/

# Solo funcionales
python -m pytest tests/functional/

# Solo integración
python -m pytest tests/integration/

# Solo E2E (requiere Playwright)
python -m pytest tests/e2e/ --headed  # con navegador visible

# Con cobertura
python -m pytest --cov=projects --cov=reports --cov=resources --cov=risks --cov=stakeholders
```

---

## Estructura del proyecto

```
webappcuadrointegral/
├── cmi_project/           # Config Django (settings, urls, wsgi)
├── projects/              # App principal: proyectos, actividades, seguimiento
│   ├── management/commands/  # Comandos personalizados
│   ├── migrations/
│   └── templates/projects/
├── reports/               # Reportes, calendario, Gantt
│   └── templates/reports/
├── resources/             # Recursos asignados a actividades
│   └── templates/resources/
├── risks/                 # Gestión de riesgos
│   └── templates/risks/
├── stakeholders/          # Interesados y feedback
│   └── templates/stakeholders/
├── templates/             # Templates base y shared
│   ├── registration/      # Login
│   └── errors/            # Páginas de error (403, 404, 500)
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── tests/                 # Suite de tests
│   ├── unit/
│   ├── functional/
│   ├── integration/
│   └── e2e/
├── .env.example           # Template de variables de entorno
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## URLs principales

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard del proyecto |
| `/admin/` | Admin Django |
| `/accounts/login/` | Login |
| `/projects/` | CRUD de proyectos |
| `/projects/<id>/linea-base/` | Línea Base y Seguimiento (EVM) |
| `/reports/` | Reportes y gráficos |
| `/risks/` | Gestión de riesgos |
| `/resources/` | Gestión de recursos |
| `/stakeholders/` | Gestión de interesados |
| `/health/` | Health check |

---

## Producción

Para desplegar en producción:

1. Usar PostgreSQL en vez de SQLite
2. Generar `DJANGO_SECRET_KEY` segura y única
3. `DJANGO_DEBUG=False`
4. Configurar `DJANGO_ALLOWED_HOSTS` con los dominios reales
5. Configurar un servidor SMTP real (no `console`)
6. `DJANGO_SECURE_COOKIES=True`
7. Usar `gunicorn` o `uwsgi` como servidor WSGI
8. Configurar nginx o Caddy para servir estáticos y proxy reverso
