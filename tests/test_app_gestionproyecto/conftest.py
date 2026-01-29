"""
Configuración mínima para pytest con Django y Playwright
"""

import pytest
import os
import django
from django.contrib.auth.models import User

# Configurar Django para pytest
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

# ============================================
# FIXTURES DE BASE DE DATOS
# ============================================

@pytest.fixture
def db_access(db):
    """Acceso a base de datos para pruebas"""
    yield


@pytest.fixture
def test_user(db_access):
    """Usuario de prueba"""
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )


# ============================================
# FIXTURES DE PLAYWRIGHT (SIN CONFLICTOS)
# ============================================

@pytest.fixture(scope="function")
def page():
    """Página de Playwright para cada prueba"""
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        # Usar chromium en modo headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()
        page.set_default_timeout(10000)  # 10 segundos
        
        yield page
        
        # Limpiar
        context.close()
        browser.close()


# ============================================
# FIXTURES DE SERVIDOR DJANGO
# ============================================

@pytest.fixture
def live_server_url(live_server):
    """URL del servidor en vivo"""
    return live_server.url


# ============================================
# FIXTURES DE DATOS DE PRUEBA
# ============================================

@pytest.fixture
def setup_test_data(db_access, test_user):
    """Configurar datos de prueba para la aplicación"""
    from gestionproyecto.models import Proyecto, Interesado, ActaConstitucion
    from datetime import date, timedelta
    
    # Crear interesado
    interesado = Interesado.objects.create(
        nombre='Juan',
        apellido='Perez',
        email='juan@example.com',
        rol='Cliente',
        slug='juan-perez'
    )
    
    # Crear acta
    acta = ActaConstitucion.objects.create(
        alcance='Proyecto de prueba E2E',
        objetivos='Probar funcionalidades E2E',
        entregables='Pruebas funcionales',
        justificacion='Validar integración completa',
        usuario=test_user,
        slug='acta-e2e'
    )
    
    # Crear proyecto
    proyecto = Proyecto.objects.create(
        nombre='Proyecto E2E Test',
        descripcion='Proyecto para pruebas end-to-end',
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=30),
        estado=1,
        acta_constitucion=acta,
        slug='proyecto-e2e-test'
    )
    
    proyecto.interesados.add(interesado)
    
    return {
        'user': test_user,
        'interesado': interesado,
        'acta': acta,
        'proyecto': proyecto
    }