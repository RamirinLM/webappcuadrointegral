import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestSeguimientoIntegration:
    def test_seguimiento_list_view(self, client, setup_test_data):
        """Prueba la vista de lista de seguimientos."""
        url = reverse('index') # URL de la app seguimiento
        response = client.get(url)
        
        assert response.status_code == 200
        assert 'seguimiento_list' in response.context
        #assert setup_test_data["proyecto"].nombre in response.content.decode()

    def test_seguimiento_detail_context(self, client, setup_test_data):
        """Verifica que el detalle del seguimiento contenga los índices calculados."""
        seguimiento = setup_test_data["proyecto"].seguimiento_set.first()
        url = reverse('seguimiento_view', kwargs={'slug': seguimiento.slug})
        
        response = client.get(url)
        
        assert response.status_code == 200
        # Verificamos acceso a propiedades del modelo desde la vista
        assert 'object' in response.context
        assert response.context['object'].proyecto.nombre == "Proyecto E2E Test"