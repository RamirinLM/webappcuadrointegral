from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from projects.models import Project, Activity

class TestReportViews(TestCase):
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
        self.activity = Activity.objects.create(
            project=self.project,
            name='Test Activity',
            description='Desc',
            start_date=date.today(),
            end_date=date.today()
        )

    def test_report_list(self):
        response = self.client.get(reverse('reports:report_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/report_list.html')
        self.assertIn('projects', response.context)
        self.assertIn(self.project, response.context['projects'])

    def test_gantt_chart(self):
        response = self.client.get(reverse('reports:gantt_chart', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reports/gantt.html')
        self.assertEqual(response.context['project'], self.project)
        self.assertIn(self.activity, response.context['activities'])