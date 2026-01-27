from playwright.sync_api import sync_playwright
import pytest

@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True para CI
        yield browser
        browser.close()

def test_login_admin(browser):
    page = browser.new_page()
    
    try:
        page.goto("http://localhost:8000/admin/login/")
        page.fill("#id_username", "ramir")
        page.fill("#id_password", "Tesis2026")
        page.click("input[type='submit']")
        
        # Verificar login exitoso
        assert "Site administration" in page.inner_text("body")
        print("✓ Login exitoso")
        
    finally:
        page.close()

if __name__ == "__main__":
    # Ejecutar prueba directamente
    with sync_playwright() as p:
        test_login_admin(p.chromium.launch(headless=False))