from .permissions import is_jefe_departamental


def app_shell(request):
    user = request.user
    profile = getattr(user, "userprofile", None) if getattr(user, "is_authenticated", False) else None
    role = getattr(profile, "role", "")
    role_label = profile.get_role_display() if profile else ""

    return {
        "app_version": "v2026.2",
        "user_role_code": role,
        "user_role_label": role_label,
        "can_manage_users": is_jefe_departamental(user) if getattr(user, "is_authenticated", False) else False,
    }
