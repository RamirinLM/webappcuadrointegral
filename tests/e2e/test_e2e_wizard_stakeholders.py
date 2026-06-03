"""E2E test: existing stakeholder selection in wizard step 3.

Verifies that pre-existing stakeholders appear as checkboxes on step 3
and can be selected/assigned to the new project during the wizard flow.
"""
from datetime import date, timedelta

from playwright.sync_api import expect

from projects.models import Project
from stakeholders.models import Stakeholder


def test_wizard_step3_existing_stakeholders(
    page_with_server, login, seeded_roles, unique_suffix, transactional_db
):
    """Create stakeholders beforehand, then verify they appear and can be
    selected on wizard step 3."""
    page = login("gestor_e2e")
    gestor = seeded_roles["gestor"]

    # ── Seed project so stakeholders appear in the wizard query ──
    # The wizard view filters by Stakeholder.objects.filter(
    #   projects__in=get_user_projects(request.user)).distinct()
    seed_project = Project.objects.create(
        name="Seed Stakeholders",
        description="Temporary seed project",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=30),
        budget=1000,
        created_by=gestor,
    )

    # Create stakeholders and associate them with the seed project
    s1 = Stakeholder.objects.create(
        name="Stakeholder Existente A",
        email="existente.a@example.com",
        role="client",
        interest_level="high",
        power_level="high",
    )
    s1.projects.add(seed_project)

    s2 = Stakeholder.objects.create(
        name="Stakeholder Existente B",
        email="existente.b@example.com",
        role="sponsor",
        interest_level="medium",
        power_level="high",
    )
    s2.projects.add(seed_project)

    # ── Step 1: Datos del Proyecto ──
    project_name = f"Proyecto Stakeholder E2E {unique_suffix}"
    page.goto("/projects/wizard/")
    page.wait_for_url("**/wizard/step/1/")
    expect(page.locator("body")).to_contain_text("Paso 1 de 7")
    page.fill("#id_name", project_name)
    page.fill("#id_description", "Proyecto para probar stakeholders existentes")
    page.fill("#id_start_date", "2026-03-01")
    page.fill("#id_end_date", "2026-12-31")
    page.fill("#id_budget", "30000")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/2/")

    # ── Step 2: Acta de Constitución ──
    page.fill("#id_alcance", "Alcance E2E stakeholders")
    page.fill("#id_entregables", "Entregable E2E stakeholders")
    page.fill("#id_justificacion", "Justificacion E2E stakeholders")
    page.fill("#id_objetivos", "Objetivos E2E stakeholders")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/3/")
    expect(page.locator("body")).to_contain_text("Paso 3 de 7")

    # ── Step 3: Interesados ──
    # Verify both existing stakeholders appear on the page
    expect(page.locator("body")).to_contain_text("Stakeholder Existente A")
    expect(page.locator("body")).to_contain_text("Stakeholder Existente B")

    # Verify the checkboxes exist for both stakeholders
    checkbox_a = page.locator(f'input.stakeholder-checkbox[value="{s1.pk}"]')
    checkbox_b = page.locator(f'input.stakeholder-checkbox[value="{s2.pk}"]')
    expect(checkbox_a).to_be_visible()
    expect(checkbox_b).to_be_visible()

    # Initially both should be unchecked
    expect(checkbox_a).not_to_be_checked()
    expect(checkbox_b).not_to_be_checked()

    # Select stakeholder A, leave B unselected
    checkbox_a.check()
    expect(checkbox_a).to_be_checked()
    expect(checkbox_b).not_to_be_checked()

    # Also add a new stakeholder via JS (combined scenario)
    page.fill("#stakeholder-name", "Stakeholder Nuevo C")
    page.fill("#stakeholder-email", "nuevo.c@example.com")
    page.select_option("#stakeholder-role", "team_member")
    page.select_option("#stakeholder-interest", "high")
    page.select_option("#stakeholder-power", "medium")
    page.evaluate("addStakeholder()")
    expect(page.locator("#new-stakeholders-list")).to_contain_text("Stakeholder Nuevo C")

    # Submit step 3
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/4/")
    expect(page.locator("body")).to_contain_text("Paso 4 de 7")

    # ── Quick steps 4-7 to finish the project ──
    page.fill("#id_descripcion", "Alcance detallado stakeholders E2E")
    page.fill("#id_objetivos", "Objetivos stakeholders E2E")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/5/")

    page.fill("#risk-description", "Riesgo stakeholders E2E")
    page.select_option("#risk-probability", "medium")
    page.select_option("#risk-impact", "high")
    page.fill("#risk-mitigation", "Mitigacion E2E")
    page.evaluate("addRisk()")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/6/")

    page.fill("#activity-name", "Actividad stakeholders")
    page.fill("#activity-description", "Descripcion actividad stakeholders")
    page.fill("#activity-start", "2026-04-01")
    page.fill("#activity-end", "2026-05-01")
    page.fill("#resource-name", "Recurso E2E")
    page.select_option("#resource-type", "human")
    page.fill("#resource-quantity", "1")
    page.fill("#resource-cost", "2000")
    page.evaluate("addResourceToActivity()")
    page.evaluate("addActivity()")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/7/")

    page.fill("#milestone-name", "Hito stakeholders")
    page.fill("#milestone-due-date", "2026-05-15")
    page.select_option("#milestone-phase", "planning")
    page.fill("#milestone-description", "Descripcion hito")
    page.evaluate("addMilestone()")

    # Finish
    page.get_by_role("button", name="Finalizar proyecto").click()
    page.wait_for_url("**/projects/**")

    # Verify project created
    expect(page.locator("body")).to_contain_text(project_name)
    expect(page.locator("body")).to_contain_text("creado exitosamente")

    # Verify the selected stakeholder (A) is associated with the project
    expect(page.locator("body")).to_contain_text("Stakeholder Existente A")
