from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from risks.models import Risk
from projects.models import Project

class TestRisk(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_risk_creation(self):
        risk = Risk.objects.create(
            project=self.project,
            description='Test Risk Description',
            probability='high',
            impact='medium',
            status='identified',
            mitigation_plan='Plan',
            identified_by='Tester'
        )
        self.assertEqual(risk.description, 'Test Risk Description')
        self.assertEqual(str(risk), 'Riesgo: Test Risk Description - Test Project')
        self.assertEqual(risk.status, 'identified')
        self.assertIsNotNone(risk.identified_date)

    def test_risk_relationship(self):
        risk = Risk.objects.create(
            project=self.project,
            description='Another Risk',
            probability='low',
            impact='low'
        )
        self.assertEqual(risk.project, self.project)