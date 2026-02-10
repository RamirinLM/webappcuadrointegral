from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


def get_perfil(user):
    """Obtiene el perfil del usuario; si no existe, crea uno consultor."""
    if not user or not user.is_authenticated:
        return None
    from gestionproyecto.models import PerfilUsuario
    perfil = getattr(user, 'perfil', None)
    if perfil is None:
        perfil, _ = PerfilUsuario.objects.get_or_create(user=user, defaults={'rol': 'consultor'})
    return perfil


def user_puede_editar(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superuser', False):
        return True
    perfil = get_perfil(user)
    return perfil and perfil.puede_editar


def user_puede_eliminar(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(user, 'is_superuser', False):
        return True
    perfil = get_perfil(user)
    return perfil and perfil.puede_eliminar


class RequireAuthMixin(LoginRequiredMixin):
    login_url = reverse_lazy('login')


class RequireEditarMixin(RequireAuthMixin):
    """Solo gestor y admin pueden crear/editar."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not user_puede_editar(request.user):
            raise PermissionDenied('No tiene permiso para realizar esta acción.')
        return super().dispatch(request, *args, **kwargs)


class RequireEliminarMixin(RequireAuthMixin):
    """Solo admin puede eliminar."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not user_puede_eliminar(request.user):
            raise PermissionDenied('Solo un administrador puede eliminar.')
        return super().dispatch(request, *args, **kwargs)
