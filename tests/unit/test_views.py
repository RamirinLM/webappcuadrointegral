import pytest
from django.urls import reverse
from django.test import Client

@pytest.mark.django_db
class TestVistasPublicas:
    def setup_method(self):
        self.client = Client()
    
    def test_home_page_status(self):
        response = self.client.get(reverse('home'))
        assert response.status_code == 200
    
    def test_admin_login_redirect(self):
        response = self.client.get('/admin/')
        assert response.status_code == 302  # Redirección a login

@pytest.mark.django_db
class TestVistasAutenticadas:
    def test_lista_proyectos_autenticado(self, user_client):
        response = user_client.get(reverse('lista_proyectos'))
        assert response.status_code == 200
        assert 'proyectos' in response.context