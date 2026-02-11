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

    def test_resource_cost_calculation(self):
        # Test that resource total_cost is calculated correctly
        resource = Resource.objects.create(
            project=self.project,
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
        # Test progreso calculation in Seguimiento
        seguimiento = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            perspectiva='financiera',
            valor_actual=2500.00,
            valor_objetivo=10000.00
        )
        self.assertEqual(seguimiento.progreso, 25.00)

        # Update values and check
        seguimiento.valor_actual = 5000.00
        seguimiento.save()
        seguimiento.refresh_from_db()
        self.assertEqual(seguimiento.progreso, 50.00)

        # Test division by zero
        seguimiento.valor_objetivo = 0
        seguimiento.save()
        seguimiento.refresh_from_db()
        self.assertEqual(seguimiento.progreso, 0)

    def test_activities_and_milestones_relationship(self):
        # Create activities and milestones for the project
        activity1 = Activity.objects.create(
            project=self.project,
            name='Activity 1',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            cost=1000.00
        )
        activity2 = Activity.objects.create(
            project=self.project,
            name='Activity 2',
            start_date=date.today() + timedelta(days=6),
            end_date=date.today() + timedelta(days=15),
            cost=2000.00
        )
        milestone = Milestone.objects.create(
            project=self.project,
            name='Phase 1 Complete',
            due_date=date.today() + timedelta(days=10)
        )

        # Verify they belong to same project
        self.assertEqual(activity1.project, self.project)
        self.assertEqual(activity2.project, self.project)
        self.assertEqual(milestone.project, self.project)

        # Test that milestone date is after some activities
        self.assertGreater(milestone.due_date, activity1.end_date)

    def test_cmi_perspectives_tracking(self):
        # Test seguimiento across different CMI perspectives
        perspectivas = ['financiera', 'cliente', 'procesos_internos', 'aprendizaje_crecimiento']
        seguimientos = []
        for persp in perspectivas:
            seg = Seguimiento.objects.create(
                proyecto=self.project,
                fecha=date.today(),
                perspectiva=persp,
                indicador=f'Indicador {persp}',
                valor_actual=50.00,
                valor_objetivo=100.00
            )
            seguimientos.append(seg)

        # Verify all perspectives are tracked
        tracked_perspectivas = [s.perspectiva for s in Seguimiento.objects.filter(proyecto=self.project)]
        self.assertEqual(set(tracked_perspectivas), set(perspectivas))

        # Verify progress for each
        for seg in seguimientos:
            self.assertEqual(seg.progreso, 50.00)

    def test_project_budget_vs_resource_costs(self):
        # Test how resource costs relate to project budget
        resource1 = Resource.objects.create(
            project=self.project,
            name='Resource 1',
            type='material',
            quantity=2,
            cost_per_unit=1000.00
        )
        resource2 = Resource.objects.create(
            project=self.project,
            name='Resource 2',
            type='human',
            quantity=1,
            cost_per_unit=3000.00
        )

        total_resource_cost = sum(r.total_cost for r in Resource.objects.filter(project=self.project))
        self.assertEqual(total_resource_cost, 5000.00)  # 2000 + 3000

        # Project budget should be sufficient (though not automatically updated)
        self.assertGreaterEqual(self.project.budget, total_resource_cost)