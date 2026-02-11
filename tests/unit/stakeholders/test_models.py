from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from stakeholders.models import Stakeholder
from projects.models import Project

class TestStakeholder(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_stakeholder_creation(self):
        stakeholder = Stakeholder.objects.create(
            name='John Doe',
            email='john@example.com',
            role='client',
            contact_info='Phone: 123',
            interest_level='high',
            power_level='high'
        )
        self.assertEqual(stakeholder.name, 'John Doe')
        self.assertEqual(str(stakeholder), 'John Doe')
        self.assertEqual(stakeholder.role, 'client')

    def test_stakeholder_relationships(self):
        stakeholder = Stakeholder.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            role='manager'
        )
        stakeholder.projects.add(self.project)
        self.assertIn(self.project, stakeholder.projects.all())
        self.assertIn(stakeholder, self.project.stakeholders.all())