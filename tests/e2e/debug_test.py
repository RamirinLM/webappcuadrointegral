"""Debug test to see form submission behavior."""
from playwright.sync_api import expect


def test_debug_activity_create(page_with_server, login, seeded_project, unique_suffix):
    page = login("gestor_e2e")
    project = seeded_project["project"]
    activity_name = f"Actividad Debug {unique_suffix}"

    page.goto(f"/projects/{project.pk}/activities/create/")
    page.wait_for_selector("#id_name")

    # Debug: check project options
    options = page.locator("#id_project option")
    count = options.count()
    print(f"\n[DEBUG] Project options ({count}):")
    for i in range(count):
        opt = options.nth(i)
        print(f"  value='{opt.get_attribute('value')}' text='{opt.text_content()}'")

    page.fill("#id_name", activity_name)
    page.fill("#id_description", "Actividad debug")
    page.fill("#id_start_date", "2026-06-01")
    page.fill("#id_end_date", "2026-06-30")
    page.fill("#id_cost", "5000")
    page.fill("#id_time_estimate", "40")

    # Check assigned_to options too
    assigned = page.locator("#id_assigned_to option")
    ac = assigned.count()
    print(f"[DEBUG] Assigned_to options ({ac}):")
    for i in range(ac):
        opt = assigned.nth(i)
        print(f"  value='{opt.get_attribute('value')}' text='{opt.text_content()}'")

    page.select_option("#id_project", str(project.pk))
    print(f"[DEBUG] Selected project {project.pk}")

    # Check form HTML briefly
    form_html = page.locator("#activity-form").inner_html()
    print(f"[DEBUG] Form action: {page.locator('#activity-form').get_attribute('action')}")
    print(f"[DEBUG] CSRF present: {'csrfmiddlewaretoken' in form_html}")

    page.get_by_role("button", name="Crear actividad").click()
    page.wait_for_timeout(3000)

    url = page.url
    print(f"[DEBUG] URL after submit: {url}")

    alerts = page.locator(".alert")
    for i in range(alerts.count()):
        a = alerts.nth(i)
        print(f"[DEBUG] Alert [{a.get_attribute('class')}]: {a.text_content()}")

    error_items = page.locator(".errorlist, .text-danger, .invalid-feedback")
    for i in range(error_items.count()):
        print(f"[DEBUG] Error: {error_items.nth(i).text_content()}")

    page.screenshot(path="/tmp/debug_create_screenshot.png")
    print("[DEBUG] Screenshot saved!")

    # The real assertions
    page.wait_for_url(f"**/projects/{project.pk}/activities/")
    expect(page.locator("body")).to_contain_text("Actividad creada exitosamente")
    expect(page.locator("body")).to_contain_text(activity_name)
