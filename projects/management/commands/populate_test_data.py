from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from projects.models import Project, Activity, Milestone, UserProfile, ActaConstitucion
from stakeholders.models import Stakeholder
from resources.models import Resource
from risks.models import Risk
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Populate the database with test data'

    def handle(self, *args, **options):
        # Create test users
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
        )
        if created:
            user.set_password('password123')
            user.save()
            UserProfile.objects.get_or_create(user=user, defaults={'role': 'tecnico_proyectos'})
            self.stdout.write(self.style.SUCCESS('Created test user'))

        jefe, created = User.objects.get_or_create(
            username='jefe',
            defaults={'email': 'jefe@example.com', 'first_name': 'Jefe', 'last_name': 'Departamental'}
        )
        if created:
            jefe.set_password('password123')
            jefe.save()
            UserProfile.objects.get_or_create(user=jefe, defaults={'role': 'jefe_departamental'})
            self.stdout.write(self.style.SUCCESS('Created jefe user'))

        # Create test project
        project, created = Project.objects.get_or_create(
            name='Proyecto de Prueba CMI',
            defaults={
                'description': 'Un proyecto de prueba para demostrar las funcionalidades del sistema.',
                'start_date': date.today(),
                'end_date': date.today() + timedelta(days=90),
                'status': 'in_progress',
                'created_by': user
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created test project'))

        # Create acta constitucion
        acta, created = ActaConstitucion.objects.get_or_create(
            proyecto=project,
            defaults={
                'alcance': 'Desarrollo de un sistema de gestión de proyectos completo con módulos para actividades, hitos, stakeholders, recursos y reportes.',
                'entregables': 'Sistema web funcional, documentación técnica, manual de usuario, base de datos poblada con datos de prueba.',
                'justificacion': 'Mejora la eficiencia en la gestión de proyectos del GAD Célica, permitiendo un mejor control y seguimiento.',
                'objetivos': 'Implementar un sistema que permita gestionar proyectos de manera integral, con reportes y métricas para toma de decisiones.'
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created acta constitucion'))

        # Create activities
        activities_data = [
            {'name': 'Análisis de Requisitos', 'status': 'completed', 'cost': 5000.00, 'days': 10},
            {'name': 'Diseño del Sistema', 'status': 'completed', 'cost': 8000.00, 'days': 15},
            {'name': 'Desarrollo Frontend', 'status': 'in_progress', 'cost': 15000.00, 'days': 30},
            {'name': 'Desarrollo Backend', 'status': 'in_progress', 'cost': 20000.00, 'days': 35},
            {'name': 'Pruebas Unitarias', 'status': 'pending', 'cost': 3000.00, 'days': 7},
            {'name': 'Pruebas de Integración', 'status': 'pending', 'cost': 4000.00, 'days': 10},
            {'name': 'Despliegue', 'status': 'pending', 'cost': 2000.00, 'days': 5},
        ]

        activities = []
        start_date = project.start_date
        for i, act_data in enumerate(activities_data):
            act_start = start_date + timedelta(days=sum(a['days'] for a in activities_data[:i]))
            act_end = act_start + timedelta(days=act_data['days'])
            activity, created = Activity.objects.get_or_create(
                name=act_data['name'],
                project=project,
                defaults={
                    'description': f'Descripción de {act_data["name"]}',
                    'start_date': act_start,
                    'end_date': act_end,
                    'status': act_data['status'],
                    'cost': act_data['cost']
                }
            )
            activities.append(activity)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created activity: {act_data["name"]}'))

        # Create milestones
        milestones_data = [
            {'name': 'Inicio del Proyecto', 'days': 0},
            {'name': 'Finalización Análisis', 'days': 10},
            {'name': 'Finalización Diseño', 'days': 25},
            {'name': 'Entrega Primera Versión', 'days': 60},
            {'name': 'Finalización Proyecto', 'days': 90},
        ]

        for ms_data in milestones_data:
            ms_date = project.start_date + timedelta(days=ms_data['days'])
            milestone, created = Milestone.objects.get_or_create(
                name=ms_data['name'],
                project=project,
                defaults={
                    'description': f'Hito: {ms_data["name"]}',
                    'due_date': ms_date
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created milestone: {ms_data["name"]}'))

        # Create stakeholders
        stakeholders_data = [
            {'name': 'Juan Pérez', 'role': 'manager', 'contact_info': 'juan@example.com'},
            {'name': 'María García', 'role': 'team_member', 'contact_info': 'maria@example.com'},
            {'name': 'Carlos López', 'role': 'client', 'contact_info': 'carlos@example.com'},
        ]

        for st_data in stakeholders_data:
            stakeholder, created = Stakeholder.objects.get_or_create(
                name=st_data['name'],
                defaults={
                    'role': st_data['role'],
                    'contact_info': st_data['contact_info']
                }
            )
            stakeholder.projects.add(project)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created stakeholder: {st_data["name"]}'))

        # Create resources
        resources_data = [
            {'name': 'Desarrollador Senior', 'type': 'human', 'cost_per_unit': 50.00, 'quantity': 2, 'activity': activities[2]},  # Desarrollo Frontend
            {'name': 'Servidor AWS', 'type': 'material', 'cost_per_unit': 100.00, 'quantity': 1, 'activity': activities[3]},  # Desarrollo Backend
            {'name': 'Licencia Software', 'type': 'material', 'cost_per_unit': 500.00, 'quantity': 1, 'activity': None},
        ]

        for res_data in resources_data:
            resource, created = Resource.objects.get_or_create(
                name=res_data['name'],
                activity=res_data['activity'],
                defaults={
                    'type': res_data['type'],
                    'cost_per_unit': res_data['cost_per_unit'],
                    'quantity': res_data['quantity']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created resource: {res_data["name"]}'))

        # Create risks
        risks_data = [
            {'description': 'Retraso en entregas de terceros', 'probability': 'medium', 'impact': 'high', 'mitigation_plan': 'Monitoreo constante', 'status': 'identified'},
            {'description': 'Cambios en requisitos', 'probability': 'high', 'impact': 'medium', 'mitigation_plan': 'Reuniones semanales', 'status': 'identified'},
            {'description': 'Falta de personal', 'probability': 'low', 'impact': 'high', 'mitigation_plan': 'Plan de contingencia', 'status': 'mitigated'},
        ]

        for risk_data in risks_data:
            risk, created = Risk.objects.get_or_create(
                description=risk_data['description'],
                project=project,
                defaults={
                    'probability': risk_data['probability'],
                    'impact': risk_data['impact'],
                    'mitigation_plan': risk_data['mitigation_plan'],
                    'status': risk_data['status']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created risk: {risk_data["description"][:20]}...'))

        self.stdout.write(self.style.SUCCESS('Test data populated successfully'))