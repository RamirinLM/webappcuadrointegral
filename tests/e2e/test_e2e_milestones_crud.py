"""E2E tests for standalone Milestones CRUD via Playwright.

Covers create and edit operations for milestones outside the wizard.
"""
from playwright.sync_api import expect


def test_milestone_create(page_with_server, login, seeded_project, unique_suffix):
    """Create a new milestone via the standalone form and verify it appears in the list."""
    page = login("jefe_e2e")
    project = seeded_project["project"]
    milestone_name = f"Hito Creado E2E {unique_suffix}"

    page.goto(f"/projects/{project.pk}/milestones/create/")
    page.wait_for_selector("#id_name")

    # Fill the form
    page.fill("#id_name", milestone_name)
    page.fill("#id_description", "Hito creado desde test E2E")
    page.fill("#id_due_date", "2026-06-15")
    page.select_option("#id_phase", "planning")
    page.check("#id_is_phase_gate")

    # Submit
    page.get_by_role("button", name="Guardar hito").click()

    # Should redirect to milestone_list
    page.wait_for_url(f"**/projects/{project.pk}/milestones/")
    expect(page.locator("body")).to_contain_text("Hito creado exitosamente")
    expect(page.locator("body")).to_contain_text(milestone_name)


def test_milestone_edit(page_with_server, login, seeded_project, seeded_roles, unique_suffix):
    """Edit an existing milestone and verify changes persist.
    
    NOTE: milestone_edit view requires @jefe_departamental_required.
    """
    from projects.models import Milestone
    from datetime import date, timedelta

    page = login("jefe_e2e")
    project = seeded_project["project"]

    # Create a milestone via ORM so we have one to edit
    milestone = Milestone.objects.create(
        project=project,
        name=f"Hito Original E2E {unique_suffix}",
        description="Hito creado para edicion",
        due_date=date.today() + timedelta(days=10),
        phase="execution",
        is_phase_gate=False,
    )

    # Navigate directly to edit URL
    page.goto(f"/projects/{project.pk}/milestones/{milestone.pk}/edit/")
    page.wait_for_selector("#id_name")

    # Verify existing value
    expect(page.locator("#id_name")).to_have_value(milestone.name)

    # Change fields (must fill all required fields explicitly)
    new_name = f"Hito Editado E2E {unique_suffix}"
    page.fill("#id_name", new_name)
    page.fill("#id_due_date", "2026-06-20")
    page.select_option("#id_phase", "closure")
    page.check("#id_completed")

    # Submit
    page.get_by_role("button", name="Guardar hito").click()

    # After redirect, verify success message and new name on the list page
    expect(page.locator("body")).to_contain_text("Hito actualizado exitosamente")
    expect(page.locator("body")).to_contain_text(new_name)
    expect(page.locator("body")).not_to_contain_text(milestone.name)
