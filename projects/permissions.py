from __future__ import annotations

from django.contrib.auth.models import User

from .models import Project


ROLE_JEFE = "jefe_departamental"
ROLE_GESTOR = "gestor_proyectos"
ROLE_TECNICO = "tecnico_proyectos"


def get_user_role(user: User) -> str | None:
    if not user or not getattr(user, "is_authenticated", False):
        return None
    profile = getattr(user, "userprofile", None)
    return getattr(profile, "role", None)


def is_jefe_departamental(user: User) -> bool:
    return get_user_role(user) == ROLE_JEFE


def is_gestor_proyectos(user: User) -> bool:
    return get_user_role(user) == ROLE_GESTOR


def is_tecnico_proyectos(user: User) -> bool:
    return get_user_role(user) == ROLE_TECNICO


def can_manage_users(user: User) -> bool:
    return is_jefe_departamental(user)


def get_user_projects(user: User):
    if is_jefe_departamental(user):
        return Project.objects.all()
    return Project.objects.filter(created_by=user)


def can_view_project(user: User, project: Project) -> bool:
    return is_jefe_departamental(user) or project.created_by_id == user.id


def can_edit_project(user: User, project: Project) -> bool:
    return can_view_project(user, project)


def can_view_project_related(user: User, project: Project) -> bool:
    return can_view_project(user, project)


def can_edit_project_related(user: User, project: Project) -> bool:
    return can_edit_project(user, project)

