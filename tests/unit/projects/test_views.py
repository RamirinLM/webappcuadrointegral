from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.utils import OperationalError
from unittest.mock import patch
from datetime import date
from projects.models import Project, Activity, Milestone, UserProfile, Seguimiento

class TestProjectViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.user.userprofile.role = 'tecnico_proyectos'
        self.user.userprofile.save()
        self.client.login(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_dashboard(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/dashboard.html')
        self.assertIn('projects', response.context)

    def test_project_list(self):
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_list.html')
        self.assertIn('projects', response.context)

    def test_project_detail(self):
        response = self.client.get(reverse('project_detail', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_detail.html')
        self.assertEqual(response.context['project'], self.project)

    def test_project_create_get(self):
        response = self.client.get(reverse('project_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')
        self.assertIn('form', response.context)

    def test_project_create_post_valid(self):
        data = {
            'name': 'New Project',
            'description': 'New Desc',
            'start_date': date.today().isoformat(),
            'end_date': date.today().isoformat(),
            'status': 'planning',
            'budget': '1000.00',
            # ActaConstitucionForm fields
            'alcance': 'Project scope',
            'entregables': 'Deliverables',
            'justificacion': 'Justification',
            'objetivos': 'Objectives'
        }
        response = self.client.post(reverse('project_create'), data)
        self.assertRedirects(response, reverse('project_detail', args=[Project.objects.last().pk]))
        self.assertEqual(Project.objects.count(), 2)

    def test_project_create_post_invalid(self):
        data = {
            'name': '',
            'description': 'Desc',
            'start_date': date.today().isoformat(),
            'end_date': date.today().isoformat(),
        }
        response = self.client.post(reverse('project_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_project_edit_get(self):
        response = self.client.get(reverse('project_edit', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_form.html')

    def test_project_edit_post_valid(self):
        data = {
            'name': 'Updated Project',
            'description': 'Updated Desc',
            'start_date': date.today().isoformat(),
            'end_date': date.today().isoformat(),
            'status': 'in_progress',
            'budget': '2000.00'
        }
        response = self.client.post(reverse('project_edit', args=[self.project.pk]), data)
        self.assertRedirects(response, reverse('project_detail', args=[self.project.pk]))
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, 'Updated Project')

    def test_project_delete_get(self):
        response = self.client.get(reverse('project_delete', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/project_confirm_delete.html')

    def test_project_delete_post(self):
        response = self.client.post(reverse('project_delete', args=[self.project.pk]))
        self.assertRedirects(response, reverse('project_list'))
        self.assertEqual(Project.objects.count(), 0)

    def test_health_check(self):
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'status': 'ok'})

class TestActivityViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.safe_client = Client(raise_request_exception=False)
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.user.userprofile.role = 'tecnico_proyectos'
        self.user.userprofile.save()
        self.client.login(username='testuser', password='pass')
        self.safe_client.login(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_activity_list(self):
        response = self.client.get(reverse('activity_list', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/activity_list.html')

    def test_activity_create_post_valid(self):
        data = {
            'project': self.project.pk,
            'name': 'New Activity',
            'description': 'Desc',
            'start_date': date.today().isoformat(),
            'end_date': date.today().isoformat(),
            'status': 'pending',
            'cost': '100.00',
            'time_estimate': 5
        }
        response = self.client.post(reverse('activity_create', args=[self.project.pk]), data)
        self.assertRedirects(response, reverse('activity_list', args=[self.project.pk]))
        self.assertEqual(Activity.objects.count(), 1)

    def test_notification_schema_mismatch_is_handled_gracefully(self):
        with patch("projects.views.Notification.objects.filter", side_effect=OperationalError("no such column: projects_notification.recipient_id")):
            response = self.safe_client.get(reverse("notification_list"))

        self.assertEqual(response.status_code, 503)
        self.assertContains(response, "base de datos no esta sincronizada", status_code=503)

class TestMilestoneViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.user.userprofile.role = 'tecnico_proyectos'
        self.user.userprofile.save()
        self.client.login(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_milestone_list(self):
        response = self.client.get(reverse('milestone_list', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/milestone_list.html')

    def test_milestone_create_post_valid(self):
        data = {
            'project': self.project.pk,
            'name': 'New Milestone',
            'description': 'Desc',
            'due_date': date.today().isoformat(),
            'phase': 'execution',
            'is_phase_gate': False,
            'completed': False
        }
        response = self.client.post(reverse('milestone_create', args=[self.project.pk]), data)
        self.assertRedirects(response, reverse('milestone_list', args=[self.project.pk]))
        self.assertEqual(Milestone.objects.count(), 1)

class TestUserViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='jefe', password='pass')
        self.user.userprofile.role = 'jefe_departamental'
        self.user.userprofile.save()
        self.client.login(username='jefe', password='pass')

    def test_user_list(self):
        response = self.client.get(reverse('user_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/user_list.html')

    def test_user_create_post_valid(self):
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password': 'pass123',
            'role': 'tecnico_proyectos',
            'is_active': True
        }
        response = self.client.post(reverse('user_create'), data)
        self.assertRedirects(response, reverse('user_list'))
        self.assertEqual(User.objects.count(), 2)

class TestSeguimientoViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.user.userprofile.role = 'tecnico_proyectos'
        self.user.userprofile.save()
        self.client.login(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_seguimiento_list(self):
        response = self.client.get(reverse('seguimiento_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'projects/seguimiento_list.html')

    def test_seguimiento_create_post_valid(self):
        data = {
            'proyecto': self.project.pk,
            'fecha': date.today().isoformat(),
            'observacion': 'Test observation'
        }
        response = self.client.post(reverse('seguimiento_create', args=[self.project.pk]), data)
        self.assertRedirects(response, reverse('project_detail', args=[self.project.pk]))
        self.assertEqual(Seguimiento.objects.count(), 1)
