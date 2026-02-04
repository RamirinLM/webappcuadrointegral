import pytest
import os
import django
from django.contrib.auth.models import User

# --- SOLUCIÓN: Permitir operaciones async-unsafe ---
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tu_proyecto.settings')
django.setup()

@pytest.fixture(scope="session", autouse=True)
def setup_env():
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

@pytest.fixture
def db_access(db):
    """Acceso a base de datos para pruebas"""
    yield

@pytest.fixture
def test_user(db_access):
    """Usuario de prueba"""
    # Usar get_or_create previene errores si otra prueba no limpió correctamente
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
    return user

# El fixture page está bien, pero asegúrate de usarlo 
# junto con mark.django_db(transaction=True) en tus tests.