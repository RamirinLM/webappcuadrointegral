from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from stakeholders.models import Stakeholder
from projects.models import Project, UserProfile
from datetime import date

class StakeholderManagementTestCase(TestCase):
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

    def test_stakeholder_creation_success(self):
        response = self.client.post(reverse('stakeholders:stakeholder_create'), {
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'client',
            'contact_info': 'Phone: 123-456',
            'interest_level': 'high',
            'power_level': 'high',
            'projects': [self.project.pk]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Stakeholder.objects.filter(name='John Doe').exists())

    def test_stakeholder_creation_validation_error(self):
        response = self.client.post(reverse('stakeholders:stakeholder_create'), {
            'name': '',
            'email': 'invalid-email',
            'role': 'client',
            'contact_info': '',
            'interest_level': 'high',
            'power_level': 'high',
            'projects': [self.project.pk]
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Stakeholder.objects.filter(email='invalid-email').exists())

    def test_stakeholder_edit(self):
        stakeholder = Stakeholder.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            role='sponsor',
            interest_level='medium',
            power_level='medium'
        )
        stakeholder.projects.add(self.project)
        response = self.client.post(reverse('stakeholders:stakeholder_edit', args=[stakeholder.pk]), {
            'name': 'Jane Smith',
            'email': 'jane@example.com',
            'role': 'manager',
            'contact_info': 'Updated contact',
            'interest_level': 'high',
            'power_level': 'low',
            'projects': [self.project.pk]
        })
        self.assertEqual(response.status_code, 302)
        stakeholder.refresh_from_db()
        self.assertEqual(stakeholder.name, 'Jane Smith')
        self.assertEqual(stakeholder.role, 'manager')

    def test_stakeholder_list_view(self):
        Stakeholder.objects.create(
            name='Stakeholder 1',
            email='s1@example.com',
            role='client'
        )
        response = self.client.get(reverse('stakeholders:stakeholder_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stakeholder 1')