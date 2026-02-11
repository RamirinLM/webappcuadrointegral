from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from resources.models import Resource
from projects.models import Project

class TestResource(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_resource_creation_and_save(self):
        resource = Resource.objects.create(
            project=self.project,
            name='Test Resource',
            type='human',
            quantity=2,
            cost_per_unit=50.00,
            description='Desc'
        )
        self.assertEqual(resource.total_cost, 100.00)  # 2 * 50
        self.assertEqual(str(resource), 'Test Resource - Test Project')

    def test_resource_relationship(self):
        resource = Resource.objects.create(
            project=self.project,
            name='Material Resource',
            type='material',
            quantity=10,
            cost_per_unit=20.00
        )
        self.assertEqual(resource.project, self.project)