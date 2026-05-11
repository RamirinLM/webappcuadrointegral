import uuid
from datetime import date, timedelta
import os

import pytest
from django.contrib.auth.models import User
from playwright.sync_api import Page

from projects.models import Activity, ChangeRequest, Notification, Project
from stakeholders.models import Stakeholder


os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")


@pytest.fixture
def unique_suffix():
    return uuid.uuid4().hex[:8]


@pytest.fixture
def seeded_roles(transactional_db):
    jefe = User.objects.create_user(
        username="jefe_e2e",
        password="testpass123",
        email="jefe@example.com",
        first_name="Jefe",
        last_name="Departamental",
    )
    jefe.userprofile.role = "jefe_departamental"
    jefe.userprofile.save()

    gestor = User.objects.create_user(
        username="gestor_e2e",
        password="testpass123",
        email="gestor@example.com",
        first_name="Gestor",
        last_name="Proyectos",
    )
    gestor.userprofile.role = "gestor_proyectos"
    gestor.userprofile.save()

    tecnico = User.objects.create_user(
        username="tecnico_e2e",
        password="testpass123",
        email="tecnico@example.com",
        first_name="Tecnico",
        last_name="Proyectos",
    )
    tecnico.userprofile.role = "tecnico_proyectos"
    tecnico.userprofile.save()

    return {"jefe": jefe, "gestor": gestor, "tecnico": tecnico}


@pytest.fixture
def seeded_project(transactional_db, seeded_roles):
    gestor = seeded_roles["gestor"]
    tecnico = seeded_roles["tecnico"]
    project = Project.objects.create(
        name="Proyecto Base E2E",
        description="Proyecto semilla para escenarios E2E",
        start_date=date.today() - timedelta(days=5),
        end_date=date.today() + timedelta(days=45),
        budget=25000,
        created_by=gestor,
    )
    activity = Activity.objects.create(
        project=project,
        name="Actividad Base",
        description="Actividad inicial",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=5),
        assigned_to=tecnico,
        cost=1200,
        time_estimate=24,
    )
    stakeholder = Stakeholder.objects.create(
        name="Stakeholder Base",
        email="stakeholder.base@example.com",
        role="client",
        interest_level="high",
        power_level="high",
    )
    stakeholder.projects.add(project)
    return {"project": project, "activity": activity, "stakeholder": stakeholder}


@pytest.fixture
def seeded_change_request(transactional_db, seeded_roles, seeded_project):
    return ChangeRequest.objects.create(
        project=seeded_project["project"],
        requested_by=seeded_roles["gestor"],
        description="Cambio de alcance E2E",
        justification="Validar flujo de aprobacion",
        impact="Alto",
    )


@pytest.fixture
def seeded_notification(transactional_db, seeded_roles, seeded_project):
    return Notification.objects.create(
        project=seeded_project["project"],
        recipient=seeded_roles["gestor"],
        alert_type="general",
        message="Notificacion E2E pendiente",
    )


@pytest.fixture
def page_with_server(live_server, browser) -> Page:
    context = browser.new_context(base_url=live_server.url)
    page = context.new_page()
    yield page
    page.close()
    context.close()


@pytest.fixture
def login(page_with_server: Page, seeded_roles):
    def _login(username: str, password: str = "testpass123") -> Page:
        page_with_server.goto("/accounts/login/")
        page_with_server.fill("#id_username", username)
        page_with_server.fill("#id_password", password)
        page_with_server.locator('button[type="submit"]').click()
        page_with_server.wait_for_url(lambda url: "/accounts/login/" not in url)
        return page_with_server

    return _login
