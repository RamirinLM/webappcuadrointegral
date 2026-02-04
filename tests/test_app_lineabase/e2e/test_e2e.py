import pytest
from playwright.sync_api import expect

@pytest.mark.django_db(transaction=True)
def test_visualizacion_cronograma(page, live_server, setup_test_data):
    cronograma = setup_test_data["cronograma"]
    
    # Usamos la URL del live_server definida en el conftest principal
    page.goto(f"{live_server.url}/lineabase/cronograma/{cronograma.slug}/")
    
    # Verificamos que el contenido cargue
    expect(page.locator("body")).to_contain_text(cronograma.proyecto.nombre)