"""
URL configuration for cmi_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(_request):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('health/', health_check, name='health_check'),
    path('', include('projects.urls')),
    path('stakeholders/', include('stakeholders.urls', namespace='stakeholders')),
    path('resources/', include('resources.urls', namespace='resources')),
    path('risks/', include('risks.urls', namespace='risks')),
    path('reports/', include('reports.urls', namespace='reports')),
]

handler403 = "cmi_project.error_views.handler403"
handler404 = "cmi_project.error_views.handler404"
handler500 = "cmi_project.error_views.handler500"

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
