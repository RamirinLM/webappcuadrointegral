import subprocess
import pytest
import time
import requests
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def django_server():
    """Start Django development server for e2e tests."""
    server = subprocess.Popen(["python", "manage.py", "runserver", "8000"])
    # Wait for server to start
    for _ in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000")
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("Django server did not start within 30 seconds")
    yield
    server.terminate()
    server.wait()


@pytest.fixture
def page_with_server(browser, django_server):
    """Provide a Playwright page with Django server running."""
    context = browser.new_context(base_url="http://localhost:8000")
    page = context.new_page()
    page.goto("/")
    yield page
    page.close()
    context.close()