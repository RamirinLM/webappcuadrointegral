from playwright.sync_api import expect


def test_feedback_notification_and_report_filtering(page_with_server, login, seeded_project, seeded_notification):
    page = login("gestor_e2e")

    page.goto("/stakeholders/feedback/create/")
    page.select_option("#id_stakeholder", str(seeded_project["stakeholder"].pk))
    page.select_option("#id_project", str(seeded_project["project"].pk))
    page.select_option("#id_rating", "5")
    page.fill("#id_comments", "Retroalimentacion registrada por E2E")
    page.get_by_role("button", name="Guardar").click()
    expect(page.locator("body")).to_contain_text("Retroalimentación registrada exitosamente")
    expect(page.locator("body")).to_contain_text("Retroalimentacion de Interesados")

    page.goto("/notifications/")
    expect(page.locator("body")).to_contain_text("Notificacion E2E pendiente")
    page.locator(".list-group-item").first.click()
    expect(page.locator("body")).to_contain_text("Estado: Leida")

    page.goto("/reports/")
    page.fill('input[name="owner_id"]', str(seeded_project["project"].created_by_id))
    page.get_by_role("button", name="Filtrar").click()
    expect(page.locator("body")).to_contain_text("Proyecto Base E2E")
