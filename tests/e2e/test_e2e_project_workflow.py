import pytest
from playwright.sync_api import Page


def test_complete_project_workflow(page_with_server: Page):
    """Test complete project management workflow from login to reports."""
    page = page_with_server

    # Login
    page.goto("/accounts/login/")
    page.fill("#id_username", "testuser")
    page.fill("#id_password", "testpass")
    page.click("button[type='submit']")

    # Wait for redirect to dashboard
    page.wait_for_url("**/")

    # Create project
    page.goto("/projects/create/")
    page.fill("#id_name", "Test Project")
    page.fill("#id_description", "A test project for e2e testing")
    page.fill("#id_start_date", "2024-01-01")
    page.fill("#id_end_date", "2024-12-31")
    page.select_option("#id_status", "planning")  # Assuming choices
    page.fill("#id_budget", "10000")
    page.click("button[type='submit']")

    # Wait for redirect to project list or detail
    page.wait_for_url("**/projects/**")

    # Get project id from url
    project_url = page.url
    project_id = project_url.split("/")[-2]  # Assuming /projects/<id>/

    # Add activity
    page.goto("/activities/create/")
    page.select_option("#id_project", project_id)
    page.fill("#id_name", "Test Activity")
    page.fill("#id_description", "A test activity")
    page.fill("#id_start_date", "2024-01-01")
    page.fill("#id_end_date", "2024-01-15")
    page.select_option("#id_status", "pending")
    # assigned_to select user
    page.select_option("#id_assigned_to", "1")  # Assume user id 1
    page.fill("#id_cost", "1000")
    page.fill("#id_time_estimate", "10")
    page.click("button[type='submit']")

    # Add stakeholder
    page.goto("/stakeholders/create/")
    page.fill("#id_name", "Test Stakeholder")
    page.fill("#id_email", "stakeholder@test.com")
    page.select_option("#id_role", "client")
    page.fill("#id_contact_info", "Phone: 123456")
    page.select_option("#id_interest_level", "high")
    page.select_option("#id_power_level", "high")
    page.click("button[type='submit']")

    # Add resource
    page.goto("/resources/create/")
    page.select_option("#id_project", project_id)
    page.fill("#id_name", "Test Resource")
    page.fill("#id_description", "A test resource")
    page.select_option("#id_type", "human")
    page.fill("#id_quantity", "1")
    page.fill("#id_cost_per_unit", "500")
    page.select_option("#id_projects", project_id)
    page.click("button[type='submit']")

    # Add risk
    page.goto("/risks/create/")
    page.select_option("#id_project", project_id)
    page.fill("#id_description", "A test risk")
    page.select_option("#id_probability", "medium")
    page.select_option("#id_impact", "high")
    page.select_option("#id_status", "identified")
    page.fill("#id_identified_by", "Test User")
    page.click("button[type='submit']")

    # View reports
    page.goto("/reports/")
    # Assume there's a link to gantt for the project
    page.click(f"a[href*='gantt/{project_id}']")

    # Verify gantt page
    assert "Gantt" in page.content()

    # Verify report list
    page.goto("/reports/")
    assert "Reportes" in page.content()