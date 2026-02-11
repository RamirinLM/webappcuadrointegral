from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from resources.models import Resource
from projects.models import Project

class TestResourceViews(TestCase):
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

    def test_resource_list(self):
        response = self.client.get(reverse('resources:resource_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resource_list.html')
        self.assertIn('resources', response.context)

    def test_resource_create_get(self):
        response = self.client.get(reverse('resources:resource_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resource_form.html')
        self.assertIn('form', response.context)

    def test_resource_create_post_valid(self):
        data = {
            'project': self.project.pk,
            'name': 'New Resource',
            'type': 'equipment',
            'quantity': 5,
            'cost_per_unit': '100.00',
            'description': 'Test Desc'
        }
        response = self.client.post(reverse('resources:resource_create'), data)
        self.assertRedirects(response, reverse('resources:resource_list'))
        self.assertEqual(Resource.objects.count(), 1)
        resource = Resource.objects.first()
        self.assertEqual(resource.total_cost, 500.00)

    def test_resource_create_post_invalid(self):
        data = {
            'project': self.project.pk,
            'name': '',
            'type': 'human',
            'quantity': 0,
            'cost_per_unit': '0'
        }
        response = self.client.post(reverse('resources:resource_create'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resources/resource_form.html')
        self.assertFalse(response.context['form'].is_valid())