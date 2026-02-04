import pytest
from playwright.sync_api import Page, expect

@pytest.mark.django_db(transaction=True)
def test_user_checks_project_health(page: Page, live_server, setup_test_data):
    """El usuario navega desde el índice hasta el informe de seguimiento."""
    # 1. Acceder al listado de seguimientos
    page.goto(f"{live_server.url}/seguimiento/index")
    # 2. Seleccionar el seguimiento del proyecto
    proyecto_nombre = "Proyecto E2E Test"
    page.click(f"text={proyecto_nombre}")