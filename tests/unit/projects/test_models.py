from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from projects.models import (
    Project, Activity, Milestone, Persona, UserProfile, Seguimiento,
    Cronograma, Presupuesto, Alcance, Comunicacion, AutoCertificacion
)

class TestPersona(TestCase):
    def test_persona_creation(self):
        persona = Persona.objects.create(
            nombre='John',
            apellido='Doe',
            email='john@example.com',
            telefono='123456789'
        )
        self.assertEqual(str(persona), 'John Doe')
        self.assertEqual(persona.email, 'john@example.com')

class TestUserProfile(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')

    def test_userprofile_creation(self):
        profile, created = UserProfile.objects.get_or_create(user=self.user, defaults={'role': 'tecnico_proyectos'})
        self.assertEqual(str(profile), 'testuser - Técnico de Proyectos')
        self.assertEqual(profile.role, 'tecnico_proyectos')

class TestProject(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')

    def test_project_creation(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(str(project), 'Test Project')
        self.assertEqual(project.status, 'planning')  # default

    def test_project_relationships(self):
        project = Project.objects.create(
            name='Test Project',
            description='Test Description',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )
        activity = Activity.objects.create(
            project=project,
            name='Test Activity',
            description='Desc',
            start_date=date.today(),
            end_date=date.today()
        )
        self.assertIn(activity, project.activity_set.all())

class TestActivity(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_activity_creation(self):
        activity = Activity.objects.create(
            project=self.project,
            name='Test Activity',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            status='pending',
            cost=100.00,
            time_estimate=10
        )
        self.assertEqual(activity.name, 'Test Activity')
        self.assertEqual(str(activity), 'Test Activity - Test Project')
        self.assertEqual(activity.status, 'pending')

class TestMilestone(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_milestone_creation(self):
        milestone = Milestone.objects.create(
            project=self.project,
            name='Test Milestone',
            description='Desc',
            due_date=date.today(),
            completed=False
        )
        self.assertEqual(milestone.name, 'Test Milestone')
        self.assertEqual(str(milestone), 'Test Milestone - Test Project')
        self.assertFalse(milestone.completed)

class TestSeguimiento(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=10),  # Extend project end date
            created_by=self.user
        )

    def test_seguimiento_creation_and_save(self):
        # Create some activities within project date range
        Activity.objects.create(
            project=self.project,
            name='Activity 1',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            status='completed',
            cost=100.00
        )
        Activity.objects.create(
            project=self.project,
            name='Activity 2',
            description='Desc',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            status='pending',
            cost=200.00
        )
        seguimiento = Seguimiento.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            observacion='Test observation'
        )
        # Check metrics: PV = 100 (only completed), EV = 100, AC = 100, CPI = 1.0, SPI = 1.0
        self.assertEqual(seguimiento.pv, 100.00)
        self.assertEqual(seguimiento.ev, 100.00)
        self.assertEqual(seguimiento.ac, 100.00)
        self.assertEqual(seguimiento.cpi, 1.00)
        self.assertEqual(seguimiento.spi, 1.00)

class TestCronograma(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
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

    def test_cronograma_creation(self):
        cronograma = Cronograma.objects.create(
            proyecto=self.project,
            actividad=self.activity,
            fecha_inicio=date.today(),
            fecha_fin=date.today()
        )
        self.assertEqual(cronograma.proyecto, self.project)
        self.assertEqual(cronograma.actividad, self.activity)

class TestPresupuesto(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_presupuesto_creation(self):
        presupuesto = Presupuesto.objects.create(
            proyecto=self.project,
            monto_total=1000.00,
            descripcion='Test Budget'
        )
        self.assertEqual(presupuesto.monto_total, 1000.00)

class TestAlcance(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_alcance_creation(self):
        alcance = Alcance.objects.create(
            proyecto=self.project,
            descripcion='Test Scope',
            objetivos='Objectives'
        )
        self.assertEqual(alcance.descripcion, 'Test Scope')

class TestComunicacion(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )
        from stakeholders.models import Stakeholder
        self.stakeholder = Stakeholder.objects.create(
            name='Test Stakeholder',
            email='stake@example.com',
            role='client'
        )

    def test_comunicacion_creation(self):
        comunicacion = Comunicacion.objects.create(
            proyecto=self.project,
            interesado=self.stakeholder,
            mensaje='Test Message',
            tipo='email'
        )
        self.assertEqual(comunicacion.mensaje, 'Test Message')

class TestAutoCertificacion(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.project = Project.objects.create(
            name='Test Project',
            description='Desc',
            start_date=date.today(),
            end_date=date.today(),
            created_by=self.user
        )

    def test_autocertificacion_creation(self):
        autocert = AutoCertificacion.objects.create(
            proyecto=self.project,
            fecha=date.today(),
            descripcion='Test Cert',
            aprobado=True
        )
        self.assertTrue(autocert.aprobado)