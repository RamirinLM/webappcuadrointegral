from playwright.sync_api import expect


def test_project_lifecycle_from_creation_to_reports(page_with_server, login, unique_suffix):
    page = login("gestor_e2e")

    project_name = f"Proyecto E2E {unique_suffix}"
    page.goto("/projects/create/")
    page.fill("#id_name", project_name)
    page.fill("#id_description", "Proyecto creado desde Playwright")
    page.fill("#id_start_date", "2026-03-01")
    page.fill("#id_end_date", "2026-12-31")
    page.select_option("#id_status", "planning")
    page.fill("#id_budget", "15000")
    page.fill("#id_alcance", "Alcance E2E")
    page.fill("#id_entregables", "Entregables E2E")
    page.fill("#id_justificacion", "Justificacion E2E")
    page.fill("#id_objetivos", "Objetivos E2E")
    page.get_by_role("button", name="Guardar").click()

    expect(page.locator("body")).to_contain_text(project_name)
    expect(page.locator("body")).to_contain_text("Acta de Constitución")

    page.goto("/projects/")
    expect(page.locator("body")).to_contain_text(project_name)

    page.goto("/reports/")
    page.fill('input[name="project_status"]', "planning")
    page.get_by_role("button", name="Filtrar").click()
    expect(page.locator("body")).to_contain_text(project_name)


def test_project_role_visibility(page_with_server, login, seeded_project):
    page = login("tecnico_e2e")
    page.goto(f"/projects/{seeded_project['project'].pk}/")
    page.wait_for_url("**/projects/")
    expect(page.locator("body")).to_contain_text("No tienes permisos")
