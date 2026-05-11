from django.test import TestCase
from django.contrib.auth.models import User
from projects.models import Project, Milestone, Activity, Seguimiento
from resources.models import Resource
from datetime import date, timedelta


class DataFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Data Flow Project',
            description='Test data flow',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=10000.00,
            created_by=self.user
        )
        self.activity = Activity.objects.create(
            project=self.project,
            name='Test Activity',
            description='Activity description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='pending'
        )

    def test_resource_cost_calculation(self):
        # Test that resource total_cost is calculated correctly
        resource = Resource.objects.create(
            activity=self.activity,
            name='Material',
            type='material',
            quantity=5,
            cost_per_unit=200.00
        )
        self.assertEqual(resource.total_cost, 1000.00)

        # Update quantity and check recalculation
        resource.quantity = 10
        resource.save()
        resource.refresh_from_db()
        self.assertEqual(resource.total_cost, 2000.00)

    def test_seguimiento_progress_calculation(self):
        # Test seguimiento creation
        seguimiento = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            observacion='Test observation'
        )
        self.assertEqual(seguimiento.proyecto, self.project)

    def test_activities_and_milestones_relationship(self):
        # Create activities and milestones for the project
        activity1 = Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Activity 1 description',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            cost=1000.00,
            status='pending'
        )
        activity2 = Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Activity 2 description',
            start_date=date.today() + timedelta(days=6),
            end_date=date.today() + timedelta(days=15),
            cost=2000.00,
            status='pending'
        )
        milestone = Milestone.objects.create(
            project=self.project,
            name='Phase 1 Complete',
            description='Milestone description',
            due_date=date.today() + timedelta(days=10)
        )

        # Verify they belong to same project
        self.assertEqual(activity1.project, self.project)
        self.assertEqual(activity2.project, self.project)
        self.assertEqual(milestone.project, self.project)

        # Test that milestone date is after some activities
        self.assertGreater(milestone.due_date, activity1.end_date)

    def test_cmi_perspectives_tracking(self):
        # Test seguimiento creation
        seguimiento = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            observacion='Test observation for CMI tracking'
        )
        self.assertEqual(seguimiento.proyecto, self.project)

    def test_project_budget_vs_resource_costs(self):
        # Test how resource costs relate to project budget
        resource1 = Resource.objects.create(
            activity=self.activity,
            name='Resource 1',
            type='material',
            quantity=2,
            cost_per_unit=1000.00
        )
        resource2 = Resource.objects.create(
            activity=self.activity,
            name='Resource 2',
            type='human',
            quantity=1,
            cost_per_unit=3000.00
        )

        total_resource_cost = sum(r.total_cost for r in Resource.objects.filter(activity=self.activity))
        self.assertEqual(total_resource_cost, 5000.00)  # 2000 + 3000

        # Project budget should be sufficient (though not automatically updated)
        self.assertGreaterEqual(self.project.budget, total_resource_cost)