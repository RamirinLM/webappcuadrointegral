from playwright.sync_api import expect


def test_login_and_role_navigation(page_with_server, login):
    page = login("jefe_e2e")
    expect(page.locator("body")).to_contain_text("Tablero de control")
    expect(page.locator("body")).to_contain_text("Usuarios")
    expect(page.locator("body")).to_contain_text("Notificaciones")


def test_gestor_cannot_access_user_administration(page_with_server, login):
    page = login("gestor_e2e")
    page.goto("/users/")
    page.wait_for_url("**/")
    expect(page.locator("body")).to_contain_text("Acceso denegado")
