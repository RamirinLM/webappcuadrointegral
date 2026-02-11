from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project, Milestone, Activity, Seguimiento, UserProfile
from stakeholders.models import Stakeholder
from resources.models import Resource
from risks.models import Risk
from datetime import date, timedelta


class ProjectIntegrationTest(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user1.userprofile.role = 'gestor_proyectos'
        self.user1.userprofile.save()
        self.user2.userprofile.role = 'tecnico_proyectos'
        self.user2.userprofile.save()

        # Create project
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=10000.00,
            created_by=self.user1
        )

    def test_complete_project_setup(self):
        # Add stakeholders
        stakeholder = Stakeholder.objects.create(
            name='Test Stakeholder',
            email='stakeholder@test.com',
            role='client',
            interest_level='high',
            power_level='high'
        )
        stakeholder.projects.add(self.project)

        # Add resources
        resource = Resource.objects.create(
            project=self.project,
            name='Test Resource',
            type='material',
            quantity=10,
            cost_per_unit=100.00,
            description='Test resource'
        )

        # Add risks
        risk = Risk.objects.create(
            project=self.project,
            description='Test Risk',
            probability='high',
            impact='high',
            mitigation_plan='Test mitigation',
            identified_by='Tester'
        )

        # Add activities
        activity = Activity.objects.create(
            project=self.project,
            name='Test Activity',
            description='Test activity',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            assigned_to=self.user2,
            cost=500.00,
            time_estimate=20
        )

        # Add milestones
        milestone = Milestone.objects.create(
            project=self.project,
            name='Test Milestone',
            description='Test milestone',
            due_date=date.today() + timedelta(days=15)
        )

        # Add seguimiento
        seguimiento = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            perspectiva='financiera',
            indicador='Budget Usage',
            valor_actual=2000.00,
            valor_objetivo=10000.00,
            descripcion='Test seguimiento'
        )

        # Verify relationships
        self.assertIn(stakeholder, self.project.stakeholders.all())
        self.assertEqual(resource.project, self.project)
        self.assertEqual(risk.project, self.project)
        self.assertEqual(activity.project, self.project)
        self.assertEqual(milestone.project, self.project)
        self.assertEqual(seguimiento.proyecto, self.project)

        # Verify calculated fields
        self.assertEqual(resource.total_cost, 1000.00)  # 10 * 100
        self.assertEqual(seguimiento.progreso, 20.00)  # 2000 / 10000 * 100

        # Verify project has all components
        self.assertTrue(self.project.stakeholders.exists())
        self.assertTrue(Resource.objects.filter(project=self.project).exists())
        self.assertTrue(Risk.objects.filter(project=self.project).exists())
        self.assertTrue(Activity.objects.filter(project=self.project).exists())
        self.assertTrue(Milestone.objects.filter(project=self.project).exists())
        self.assertTrue(Seguimiento.objects.filter(proyecto=self.project).exists())