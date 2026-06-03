"""E2E tests for standalone Activities CRUD via Playwright.

Covers create and edit operations for activities outside the wizard.
"""
from playwright.sync_api import expect


def test_activity_create(page_with_server, login, seeded_project, unique_suffix):
    """Create a new activity via the standalone form and verify it appears in the list."""
    page = login("gestor_e2e")
    project = seeded_project["project"]
    activity_name = f"Actividad Creada E2E {unique_suffix}"

    page.goto(f"/projects/{project.pk}/activities/create/")
    page.wait_for_selector("#id_name")

    # Fill the form
    page.fill("#id_name", activity_name)
    page.fill("#id_description", "Actividad creada desde test E2E")
    page.fill("#id_start_date", "2026-06-01")
    page.fill("#id_end_date", "2026-06-30")
    page.fill("#id_cost", "5000")
    page.fill("#id_time_estimate", "40")

    # Submit
    page.get_by_role("button", name="Crear actividad").click()

    # Should redirect to activity_list
    page.wait_for_url(f"**/projects/{project.pk}/activities/")
    expect(page.locator("body")).to_contain_text("Actividad creada exitosamente")
    expect(page.locator("body")).to_contain_text(activity_name)


def test_activity_edit(page_with_server, login, seeded_project, unique_suffix):
    """Edit an existing activity and verify changes persist."""
    page = login("gestor_e2e")
    project = seeded_project["project"]
    activity = seeded_project["activity"]
    new_name = f"Actividad Editada E2E {unique_suffix}"

    page.goto(f"/projects/{project.pk}/activities/{activity.pk}/edit/")
    page.wait_for_selector("#id_name")

    # Verify existing value shows the current name
    expect(page.locator("#id_name")).to_have_value(activity.name)

    # Change fields (must fill all required fields explicitly)
    page.fill("#id_name", new_name)
    page.fill("#id_description", "Descripcion actualizada E2E")
    page.fill("#id_start_date", "2026-06-01")
    page.fill("#id_end_date", "2026-06-30")
    page.fill("#id_cost", "2500")

    # Submit
    page.get_by_role("button", name="Guardar cambios").click()

    # After redirect, verify success message and new name on the list page
    expect(page.locator("body")).to_contain_text("Actividad actualizada exitosamente")
    expect(page.locator("body")).to_contain_text(new_name)

    # Old name should no longer appear
    expect(page.locator("body")).not_to_contain_text(activity.name)
