from .mixins import get_perfil, user_puede_editar, user_puede_eliminar


def perfil_usuario(request):
    """Expone perfil y permisos en todas las plantillas."""
    if not request.user.is_authenticated:
        return {
            'perfil_usuario': None,
            'user_puede_editar': False,
            'user_puede_eliminar': False,
        }
    return {
        'perfil_usuario': get_perfil(request.user),
        'user_puede_editar': user_puede_editar(request.user),
        'user_puede_eliminar': user_puede_eliminar(request.user),
    }
