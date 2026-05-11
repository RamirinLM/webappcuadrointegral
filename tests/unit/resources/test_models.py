from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from resources.models import Resource
from projects.models import Project, Activity

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
        self.activity = Activity.objects.create(
            project=self.project,
            name='Test Activity',
            description='Activity desc',
            start_date=date.today(),
            end_date=date.today(),
            status='pending'
        )

    def test_resource_creation_and_save(self):
        resource = Resource.objects.create(
            activity=self.activity,
            name='Test Resource',
            type='human',
            quantity=2,
            cost_per_unit=50.00,
            description='Desc'
        )
        self.assertEqual(resource.total_cost, 100.00)  # 2 * 50
        self.assertEqual(str(resource), 'Test Resource - Test Activity')

    def test_resource_relationship(self):
        resource = Resource.objects.create(
            activity=self.activity,
            name='Material Resource',
            type='material',
            quantity=10,
            cost_per_unit=20.00
        )
        self.assertEqual(resource.activity, self.activity)