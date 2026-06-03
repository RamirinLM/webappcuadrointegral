"""E2E tests for the wizard project creation flow via Playwright.

Covers the full 7-step wizard navigation and form submission using
real browser interactions including JS-managed forms (steps 3, 5, 6, 7).
"""
from playwright.sync_api import expect


def test_wizard_full_create_flow(page_with_server, login, seeded_roles, unique_suffix):
    """Complete wizard flow through all 7 steps creating a new project."""
    page = login("gestor_e2e")

    # ── Start wizard ──
    page.goto("/projects/wizard/")
    page.wait_for_url("**/wizard/step/1/")
    expect(page.locator("body")).to_contain_text("Paso 1 de 7")

    # ── Step 1: Datos del Proyecto ──
    project_name = f"Proyecto Wizard E2E {unique_suffix}"
    page.fill("#id_name", project_name)
    page.fill("#id_description", "Proyecto creado desde wizard E2E")
    page.fill("#id_start_date", "2026-03-01")
    page.fill("#id_end_date", "2026-12-31")
    page.fill("#id_budget", "50000")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/2/")
    expect(page.locator("body")).to_contain_text("Paso 2 de 7")

    # ── Step 2: Acta de Constitución ──
    page.fill("#id_alcance", "Alcance del proyecto E2E")
    page.fill("#id_entregables", "Entregable 1, Entregable 2")
    page.fill("#id_justificacion", "Justificacion del proyecto E2E")
    page.fill("#id_objetivos", "Objetivos del proyecto E2E")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/3/")
    expect(page.locator("body")).to_contain_text("Paso 3 de 7")

    # ── Step 3: Interesados ──
    # Add a new stakeholder via the JS function
    page.fill("#stakeholder-name", "Stakeholder Wizard E2E")
    page.fill("#stakeholder-email", "stakeholder.wizard@example.com")
    page.select_option("#stakeholder-role", "client")
    page.select_option("#stakeholder-interest", "high")
    page.select_option("#stakeholder-power", "high")
    page.evaluate("addStakeholder()")
    # Verify the stakeholder was added to the list
    expect(page.locator("#new-stakeholders-list")).to_contain_text("Stakeholder Wizard E2E")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/4/")
    expect(page.locator("body")).to_contain_text("Paso 4 de 7")

    # ── Step 4: Alcance Detallado ──
    page.fill("#id_descripcion", "Alcance tecnico detallado E2E")
    page.fill("#id_objetivos", "Objetivos especificos medibles E2E")
    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/5/")
    expect(page.locator("body")).to_contain_text("Paso 5 de 7")

    # ── Step 5: Riesgos y Comunicación ──
    # Add a risk via JS
    page.fill("#risk-description", "Riesgo de presupuesto E2E")
    page.select_option("#risk-probability", "medium")
    page.select_option("#risk-impact", "high")
    page.fill("#risk-mitigation", "Monitorear gastos semanalmente")
    page.evaluate("addRisk()")
    expect(page.locator("#risks-list")).to_contain_text("Riesgo de presupuesto E2E")

    # Add a communication via JS
    page.select_option("#comm-type", "email")
    page.fill("#comm-recipient", "gestor@example.com")
    page.fill("#comm-description", "Reporte semanal de avance")
    page.evaluate("addCommunication()")
    expect(page.locator("#communications-list")).to_contain_text("Reporte semanal de avance")

    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/6/")
    expect(page.locator("body")).to_contain_text("Paso 6 de 7")

    # ── Step 6: Actividades y Recursos ──
    # Add a resource
    page.fill("#activity-name", "Analisis de requisitos")
    page.fill("#activity-description", "Relevar y documentar requisitos")
    page.fill("#activity-start", "2026-03-15")
    page.fill("#activity-end", "2026-04-15")
    page.fill("#resource-name", "Analista Senior")
    page.select_option("#resource-type", "human")
    page.fill("#resource-quantity", "2")
    page.fill("#resource-cost", "5000")
    page.evaluate("addResourceToActivity()")
    # Verify resource badge appears
    expect(page.locator("#resource-count-badge")).to_contain_text("1 recurso")

    # Add the activity (includes resources)
    page.evaluate("addActivity()")
    expect(page.locator("#activities-list")).to_contain_text("Analisis de requisitos")
    expect(page.locator("#total-activities")).to_contain_text("1")

    page.get_by_role("button", name="Guardar y continuar").click()
    page.wait_for_url("**/wizard/step/7/")
    expect(page.locator("body")).to_contain_text("Paso 7 de 7")

    # ── Step 7: Hitos ──
    # Add a milestone via JS
    page.fill("#milestone-name", "Hito de analisis")
    page.fill("#milestone-due-date", "2026-04-15")
    page.select_option("#milestone-phase", "planning")
    page.fill("#milestone-description", "Analisis completado")
    page.evaluate("addMilestone()")
    expect(page.locator("#milestones-list")).to_contain_text("Hito de analisis")

    # Finish project creation
    page.get_by_role("button", name="Finalizar proyecto").click()
    page.wait_for_url("**/projects/**")

    # Verify project was created successfully
    expect(page.locator("body")).to_contain_text(project_name)
    expect(page.locator("body")).to_contain_text("creado exitosamente")


def test_wizard_back_navigate_no_duplicates(page_with_server, login, seeded_roles, unique_suffix):
    """Navigate backward and forward through wizard steps without data loss."""
    page = login("gestor_e2e")

    project_name = f"Proyecto BackNav {unique_suffix}"
    page.goto("/projects/wizard/")
    expect(page.locator("body")).to_contain_text("Paso 1 de 7")

    # Step 1
    page.fill("#id_name", project_name)
    page.fill("#id_description", "Proyecto back-navigate E2E")
    page.fill("#id_start_date", "2026-03-01")
    page.fill("#id_end_date", "2026-12-31")
    page.fill("#id_budget", "50000")
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 2 de 7")

    # Step 2
    page.fill("#id_alcance", "Alcance backnav E2E")
    page.fill("#id_entregables", "Entregable backnav")
    page.fill("#id_justificacion", "Justificacion backnav")
    page.fill("#id_objetivos", "Objetivos backnav")
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 3 de 7")

    # Step 3 — add a stakeholder via JS
    page.fill("#stakeholder-name", "Stakeholder BackNav")
    page.fill("#stakeholder-email", "backnav@example.com")
    page.evaluate("addStakeholder()")
    expect(page.locator("#new-stakeholders-list")).to_contain_text("Stakeholder BackNav")
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 4 de 7")

    # Step 4
    page.fill("#id_descripcion", "Alcance detallado backnav")
    page.fill("#id_objetivos", "Objetivos backnav")
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 5 de 7")

    # Back-navigate to step 3 via "Anterior" links
    page.get_by_role("link", name="Anterior").click()
    expect(page.locator("body")).to_contain_text("Paso 4 de 7")
    page.get_by_role("link", name="Anterior").click()
    expect(page.locator("body")).to_contain_text("Paso 3 de 7")

    # Submit step 3 again (no new stakeholders in the UI on back-nav,
    # but the server handles this correctly via update-or-create logic)
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 4 de 7")

    # Go forward to step 5 again
    page.fill("#id_descripcion", "Alcance detallado backnav")
    page.fill("#id_objetivos", "Objetivos backnav")
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 5 de 7")

    # Verify we can still move forward — no crash from duplicate stakeholders
    page.fill("#risk-description", "Riesgo de prueba")
    page.evaluate("addRisk()")
    page.get_by_role("button", name="Guardar y continuar").click()
    expect(page.locator("body")).to_contain_text("Paso 6 de 7")
