# Ejecución de Pruebas — Guía para el Equipo de Trabajo

**Proyecto:** CMI GAD Municipal de Celica  
**Propósito:** Instrucciones para ejecutar, interpretar y mantener la suite de pruebas automatizadas.

---

## Índice

1. [Requisitos previos](#1-requisitos-previos)
2. [Estructura de las pruebas](#2-estructura-de-las-pruebas)
3. [Ejecución rápida](#3-ejecución-rápida)
4. [Ejecución por nivel](#4-ejecución-por-nivel)
5. [Ejecución de un archivo específico](#5-ejecución-de-un-archivo-específico)
6. [Ejecución de una prueba individual](#6-ejecución-de-una-prueba-individual)
7. [Pruebas E2E (Playwright)](#7-pruebas-e2e-playwright)
8. [Ver resultados con detalle](#8-ver-resultados-con-detalle)
9. [Depurar pruebas fallidas](#9-depurar-pruebas-fallidas)
10. [Resolver fallos comunes](#10-resolver-fallos-comunes)
11. [Agregar nuevas pruebas](#11-agregar-nuevas-pruebas)
12. [Referencia rápida](#12-referencia-rápida)

---

## 1. Requisitos Previos

### 1.1 Entorno base

```bash
python3 --version   # ≥ 3.10
pip --version       # Última versión
```

### 1.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 1.3 Dependencias específicas de pruebas

```bash
pip install pytest pytest-django pytest-playwright playwright
```

### 1.4 Instalar navegador para pruebas E2E

```bash
python3 -m playwright install chromium-headless-shell
```

Esto descarga Chromium Headless Shell en `~/.cache/ms-playwright/`.

### 1.5 Bibliotecas del sistema (Linux/WSL)

Si ves errores como `libnspr4.so: cannot open shared object file`, las bibliotecas compartidas necesarias están en `/tmp/playwright-libs/`. Se cargan automáticamente con:

```bash
export LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu
```

En sistemas Debian/Ubuntu con sudo se pueden instalar directamente:

```bash
sudo apt install libnspr4 libnss3 libasound2
```

---

## 2. Estructura de las Pruebas

```
tests/
├── e2e/                          # End-to-End (navegador real)
│   ├── conftest.py               # Fixtures: page, login, seeded data
│   ├── test_e2e_activities_crud.py
│   ├── test_e2e_change_requests.py
│   ├── test_e2e_feedback_notifications_reports.py
│   ├── test_e2e_milestones_crud.py
│   ├── test_e2e_project_workflow.py
│   ├── test_e2e_user_management.py
│   ├── test_e2e_wizard_flow.py
│   └── test_e2e_wizard_stakeholders.py
│
├── functional/                   # Funcionales (vistas Django)
│   ├── projects/
│   │   ├── test_evm_view.py
│   │   ├── test_notification_flow.py
│   │   ├── test_project_management.py
│   │   └── test_wizard_create_flow.py
│   ├── reports/
│   │   └── test_reporting.py
│   ├── resources/
│   │   └── test_resource_management.py
│   ├── risks/
│   │   └── test_risk_management.py
│   └── stakeholders/
│       ├── test_feedback_management.py
│       └── test_stakeholder_management.py
│
├── integration/                  # Integración (módulos combinados)
│   ├── test_data_flow.py
│   ├── test_evm_integration.py
│   ├── test_project_integration.py
│   └── test_user_permissions.py
│
└── unit/                         # Unitarias (componentes aislados)
    ├── projects/
    │   ├── test_evm.py
    │   ├── test_models.py
    │   ├── test_permissions.py
    │   ├── test_services.py
    │   ├── test_views.py
    │   └── test_wizard_predecessor.py
    ├── reports/
    │   ├── test_models.py
    │   └── test_views.py
    ├── resources/
    │   ├── test_models.py
    │   └── test_views.py
    ├── risks/
    │   ├── test_models.py
    │   └── test_views.py
    └── stakeholders/
        ├── test_models.py
        └── test_views.py
```

**Niveles de la pirámide:**

| Nivel | Qué prueba | Velocidad | Cantidad |
|-------|-----------|-----------|----------|
| Unitarias | Modelos, servicios, permisos, vistas individuales | ⚡ Rápidas (~3 min) | 122 |
| Funcionales | Flujos de negocio completos en vistas | 🚶 (~1.5 min) | 48 |
| Integración | Interacción entre módulos | 🚶 (~1 min) | 36 |
| E2E | Flujos de usuario en navegador real | 🐢 (~1.5 min) | 14 |

---

## 3. Ejecución Rápida

### Todas las pruebas del proyecto

```bash
python3 -m pytest
```

### Con variable de entorno (necesario en algunas terminales)

```bash
LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu python3 -m pytest
```

### Salida esperada

```
220 passed in 394.73s (0:06:34)
```

---

## 4. Ejecución por Nivel

### Solo pruebas unitarias

```bash
# Rápido, para verificar cambios en modelos/servicios
python3 -m pytest tests/unit/
```

### Solo pruebas funcionales

```bash
# Verifica flujos de negocio completos
python3 -m pytest tests/functional/
```

### Solo pruebas de integración

```bash
# Verifica interacción entre módulos
python3 -m pytest tests/integration/
```

### Solo pruebas E2E

```bash
# Verifica flujos de usuario en navegador (las más importantes)
LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu \
  python3 -m pytest tests/e2e/
```

---

## 5. Ejecución de un Archivo Específico

```bash
# Unitarias de modelos
python3 -m pytest tests/unit/projects/test_models.py

# E2E del wizard completo
LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu \
  python3 -m pytest tests/e2e/test_e2e_wizard_flow.py

# Funcionales de interesados
python3 -m pytest tests/functional/stakeholders/test_stakeholder_management.py
```

---

## 6. Ejecución de una Prueba Individual

Usa `::` para separar el archivo del nombre de la clase/función:

```bash
# Una prueba unitaria específica
python3 -m pytest tests/unit/projects/test_models.py::TestProjectModel::test_project_creation

# Una prueba E2E específica
LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu \
  python3 -m pytest tests/e2e/test_e2e_wizard_flow.py::test_wizard_full_create_flow
```

---

## 7. Pruebas E2E (Playwright)

### 7.1 Configuración del navegador

Las pruebas E2E usan **Chromium Headless Shell** (sin interfaz gráfica). El navegador se instala con:

```bash
python3 -m playwright install chromium-headless-shell
```

### 7.2 Fixtures principales

Definidas en `tests/e2e/conftest.py`:

| Fixture | Qué hace |
|---------|----------|
| `page_with_server` | Abre un navegador conectado al servidor de prueba de Django |
| `login(username)` | Inicia sesión con un usuario y devuelve la página |
| `seeded_roles` | Crea 3 usuarios: jefe, gestor, técnico |
| `seeded_project` | Crea proyecto + actividad + stakeholder asociado |
| `unique_suffix` | Sufijo UUID para nombres únicos |

### 7.3 Usuarios de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `jefe_e2e` | `testpass123` | Jefe Departamental |
| `gestor_e2e` | `testpass123` | Gestor de Proyectos |
| `tecnico_e2e` | `testpass123` | Técnico de Proyectos |

### 7.4 Base de datos de prueba

Las pruebas E2E usan **SQLite en memoria**. Cada ejecución crea y destruye la base de datos, por lo que los datos de fixtures (`seeded_roles`, `seeded_project`, etc.) existen solo durante la prueba.

### 7.5 Tiempo estimado

Cada prueba E2E tarda entre 12 y 20 segundos. Las 14 pruebas completas toman ~1.5 minutos.

---

## 8. Ver Resultados con Detalle

### Resumen compacto

```bash
python3 -m pytest -q
```

### Salida verbose (nombres de prueba)

```bash
python3 -m pytest -v
```

### Traceback completo de fallos

```bash
python3 -m pytest --tb=long
```

### Traceback en una línea (compacto)

```bash
python3 -m pytest --tb=line
```

### Detener en el primer fallo

```bash
python3 -m pytest -x
```

### Sin output de captura (ver prints)

```bash
python3 -m pytest -s
```

### Combinaciones comunes

```bash
# Desarrollo rápido: detener en primer fallo, verbose
python3 -m pytest -x -v

# Debug: verbose, traceback largo, con prints
python3 -m pytest -v --tb=long -s
```

---

## 9. Depurar Pruebas Fallidas

### 9.1 Identificar el tipo de fallo

```
E       AssertionError: Locator expected to contain text '...'
→ El texto esperado no está en la página. Revisar template o vista.

E       django.urls.exceptions.NoReverseMatch: Reverse for '...' not found
→ La URL nombrada no existe o los argumentos son incorrectos.

E       AssertionError: 404 != 200
→ La página devolvió 404. La URL no existe.

E       playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded
→ La página tardó demasiado en cargar. Posible problema de red o base de datos.
```

### 9.2 Para pruebas E2E: capturar pantalla

Agregar esto temporalmente en la prueba para ver el estado de la página:

```python
page.screenshot(path="/tmp/debug_screenshot.png")
```

Luego inspeccionar la imagen:

```bash
open /tmp/debug_screenshot.png   # macOS
# O copiar desde WSL y abrir en Windows
```

### 9.3 Para pruebas E2E: inspeccionar HTML

```python
html = page.content()
with open("/tmp/debug_page.html", "w") as f:
    f.write(html)
```

### 9.4 Ver el texto completo del body

```python
text = page.locator("body").inner_text()
print(text)
```

### 9.5 Probar una URL manualmente

Si una prueba E2E falla al navegar a cierta URL, probala en el navegador real para ver si la página carga correctamente:

```bash
python3 manage.py runserver 0.0.0.0:8000
```

Luego abrir `http://localhost:8000/accounts/login/` y seguir los mismos pasos que la prueba.

---

## 10. Resolver Fallos Comunes

### 10.1 "libnspr4.so: cannot open shared object file"

```bash
export LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu
# Luego ejecutar pytest
```

O instalar las bibliotecas del sistema:

```bash
sudo apt install libnspr4 libnss3 libasound2
```

### 10.2 "NoReverseMatch" en pruebas de vistas

Ocurre cuando una prueba usa `reverse('nombre_url')` sin los argumentos requeridos. Revisar si la URL cambió para requerir parámetros:

```python
# Antes (ruta plana):
reverse('activity_create')

# Después (ruta anidada bajo proyecto):
reverse('activity_create', args=[project.id])
```

### 10.3 Prueba E2E falla por timeout

Aumentar el timeout en la aserción:

```python
expect(page.locator("body")).to_contain_text("texto", timeout=10000)
```

O verificar que la página navegó correctamente:

```python
page.goto("/alguna-url/")
page.wait_for_url("**/alguna-url/")
```

### 10.4 "transactional_db" no funciona

Si creás datos con ORM en una prueba E2E y no aparecen en las vistas, asegurate de que la prueba tenga acceso a `transactional_db`:

```python
# ✅ Correcto: transactional_db como parámetro
def test_algo(page_with_server, transactional_db, ...):
    MiModelo.objects.create(...)

# ❌ Incorrecto: falta transactional_db
def test_algo(page_with_server, ...):
    MiModelo.objects.create(...)  # Esto falla
```

---

## 11. Agregar Nuevas Pruebas

### 11.1 Plantilla para prueba unitaria

```python
import pytest
from django.test import RequestFactory
from projects.models import Project


@pytest.mark.django_db
class TestMiFuncionalidad:
    def test_algo_esperado(self):
        """Descripción clara de lo que verifica."""
        resultado = mi_funcion()
        assert resultado == "valor_esperado"
```

### 11.2 Plantilla para prueba E2E

```python
from playwright.sync_api import expect


def test_mi_flujo_e2e(page_with_server, login, seeded_roles):
    page = login("gestor_e2e")

    page.goto("/alguna-pagina/")
    page.fill("#id_campo", "valor")
    page.get_by_role("button", name="Guardar").click()

    expect(page.locator("body")).to_contain_text("Resultado esperado")
```

Reglas para pruebas E2E:
- Usar `page.wait_for_url("**/patron/**")` después de cada navegación por formulario
- Los pasos del wizard que usan JS (`addStakeholder()`, `addRisk()`, etc.) se ejecutan con `page.evaluate()`
- Para editar actividades/hitos: llenar siempre las fechas explícitamente con `page.fill()`
- La edición de hitos requiere usuario `jefe_e2e` (por el decorador `@jefe_departamental_required`)

### 11.3 Convenir nombres

| Archivo | Contenido |
|---------|-----------|
| `test_e2e_<modulo>.py` | Pruebas E2E de un módulo |
| `test_<modulo>.py` en `tests/functional/` | Pruebas funcionales |
| `test_<modulo>.py` en `tests/integration/` | Pruebas de integración |
| `test_<componente>.py` en `tests/unit/` | Pruebas unitarias |

---

## 12. Referencia Rápida

### Ejecutar todo
```bash
LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu python3 -m pytest
```

### Solo E2E
```bash
LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu python3 -m pytest tests/e2e/
```

### Solo unitarias
```bash
python3 -m pytest tests/unit/
```

### Una prueba específica
```bash
python3 -m pytest tests/e2e/test_e2e_wizard_flow.py::test_wizard_full_create_flow -v
```

### Con variable de entorno persistente
```bash
export LD_LIBRARY_PATH=/tmp/playwright-libs/usr/lib/x86_64-linux-gnu
python3 -m pytest tests/e2e/
```

### Flags útiles

| Flag | Efecto |
|------|--------|
| `-v` | Modo verbose (nombres de prueba) |
| `-q` | Modo silencioso |
| `-x` | Detener en el primer fallo |
| `--tb=long` | Traceback completo |
| `--tb=line` | Traceback en una línea |
| `-k "texto"` | Ejecuta pruebas cuyo nombre contenga "texto" |
| `-s` | Muestra output de print() |

---

*Documento actualizado: 3 de junio de 2026*  
*Equipo de Desarrollo — CMI GAD Municipal de Celica*
