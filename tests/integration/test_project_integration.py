from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from projects.models import Project, Milestone, Activity, Seguimiento, UserProfile, ActivityAssignment
from stakeholders.models import Stakeholder
from resources.models import Resource
from risks.models import Risk
from datetime import date, timedelta
from decimal import Decimal


class ProjectIntegrationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='pass')
        self.user2 = User.objects.create_user(username='user2', password='pass')
        self.user1.userprofile.role = 'gestor_proyectos'
        self.user1.userprofile.save()
        self.user2.userprofile.role = 'tecnico_proyectos'
        self.user2.userprofile.save()

        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
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

        # Add activities first (resources are linked to activities)
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

        # Add resources (linked to activity, not project)
        resource = Resource.objects.create(
            activity=activity,
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
            observacion='Test seguimiento observation'
        )

        # Verify relationships
        self.assertIn(stakeholder, self.project.stakeholders.all())
        self.assertEqual(resource.activity, activity)
        self.assertEqual(risk.project, self.project)
        self.assertEqual(activity.project, self.project)
        self.assertEqual(milestone.project, self.project)
        self.assertEqual(seguimiento.proyecto, self.project)

        # Verify calculated fields
        self.assertEqual(resource.total_cost, 1000.00)  # 10 * 100

        # Verify project has all components
        self.assertTrue(self.project.stakeholders.exists())
        self.assertTrue(Risk.objects.filter(project=self.project).exists())
        self.assertTrue(Activity.objects.filter(project=self.project).exists())
        self.assertTrue(Milestone.objects.filter(project=self.project).exists())
        self.assertTrue(Seguimiento.objects.filter(proyecto=self.project).exists())


class CMITrafficLightTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cmi_user', password='pass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        
        self.project = Project.objects.create(
            name='CMI Test Project',
            description='Test project for CMI',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            budget=Decimal('50000.00'),
            created_by=self.user
        )

    def test_traffic_light_no_seguimiento(self):
        self.assertEqual(self.project.get_traffic_light_status(), 'gray')

    def test_traffic_light_green(self):
        Activity.objects.create(
            project=self.project,
            name='Completed Activity 1',
            description='Good progress',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='completed',
            cost=Decimal('5000.00')
        )
        Activity.objects.create(
            project=self.project,
            name='Completed Activity 2',
            description='Good progress',
            start_date=date.today() + timedelta(days=10),
            end_date=date.today() + timedelta(days=20),
            status='completed',
            cost=Decimal('5000.00')
        )
        seguimiento = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today() + timedelta(days=25),
            observacion='Good performance'
        )
        self.assertEqual(self.project.get_traffic_light_status(), 'green')

    def test_traffic_light_red(self):
        Activity.objects.create(
            project=self.project,
            name='Incomplete Activity',
            description='Behind schedule',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='in_progress',
            cost=Decimal('10000.00')
        )
        Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today() + timedelta(days=25),
            observacion='Behind schedule'
        )
        self.assertEqual(self.project.get_traffic_light_status(), 'red')


class ActivityPredecessorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pred_user', password='pass')
        self.project = Project.objects.create(
            name='Predecessor Test',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            created_by=self.user
        )

    def test_predecessor_dependency(self):
        act1 = Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='First',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            cost=Decimal('500.00')
        )
        act2 = Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Second',
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            predecessor=act1,
            cost=Decimal('300.00')
        )
        self.assertEqual(act2.predecessor, act1)
        self.assertIn(act2, act1.successors.all())

    def test_no_circular_dependency(self):
        act1 = Activity.objects.create(
            project=self.project,
            name='Act 1',
            description='First',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )
        act2 = Activity.objects.create(
            project=self.project,
            name='Act 2',
            description='Second',
            start_date=date.today() + timedelta(days=5),
            end_date=date.today() + timedelta(days=10),
            predecessor=act1
        )
        act1.predecessor = act2
        with self.assertRaises(ValidationError):
            act1.full_clean()


class ActivityAssignmentTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='assign_user', password='pass')
        self.project = Project.objects.create(
            name='Assignment Test',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            budget=Decimal('10000.00'),
            created_by=self.user
        )
        self.activity = Activity.objects.create(
            project=self.project,
            name='Test Activity',
            description='Testing assignments',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5)
        )

    def test_multiple_assignments(self):
        user2 = User.objects.create_user(username='assign_user2', password='pass')
        ActivityAssignment.objects.create(
            activity=self.activity,
            user=self.user,
            role='responsable',
            hours_assigned=20
        )
        ActivityAssignment.objects.create(
            activity=self.activity,
            user=user2,
            role='colaborador',
            hours_assigned=10
        )
        self.assertEqual(self.activity.assignments.count(), 2)

    def test_unique_assignment(self):
        ActivityAssignment.objects.create(
            activity=self.activity,
            user=self.user,
            role='responsable'
        )
        with self.assertRaises(Exception):
            ActivityAssignment.objects.create(
                activity=self.activity,
                user=self.user,
                role='colaborador'
            )


class BudgetCalculationsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='budget_user', password='pass')
        self.project = Project.objects.create(
            name='Budget Test',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            budget=Decimal('20000.00'),
            created_by=self.user
        )

    def test_activity_cost_calculation(self):
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('5000.00')
        )
        Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('3000.00')
        )
        self.assertEqual(self.project.total_activities_cost, Decimal('8000.00'))

    def test_resource_cost_calculation(self):
        activity = Activity.objects.create(
            project=self.project,
            name='Activity with Resources',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10)
        )
        Resource.objects.create(
            activity=activity,
            name='Resource 1',
            type='material',
            quantity=10,
            cost_per_unit=Decimal('100.00')
        )
        Resource.objects.create(
            activity=activity,
            name='Resource 2',
            type='labor',
            quantity=5,
            cost_per_unit=Decimal('200.00')
        )
        self.assertEqual(self.project.total_resources_cost, Decimal('2000.00'))

    def test_budget_utilization(self):
        """Utilización usa costo REAL (actual_cost), no planificado."""
        Activity.objects.create(
            project=self.project,
            name='Activity',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('10000.00'),
            actual_cost=Decimal('10000.00'),
        )
        self.assertEqual(self.project.budget_utilization_percentage, Decimal('50.0'))

    def test_budget_utilization_zero_when_no_actual_cost(self):
        """Sin costos reales registrados, utilización = 0%."""
        Activity.objects.create(
            project=self.project,
            name='Activity',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('10000.00'),
        )
        self.assertEqual(self.project.budget_utilization_percentage, 0)

    def test_budget_utilization_with_partial_actual(self):
        """Costo real parcial versus planificado."""
        Activity.objects.create(
            project=self.project,
            name='Activity',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('10000.00'),
            actual_cost=Decimal('5000.00'),
        )
        self.assertEqual(self.project.budget_utilization_percentage, Decimal('25.0'))

    def test_budget_variance(self):
        """Desviación de presupuesto: budget - costo planificado."""
        Activity.objects.create(
            project=self.project,
            name='Activity',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('15000.00')
        )
        self.assertEqual(self.project.budget_variance, Decimal('5000.00'))

    def test_planned_vs_actual_variance(self):
        """Desviación de ejecución: planificado - real."""
        Activity.objects.create(
            project=self.project,
            name='Activity',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('10000.00'),
            actual_cost=Decimal('8000.00'),
        )
        self.assertEqual(self.project.planned_vs_actual_variance, Decimal('2000.00'))

    def test_total_actual_cost_sums_actual_cost(self):
        """total_actual_cost suma actual_cost (NO cost planificado)."""
        Activity.objects.create(
            project=self.project,
            name='A1',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('5000.00'),
            actual_cost=Decimal('3000.00'),
        )
        Activity.objects.create(
            project=self.project,
            name='A2',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            cost=Decimal('5000.00'),
            actual_cost=Decimal('4000.00'),
        )
        self.assertEqual(self.project.total_actual_cost, Decimal('7000.00'))
        self.assertEqual(self.project.total_planned_cost, Decimal('10000.00'))


class MilestonePhaseGateTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='milestone_user', password='pass')
        self.project = Project.objects.create(
            name='Milestone Test',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=90),
            budget=Decimal('50000.00'),
            created_by=self.user
        )

    def test_milestone_phases(self):
        phases = ['initiation', 'planning', 'execution', 'monitoring', 'closure']
        for i, phase in enumerate(phases):
            Milestone.objects.create(
                project=self.project,
                name=f'{phase.capitalize()} Gate',
                description=f'{phase.capitalize()} phase completion',
                due_date=date.today() + timedelta(days=(i + 1) * 15),
                phase=phase,
                is_phase_gate=True
            )
        self.assertEqual(self.project.milestone_set.count(), 5)

    def test_milestone_completion_check(self):
        activity1 = Activity.objects.create(
            project=self.project,
            name='Task 1',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='completed'
        )
        activity2 = Activity.objects.create(
            project=self.project,
            name='Task 2',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='in_progress'
        )
        milestone = Milestone.objects.create(
            project=self.project,
            name='Test Milestone',
            description='Test',
            due_date=date.today() + timedelta(days=10),
            phase='execution'
        )
        milestone.activities.add(activity1, activity2)
        self.assertFalse(milestone.check_completion())
        
        activity2.status = 'completed'
        activity2.save()
        self.assertTrue(milestone.check_completion())