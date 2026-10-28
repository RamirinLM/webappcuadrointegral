"""Middleware for screenshot capture - bypasses authentication ONLY when enabled.

Activate with DJANGO_SCREENSHOT_MODE=true in .env.
When disabled, passes through without interfering with normal auth flow.
"""
import os

from django.contrib.auth import login
from django.contrib.auth.models import User


class ScreenshotAuthBypassMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = os.environ.get("DJANGO_SCREENSHOT_MODE", "").lower() in {"1", "true", "yes", "on"}

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        # Auto-login as admin if not authenticated (screenshot mode only)
        if not request.user.is_authenticated:
            try:
                admin = User.objects.get(username='admin')
                login(request, admin)
            except User.DoesNotExist:
                pass
        return self.get_response(request)
