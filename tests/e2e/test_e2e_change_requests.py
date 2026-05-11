from playwright.sync_api import expect


def test_change_request_approval_flow(page_with_server, login, seeded_change_request):
    page = login("jefe_e2e")
    page.goto("/change-requests/")
    expect(page.locator("body")).to_contain_text("Cambio de alcance E2E")
    page.get_by_role("link", name="Aprobar").first.click()
    expect(page.locator("body")).to_contain_text("Cambio aprobado")
    expect(page.locator("body")).to_contain_text("Aprobado")


def test_change_request_creation_by_gestor(page_with_server, login, seeded_project):
    page = login("gestor_e2e")
    page.goto("/change-requests/create/")
    page.select_option("#id_project", str(seeded_project["project"].pk))
    page.fill("#id_description", "Nueva solicitud E2E")
    page.fill("#id_justification", "Justificacion desde E2E")
    page.fill("#id_impact", "Impacto medio")
    page.get_by_role("button", name="Guardar Solicitud").click()
    expect(page.locator("body")).to_contain_text("Solicitud de cambio creada exitosamente")
    expect(page.locator("body")).to_contain_text("Nueva solicitud E2E")
