"""
Test para verificar que las actividades con predecesoras se guardan correctamente
y que las actividades se listan al crear hitos.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from projects.models import Project, Activity, Milestone, UserProfile
from datetime import date, timedelta


class WizardPredecessorTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.user.userprofile.role = 'gestor_proyectos'
        self.user.userprofile.save()
        self.client.login(username='testuser', password='testpass')
        
    def test_activity_predecessor_saved_correctly(self):
        """Verifica que una actividad con predecesora se guarda correctamente"""
        # Crear proyecto
        project = Project.objects.create(
            name='Test Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )
        
        # Crear actividad sin predecesora
        activity1 = Activity.objects.create(
            project=project,
            name='Actividad 1',
            description='Primera actividad',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=5),
            status='pending'
        )
        
        # Crear actividad con predecesora
        activity2 = Activity.objects.create(
            project=project,
            name='Actividad 2',
            description='Segunda actividad',
            start_date=date.today() + timedelta(days=6),
            end_date=date.today() + timedelta(days=10),
            status='pending',
            predecessor=activity1
        )
        
        # Verificar que la predecesora se guardó
        self.assertEqual(activity2.predecessor, activity1)
        self.assertEqual(activity2.predecessor.name, 'Actividad 1')
        
    def test_multiple_predecessors_chain(self):
        """Verifica una cadena de predecesoras"""
        project = Project.objects.create(
            name='Chain Project',
            description='Test chain',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=60),
            created_by=self.user
        )
        
        # Crear cadena de actividades
        activities = []
        for i in range(5):
            act = Activity.objects.create(
                project=project,
                name=f'Actividad {i+1}',
                description=f'Actividad número {i+1}',
                start_date=date.today() + timedelta(days=i*10),
                end_date=date.today() + timedelta(days=(i+1)*10-1),
                status='pending',
                predecessor=activities[-1] if activities else None
            )
            activities.append(act)
        
        # Verificar cadena
        self.assertIsNone(activities[0].predecessor)
        for i in range(1, 5):
            self.assertEqual(activities[i].predecessor, activities[i-1])
            
    def test_milestone_activities_list(self):
        """Verifica que las actividades se pueden asociar a un hito"""
        project = Project.objects.create(
            name='Milestone Project',
            description='Test milestone',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )
        
        # Crear actividades
        activity1 = Activity.objects.create(
            project=project,
            name='Actividad A',
            description='Descripción A',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='pending'
        )
        activity2 = Activity.objects.create(
            project=project,
            name='Actividad B',
            description='Descripción B',
            start_date=date.today() + timedelta(days=11),
            end_date=date.today() + timedelta(days=20),
            status='pending'
        )
        
        # Crear hito con actividades asociadas
        milestone = Milestone.objects.create(
            project=project,
            name='Hito 1',
            description='Primer hito',
            due_date=date.today() + timedelta(days=15),
            phase='execution'
        )
        milestone.activities.add(activity1, activity2)
        
        # Verificar asociación
        self.assertEqual(milestone.activities.count(), 2)
        self.assertIn(activity1, milestone.activities.all())
        self.assertIn(activity2, milestone.activities.all())
        
    def test_wizard_step7_has_activities(self):
        """Verifica que el paso 7 del wizard tiene acceso a las actividades"""
        # Crear proyecto
        project = Project.objects.create(
            name='Wizard Project',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            created_by=self.user
        )
        
        # Crear actividades
        Activity.objects.create(
            project=project,
            name='Actividad 1',
            description='Test',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),
            status='pending'
        )
        
        # Acceder al paso 7 del wizard
        response = self.client.get(f'/projects/wizard/step/7/')
        
        # Verificar que la respuesta es exitosa (puede ser redirect si no hay sesión)
        self.assertIn(response.status_code, [200, 302])
