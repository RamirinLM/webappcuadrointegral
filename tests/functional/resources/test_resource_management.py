from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from resources.models import Resource
from projects.models import Project, UserProfile
from datetime import date

class ResourceManagementTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        self.user_profile = self.user.userprofile
        self.client.login(username='testuser', password='testpass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            created_by=self.user
        )

    def test_resource_creation_success(self):
        response = self.client.post(reverse('resources:resource_create'), {
            'project': self.project.pk,
            'name': 'Test Resource',
            'type': 'human',
            'quantity': 5,
            'cost_per_unit': '100.00',
            'description': 'Human resource for testing'
        })
        self.assertEqual(response.status_code, 302)
        resource = Resource.objects.get(name='Test Resource')
        self.assertEqual(resource.total_cost, 500.00)

    def test_resource_creation_validation_error(self):
        response = self.client.post(reverse('resources:resource_create'), {
            'project': self.project.pk,
            'name': '',
            'type': 'human',
            'quantity': -1,
            'cost_per_unit': '-100.00',
            'description': 'Invalid resource'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Resource.objects.filter(description='Invalid resource').exists())

    def test_resource_list_view(self):
        Resource.objects.create(
            project=self.project,
            name='Resource 1',
            type='material',
            quantity=10,
            cost_per_unit=50.00
        )
        response = self.client.get(reverse('resources:resource_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resource 1')