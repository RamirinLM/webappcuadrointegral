from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from risks.models import Risk
from projects.models import Project

class TestRiskViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.login(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_risk_list(self):
        response = self.client.get(reverse('risks:risk_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'risks/risk_list.html')
        self.assertIn('risks', response.context)

    def test_risk_create_get(self):
        response = self.client.get(reverse('risks:risk_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'risks/risk_form.html')
        self.assertIn('form', response.context)

    def test_risk_create_post_valid(self):
        data = {
            'project': self.project.pk,
            'description': 'New Risk Description',
            'probability': 'medium',
            'impact': 'high',
            'status': 'identified',
            'mitigation_plan': 'Mitigation Plan',
            'identified_by': 'Tester'
        }
        response = self.client.post(reverse('risks:risk_create'), data)
        self.assertRedirects(response, reverse('risks:risk_list'))
        self.assertEqual(Risk.objects.count(), 1)

    def test_risk_create_post_invalid(self):
        data = {
            'project': self.project.pk,
            'description': '',
            'probability': 'low',
            'impact': 'low'
        }
        response = self.client.post(reverse('risks:risk_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'risks/risk_form.html')
        self.assertFalse(response.context['form'].is_valid())