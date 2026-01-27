import pytest
from django.contrib.auth.models import User
from django.test import Client
from gestionproyecto.models import Proyecto

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )

@pytest.fixture
def user_client(user):
    client = Client()
    client.login(username='testuser', password='testpass123')
    return client

@pytest.fixture
def proyecto():
    return Proyecto.objects.create(
        nombre="Proyecto Fixture",
        descripcion="Proyecto para pruebas"
    )