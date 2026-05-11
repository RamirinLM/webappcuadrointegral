from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, Activity, Milestone, Seguimiento, UserProfile
from datetime import date

class ProjectManagementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        self.user_profile = self.user.userprofile
        self.client.login(username='testuser', password='testpass')

    def test_project_creation_success(self):
        # Project creation requires both ProjectForm and ActaConstitucionForm
        response = self.client.post(reverse('project_create'), {
            # ProjectForm fields
            'name': 'Test Project',
            'description': 'A test project',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'status': 'planning',
            'budget': '10000.00',
            # ActaConstitucionForm fields
            'alcance': 'Project scope definition',
            'entregables': 'Deliverables list',
            'justificacion': 'Project justification',
            'objetivos': 'Project objectives'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(Project.objects.filter(name='Test Project').exists())

    def test_project_creation_validation_error(self):
        response = self.client.post(reverse('project_create'), {
            'name': '',
            'description': 'A test project',
            'start_date': '2023-01-01',
            'end_date': '2022-12-31',  # End before start
            'status': 'planning',
            'budget': '10000.00'
        })
        self.assertEqual(response.status_code, 200)  # Form re-rendered with errors
        self.assertFalse(Project.objects.filter(description='A test project').exists())

    def test_project_edit(self):
        project = Project.objects.create(
            name='Original Name',
            description='Original desc',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            status='planning',
            budget=5000.00,
            created_by=self.user
        )
        response = self.client.post(reverse('project_edit', args=[project.pk]), {
            'name': 'Edited Name',
            'description': 'Edited desc',
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'status': 'in_progress',
            'budget': '15000.00'
        })
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.name, 'Edited Name')
        self.assertEqual(project.status, 'modified')  # Status set to modified for approval

    def test_activity_creation(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            created_by=self.user
        )
        response = self.client.post(reverse('activity_create'), {
            'project': project.pk,
            'name': 'Test Activity',
            'description': 'Activity desc',
            'start_date': '2023-01-01',
            'end_date': '2023-01-31',
            'status': 'pending',
            'cost': '1000.00',
            'time_estimate': 40
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Activity.objects.filter(name='Test Activity').exists())

    def test_milestone_creation(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            created_by=self.user
        )
        response = self.client.post(reverse('milestone_create'), {
            'project': project.pk,
            'name': 'Test Milestone',
            'description': 'Milestone desc',
            'due_date': '2023-06-01',
            'phase': 'execution',
            'is_phase_gate': False,
            'completed': False
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Milestone.objects.filter(name='Test Milestone').exists())

    def test_user_creation(self):
        # User creation requires jefe_departamental role
        # Update the user to have jefe_departamental role
        self.user.userprofile.role = 'jefe_departamental'
        self.user.userprofile.save()
        # Re-login with updated permissions
        self.client.login(username='testuser', password='testpass')
        
        response = self.client.post(reverse('user_create'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'new@example.com',
            'password': 'newpass123',
            'role': 'tecnico_proyectos',
            'is_active': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_seguimiento_creation(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            created_by=self.user
        )
        response = self.client.post(reverse('seguimiento_create', args=[project.pk]), {
            'proyecto': project.pk,
            'fecha': '2023-01-15',
            'observacion': 'Test seguimiento observation'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Seguimiento.objects.filter(observacion='Test seguimiento observation').exists())

    def test_project_delete(self):
        project = Project.objects.create(
            name='To Delete',
            description='Test',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            created_by=self.user
        )
        response = self.client.post(reverse('project_delete', args=[project.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(name='To Delete').exists())