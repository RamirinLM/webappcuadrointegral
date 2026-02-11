from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from risks.models import Risk
from projects.models import Project, UserProfile
from datetime import date

class RiskManagementTestCase(TestCase):
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

    def test_risk_creation_success(self):
        response = self.client.post(reverse('risks:risk_create'), {
            'project': self.project.pk,
            'description': 'Test risk description',
            'probability': 'high',
            'impact': 'high',
            'status': 'identified',
            'mitigation_plan': 'Test mitigation plan',
            'identified_by': 'Test User'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Risk.objects.filter(description='Test risk description').exists())

    def test_risk_creation_validation_error(self):
        response = self.client.post(reverse('risks:risk_create'), {
            'project': self.project.pk,
            'description': '',
            'probability': 'high',
            'impact': 'high',
            'status': 'identified',
            'mitigation_plan': '',
            'identified_by': ''
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Risk.objects.filter(project=self.project).exists())

    def test_risk_list_view(self):
        Risk.objects.create(
            project=self.project,
            description='Risk 1',
            probability='medium',
            impact='medium',
            status='identified',
            identified_by='User'
        )
        response = self.client.get(reverse('risks:risk_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Risk 1')