from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, UserProfile, Activity
from datetime import date

class ReportingTestCase(TestCase):
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

    def test_report_list_view(self):
        response = self.client.get(reverse('reports:report_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reportes')  # Assuming template has this

    def test_gantt_chart_view(self):
        # Create some activities for the project
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Test activity',
            start_date=date(2023, 1, 1),
            end_date=date(2023, 1, 31),
            status='pending'
        )
        response = self.client.get(reverse('reports:gantt_chart', args=[self.project.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gantt')  # Assuming template has this