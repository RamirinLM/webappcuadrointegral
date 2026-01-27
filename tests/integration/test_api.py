import pytest
import json
from django.urls import reverse

@pytest.mark.django_db
class TestAPIEndpoints:
    def test_api_proyectos_list(self, user_client, proyecto):
        response = user_client.get('/api/proyectos/')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data) >= 1
    
    def test_api_seguimiento_create(self, user_client, proyecto):
        response = user_client.post('/api/seguimiento/', {
            'proyecto_id': proyecto.id,
            'avance': 75,
            'comentarios': 'Test API'
        })
        assert response.status_code == 201