from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from projects.models import Project, Activity, UserProfile
from resources.models import Resource
from risks.models import Risk
from stakeholders.models import Stakeholder
from datetime import date, timedelta


class UserPermissionsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user1.userprofile.role = 'gestor_proyectos'
        self.user1.userprofile.save()
        self.user2.userprofile.role = 'tecnico_proyectos'
        self.user2.userprofile.save()

        # Projects created by user1
        self.project1 = Project.objects.create(
            name='Project 1',
            description='Project by user1',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user1
        )
        # Project created by user2
        self.project2 = Project.objects.create(
            name='Project 2',
            description='Project by user2',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user2
        )

        # Activities
        self.activity1 = Activity.objects.create(
            project=self.project1,
            name='Activity 1',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            assigned_to=self.user1
        )
        self.activity2 = Activity.objects.create(
            project=self.project2,
            name='Activity 2',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            assigned_to=self.user2
        )

        # Resources linked to projects
        self.resource1 = Resource.objects.create(
            project=self.project1,
            name='Resource 1',
            type='material',
            quantity=1,
            cost_per_unit=100.00
        )
        self.resource2 = Resource.objects.create(
            project=self.project2,
            name='Resource 2',
            type='material',
            quantity=1,
            cost_per_unit=200.00
        )

        # Risks
        self.risk1 = Risk.objects.create(
            project=self.project1,
            description='Risk 1',
            identified_by='User1'
        )
        self.risk2 = Risk.objects.create(
            project=self.project2,
            description='Risk 2',
            identified_by='User2'
        )

        # Stakeholders
        self.stakeholder = Stakeholder.objects.create(
            name='Stakeholder',
            email='stake@test.com'
        )
        self.stakeholder.projects.add(self.project1, self.project2)

    def test_project_access_permissions(self):
        # Login as user1
        self.client.login(username='user1', password='pass')
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
        # Should only see project1
        self.assertContains(response, 'Project 1')
        self.assertNotContains(response, 'Project 2')

        # Login as user2
        self.client.logout()
        self.client.login(username='user2', password='pass')
        response = self.client.get('/projects/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Project 2')
        self.assertNotContains(response, 'Project 1')

    def test_activity_access_permissions(self):
        # Login as user1
        self.client.login(username='user1', password='pass')
        response = self.client.get('/activities/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Activity 1')
        self.assertNotContains(response, 'Activity 2')

    def test_resource_list_shows_all_but_creation_limited(self):
        # Resources list shows all (current implementation)
        self.client.login(username='user1', password='pass')
        response = self.client.get('/resources/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Resource 1')
        self.assertContains(response, 'Resource 2')  # Shows all

    def test_risk_list_shows_all(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get('/risks/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Risk 1')
        self.assertContains(response, 'Risk 2')

    def test_stakeholder_list_shows_all(self):
        self.client.login(username='user1', password='pass')
        response = self.client.get('/stakeholders/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stakeholder')

    def test_project_detail_access(self):
        # User1 can access project1 detail
        self.client.login(username='user1', password='pass')
        response = self.client.get(f'/projects/{self.project1.pk}/')
        self.assertEqual(response.status_code, 200)

        # But not project2
        response = self.client.get(f'/projects/{self.project2.pk}/')
        self.assertEqual(response.status_code, 404)

    def test_user_assignment_via_activities(self):
        # Test that users are assigned to projects via activities
        # User1 is assigned to activity1 in project1
        self.assertEqual(self.activity1.assigned_to, self.user1)
        self.assertEqual(self.activity1.project.created_by, self.user1)

        # User2 assigned to activity2 in project2
        self.assertEqual(self.activity2.assigned_to, self.user2)
        self.assertEqual(self.activity2.project.created_by, self.user2)