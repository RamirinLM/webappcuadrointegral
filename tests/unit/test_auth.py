import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestAutenticacion:
    def test_login_exitoso(self, client):
        User.objects.create_user('usuario', 'pass123')
        response = client.post(reverse('login'), {
            'username': 'usuario',
            'password': 'pass123'
        })
        assert response.status_code == 302
        assert response.url == reverse('home')
    
    def test_login_fallido(self, client):
        response = client.post(reverse('login'), {
            'username': 'inexistente',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        assert 'error' in response.context
    
    def test_logout(self, user_client):
        response = user_client.get(reverse('logout'))
        assert response.status_code == 302
        assert response.url == reverse('home')