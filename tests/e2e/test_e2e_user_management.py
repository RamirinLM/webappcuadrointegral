import pytest
from playwright.sync_api import Page


def test_user_registration_login_and_access(page_with_server: Page):
    """Test user registration (via user create), login, and access to different modules."""
    page = page_with_server

    # Login as admin (assume admin user exists)
    page.goto("/accounts/login/")
    page.fill("#id_username", "admin")
    page.fill("#id_password", "admin")
    page.click("button[type='submit']")

    # Wait for redirect
    page.wait_for_url("**/")

    # Create a new user
    page.goto("/users/create/")
    page.fill("#id_username", "newuser")
    page.fill("#id_first_name", "New")
    page.fill("#id_last_name", "User")
    page.fill("#id_email", "newuser@test.com")
    page.fill("#id_password", "newpass123")
    page.select_option("#id_role", "tecnico_proyectos")
    page.click("button[type='submit']")

    # Logout
    page.goto("/accounts/logout/")

    # Login as new user
    page.goto("/accounts/login/")
    page.fill("#id_username", "newuser")
    page.fill("#id_password", "newpass123")
    page.click("button[type='submit']")

    # Wait for redirect
    page.wait_for_url("**/")

    # Access stakeholders module
    page.goto("/stakeholders/")
    assert "Interesados" in page.content()

    # Access resources module
    page.goto("/resources/")
    assert "Recursos" in page.content()

    # Access risks module
    page.goto("/risks/")
    assert "Riesgos" in page.content()

    # Access reports module
    page.goto("/reports/")
    assert "Reportes" in page.content()

    # Access projects
    page.goto("/")
    assert "Tablero" in page.content()