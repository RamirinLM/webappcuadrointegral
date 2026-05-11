from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, timedelta

from projects.models import Project, UserProfile
from projects.permissions import (
    get_user_role,
    is_jefe_departamental,
    is_gestor_proyectos,
    is_tecnico_proyectos,
    can_manage_users,
    get_user_projects,
    can_view_project,
    can_edit_project,
    can_view_project_related,
    can_edit_project_related,
)


def set_user_role(user, role):
    UserProfile.objects.filter(user=user).update(role=role)
    user.userprofile.refresh_from_db()


class TestGetUserRole(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_role', password='pass')

    def test_get_role_with_profile(self):
        set_user_role(self.user, 'jefe_departamental')
        self.assertEqual(get_user_role(self.user), 'jefe_departamental')

    def test_get_role_returns_none_for_unauthenticated(self):
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        factory = RequestFactory()
        request = factory.get('/')
        request.user = AnonymousUser()
        self.assertIsNone(get_user_role(request.user))

    def test_get_role_with_none_user(self):
        self.assertIsNone(get_user_role(None))


class TestIsJefeDepartamental(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_jefe', password='pass')

    def test_is_jefe_departamental_true(self):
        set_user_role(self.user, 'jefe_departamental')
        self.assertTrue(is_jefe_departamental(self.user))

    def test_is_jefe_departamental_false(self):
        set_user_role(self.user, 'gestor_proyectos')
        self.assertFalse(is_jefe_departamental(self.user))

    def test_is_jefe_departamental_without_profile(self):
        self.user.userprofile.delete()
        self.assertFalse(is_jefe_departamental(self.user))


class TestIsGestorProyectos(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_gestor', password='pass')

    def test_is_gestor_proyectos_true(self):
        set_user_role(self.user, 'gestor_proyectos')
        self.assertTrue(is_gestor_proyectos(self.user))

    def test_is_gestor_proyectos_false(self):
        set_user_role(self.user, 'tecnico_proyectos')
        self.assertFalse(is_gestor_proyectos(self.user))


class TestIsTecnicoProyectos(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_tecnico', password='pass')

    def test_is_tecnico_proyectos_true(self):
        set_user_role(self.user, 'tecnico_proyectos')
        self.assertTrue(is_tecnico_proyectos(self.user))

    def test_is_tecnico_proyectos_false(self):
        set_user_role(self.user, 'jefe_departamental')
        self.assertFalse(is_tecnico_proyectos(self.user))


class TestCanManageUsers(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_manage', password='pass')

    def test_can_manage_users_jefe(self):
        set_user_role(self.user, 'jefe_departamental')
        self.assertTrue(can_manage_users(self.user))

    def test_can_manage_users_gestor(self):
        set_user_role(self.user, 'gestor_proyectos')
        self.assertFalse(can_manage_users(self.user))

    def test_can_manage_users_tecnico(self):
        set_user_role(self.user, 'tecnico_proyectos')
        self.assertFalse(can_manage_users(self.user))


class TestGetUserProjects(TestCase):
    def setUp(self):
        self.jefe = User.objects.create_user(username='jefe_proj', password='pass')
        set_user_role(self.jefe, 'jefe_departamental')

        self.gestor = User.objects.create_user(username='gestor_proj', password='pass')
        set_user_role(self.gestor, 'gestor_proyectos')

        self.project1 = Project.objects.create(
            name='Project 1',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.gestor
        )
        self.project2 = Project.objects.create(
            name='Project 2',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.jefe
        )

    def test_jefe_sees_all_projects(self):
        projects = get_user_projects(self.jefe)
        self.assertEqual(projects.count(), 2)

    def test_gestor_sees_own_projects(self):
        projects = get_user_projects(self.gestor)
        self.assertEqual(projects.count(), 1)
        self.assertIn(self.project1, projects)


class TestCanViewProject(TestCase):
    def setUp(self):
        self.jefe = User.objects.create_user(username='jefe_view', password='pass')
        set_user_role(self.jefe, 'jefe_departamental')

        self.gestor = User.objects.create_user(username='gestor_view', password='pass')
        set_user_role(self.gestor, 'gestor_proyectos')

        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.gestor
        )

    def test_jefe_can_view_any_project(self):
        self.assertTrue(can_view_project(self.jefe, self.project))

    def test_owner_can_view_own_project(self):
        self.assertTrue(can_view_project(self.gestor, self.project))

    def test_other_user_cannot_view(self):
        other = User.objects.create_user(username='other_view', password='pass')
        self.assertFalse(can_view_project(other, self.project))


class TestCanEditProject(TestCase):
    def setUp(self):
        self.jefe = User.objects.create_user(username='jefe_edit', password='pass')
        set_user_role(self.jefe, 'jefe_departamental')

        self.gestor = User.objects.create_user(username='gestor_edit', password='pass')
        set_user_role(self.gestor, 'gestor_proyectos')

        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.gestor
        )

    def test_jefe_can_edit_any_project(self):
        self.assertTrue(can_edit_project(self.jefe, self.project))

    def test_owner_can_edit_own_project(self):
        self.assertTrue(can_edit_project(self.gestor, self.project))

    def test_other_user_cannot_edit(self):
        other = User.objects.create_user(username='other_edit', password='pass')
        self.assertFalse(can_edit_project(other, self.project))


class TestCanViewProjectRelated(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_view_rel', password='pass')
        set_user_role(self.user, 'gestor_proyectos')

        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )

    def test_can_view_project_related_delegates_to_can_view(self):
        self.assertTrue(can_view_project_related(self.user, self.project))


class TestCanEditProjectRelated(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser_edit_rel', password='pass')
        set_user_role(self.user, 'gestor_proyectos')

        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )

    def test_can_edit_project_related_delegates_to_can_edit(self):
        self.assertTrue(can_edit_project_related(self.user, self.project))
