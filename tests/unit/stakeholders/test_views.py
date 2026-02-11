from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from stakeholders.models import Stakeholder

class TestStakeholderViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.client.login(username='testuser', password='pass')
        self.stakeholder = Stakeholder.objects.create(
            name='Test Stakeholder',
            email='test@example.com',
            role='client'
        )

    def test_stakeholder_list(self):
        response = self.client.get(reverse('stakeholders:stakeholder_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stakeholders/stakeholder_list.html')
        self.assertIn('stakeholders', response.context)

    def test_stakeholder_create_get(self):
        response = self.client.get(reverse('stakeholders:stakeholder_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stakeholders/stakeholder_form.html')
        self.assertIn('form', response.context)

    def test_stakeholder_create_post_valid(self):
        data = {
            'name': 'New Stakeholder',
            'email': 'new@example.com',
            'role': 'manager',
            'contact_info': 'Info',
            'interest_level': 'high',
            'power_level': 'high'
        }
        response = self.client.post(reverse('stakeholders:stakeholder_create'), data)
        self.assertRedirects(response, reverse('stakeholders:stakeholder_list'))
        self.assertEqual(Stakeholder.objects.count(), 2)

    def test_stakeholder_create_post_invalid(self):
        data = {
            'name': '',
            'email': 'invalid',
            'role': 'manager'
        }
        response = self.client.post(reverse('stakeholders:stakeholder_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stakeholders/stakeholder_form.html')
        self.assertFalse(response.context['form'].is_valid())

    def test_stakeholder_edit_get(self):
        response = self.client.get(reverse('stakeholders:stakeholder_edit', args=[self.stakeholder.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stakeholders/stakeholder_form.html')

    def test_stakeholder_edit_post_valid(self):
        data = {
            'name': 'Updated Stakeholder',
            'email': 'updated@example.com',
            'role': 'sponsor',
            'contact_info': 'Updated Info',
            'interest_level': 'medium',
            'power_level': 'medium',
            'projects': []
        }
        response = self.client.post(reverse('stakeholders:stakeholder_edit', args=[self.stakeholder.pk]), data)
        self.assertRedirects(response, reverse('stakeholders:stakeholder_list'))
        self.stakeholder.refresh_from_db()
        self.assertEqual(self.stakeholder.name, 'Updated Stakeholder')